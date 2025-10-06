from typing import TypedDict, Optional, Dict, Any, List
from enum import Enum
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
import json
import os
from .config import settings

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    google_api_key=settings.GOOGLE_API_KEY
)

class FitnessAppState(TypedDict):
    # User Profile Information
    height: float
    weight: float
    age: int
    gender: str
    activity_level: str
    
    # User Goals
    goal_type: str
    target_weight: float
    target_days: int
    
    # User Notes
    user_notes: Optional[str]
    
    # Generated Plans
    nutrition_plan: Optional[Dict[str, Any]]
    workout_plan: Optional[Dict[str, Any]]
    
    # Chat Context
    chat_messages: List[Dict[str, str]]
    chat_query: Optional[str]
    chat_response: Optional[str]
    
    # Error Handling
    error_message: Optional[str]

def calculate_bmr(height: float, weight: float, age: int, gender: str) -> float:
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor equation"""
    if gender.lower() == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

def calculate_daily_calories(bmr: float, activity_level: str) -> float:
    """Calculate daily calorie needs based on activity level"""
    multipliers = {
        "sedentary": 1.2,
        "lightly_active": 1.375,
        "moderately_active": 1.55,
        "very_active": 1.725,
        "extremely_active": 1.9
    }
    return bmr * multipliers.get(activity_level.lower(), 1.2)

def adjust_calories_for_goal(daily_calories: float, goal_type: str, target_weight: float, current_weight: float, target_days: int) -> float:
    """Adjust calories based on user goals"""
    if goal_type == "Fat loss":
        if target_days == 0:
            raise ValueError("target_days cannot be zero.")
        
        weekly_loss = (current_weight - target_weight) / (target_days / 7)
        deficit = min(weekly_loss * 1000, 1000)  # Max 1000 cal deficit
        return daily_calories - deficit
    elif goal_type == "Muscle build":
        return daily_calories + 300  # Moderate surplus
    else:
        return daily_calories  # Maintenance

def generate_nutrition_plan(state: FitnessAppState) -> FitnessAppState:
    """Generate personalized nutrition plan using LLM"""
    
    # Calculate BMR and daily calorie needs
    bmr = calculate_bmr(state["height"], state["weight"], state["age"], state["gender"])
    daily_calories = calculate_daily_calories(bmr, state["activity_level"])
    
    # Adjust calories based on goal
    target_calories = adjust_calories_for_goal(
        daily_calories,
        state["goal_type"],
        state["target_weight"],
        state["weight"],
        state["target_days"]
    )
    
    # Nutrition prompt for LLM
    nutrition_prompt = f"""
    Create a detailed nutrition plan for a user with the following profile:
    - Age: {state['age']}, Gender: {state['gender']}
    - Height: {state['height']}cm, Weight: {state['weight']}kg
    - Activity Level: {state['activity_level']}
    - Goal: {state['goal_type']}, Target Weight: {state['target_weight']}kg in {state['target_days']} days
    - Target Daily Calories: {target_calories}
    - Additional Notes: {state['user_notes']}
    
    Provide the answer in valid JSON format with keys:
    - daily_calories
    - macros (protein, carbs, fats in grams)
    - meal_plan (detailed plan)
    - hydration
    - supplements
    """
    
    response = llm.invoke(nutrition_prompt)
    
    # Try parsing JSON if model returns structured
    try:
        response_text = str(response.content) if hasattr(response, "content") else str(response)
        nutrition_plan = json.loads(response_text)
    except Exception:
        # Fallback if model didn't give strict JSON
        nutrition_plan = {"plan_text": str(response)}
    
    state["nutrition_plan"] = nutrition_plan
    return state

def generate_workout_plan(state: FitnessAppState) -> FitnessAppState:
    """Generate personalized workout plan"""
    
    workout_prompt = f"""
    Create a detailed workout plan for a user with the following profile:
    - Age: {state['age']}, Gender: {state['gender']}
    - Height: {state['height']}cm, Weight: {state['weight']}kg
    - Activity Level: {state['activity_level']}
    - Goal: {state['goal_type']}, Target Weight: {state['target_weight']}kg in {state['target_days']} days
    - Nutrition Plan: {state['nutrition_plan']}
    - Additional Notes: {state['user_notes']}
    
    Provide:
    1. Weekly workout schedule
    2. Exercise types and intensity
    3. Progressive overload plan
    4. Recovery recommendations
    5. Alternative exercises for equipment limitations

    Provide the answer in valid JSON format with keys:
    - weekly_schedule
    - progression
    - recovery
    """
    
    response = llm.invoke(workout_prompt)
    
    # Try parsing JSON if model returns structured
    try:
        response_text = str(response.content) if hasattr(response, "content") else str(response)
        workout_plan = json.loads(response_text)
    except Exception:
        # Fallback if model didn't give strict JSON
        workout_plan = {"plan_text": str(response)}
    
    state["workout_plan"] = workout_plan
    return state

def handle_chat_query(state: FitnessAppState) -> FitnessAppState:
    """Handle general user queries in chat"""
    
    chat_prompt = f"""
    User context:
    - Profile: Age {state['age']}, {state['gender']}, {state['height']}cm, {state['weight']}kg
    - Activity Level: {state['activity_level']}
    - Goals: {state['goal_type']}, target {state['target_weight']}kg in {state['target_days']} days
    - User Notes: {state['user_notes']}
    - Current Nutrition Plan: {state['nutrition_plan']}
    - Current Workout Plan: {state['workout_plan']}
    
    User Question: {state['chat_query']}
    
    Provide a helpful, personalized response considering their profile and plans.
    """
    
    response = llm.invoke(chat_prompt)
    
    # Add to chat history
    if not state["chat_messages"]:
        state["chat_messages"] = []
    
    state["chat_messages"].append({
        "user": state["chat_query"] or "",
        "assistant": str(response)
    })
    
    state["chat_response"] = str(response)
    state["chat_query"] = None
    return state

class FitnessWorkflowManager:
    def __init__(self):
        self.memory = MemorySaver()
        self.workflow = self._create_workflow()
    
    def _create_workflow(self):
        """Create and configure the LangGraph workflow"""
        workflow = StateGraph(FitnessAppState)
        
        # Add nodes
        workflow.add_node("generate_nutrition_plan", generate_nutrition_plan)
        workflow.add_node("generate_workout_plan", generate_workout_plan)
        workflow.add_node("handle_chat_query", handle_chat_query)
        
        # Set entry point and edges
        workflow.add_edge(START, "generate_nutrition_plan")
        workflow.add_edge("generate_nutrition_plan", "generate_workout_plan")
        workflow.add_edge("generate_workout_plan", END)
        workflow.add_edge("handle_chat_query", END)
        
        return workflow.compile(checkpointer=self.memory)
    
    def generate_plans(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate nutrition and workout plans"""
        state = FitnessAppState(**user_data)
        config = RunnableConfig(configurable={"thread_id": f"user_{user_data.get('user_id', 'unknown')}"})
        
        result = self.workflow.invoke(state, config)
        return result
    
    def chat_with_ai(self, user_data: Dict[str, Any], query: str) -> str:
        """Handle chat queries"""
        state = FitnessAppState(**user_data)
        state["chat_query"] = query
        
        config = RunnableConfig(configurable={"thread_id": f"user_{user_data.get('user_id', 'unknown')}"})
        
        # Use only the chat node
        result = handle_chat_query(state)
        return result["chat_response"] or ""

# Global instance
workflow_manager = FitnessWorkflowManager()