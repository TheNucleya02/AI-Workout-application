from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.langraph_workflow import workflow_manager
from ...models import models, schemas
from ..dependencies import get_current_user

router = APIRouter()

@router.post("/generate-plans")
def generate_fitness_plans(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get user profile and goals
    profile = db.query(models.UserProfile).filter(
        models.UserProfile.user_id == current_user.id
    ).first()
    
    goals = db.query(models.UserGoals).filter(
        models.UserGoals.user_id == current_user.id
    ).first()
    
    if not profile or not goals:
        raise HTTPException(
            status_code=400,
            detail="User profile and goals must be set before generating plans"
        )
    
    # Prepare data for LangGraph workflow
    user_data = {
        "user_id": current_user.id,
        "height": profile.height,
        "weight": profile.weight,
        "age": profile.age,
        "gender": profile.gender,
        "activity_level": profile.activity_level,
        "goal_type": goals.goal_type,
        "target_weight": goals.target_weight,
        "target_days": goals.target_days,
        "user_notes": goals.user_notes,
        "nutrition_plan": None,
        "workout_plan": None,
        "chat_messages": [],
        "chat_query": None,
        "chat_response": None,
        "error_message": None
    }
    
    # Generate plans using LangGraph workflow
    result = workflow_manager.generate_plans(user_data)
    
    # Save nutrition plan
    nutrition_plan = models.NutritionPlan(
        user_id=current_user.id,
        plan_data=result["nutrition_plan"]
    )
    db.add(nutrition_plan)
    
    # Save workout plan
    workout_plan = models.WorkoutPlan(
        user_id=current_user.id,
        plan_data=result["workout_plan"]
    )
    db.add(workout_plan)
    
    db.commit()
    db.refresh(nutrition_plan)
    db.refresh(workout_plan)
    
    return {
        "nutrition_plan": nutrition_plan.plan_data,
        "workout_plan": workout_plan.plan_data
    }

@router.get("/plans")
def get_user_plans(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    nutrition_plan = db.query(models.NutritionPlan).filter(
        models.NutritionPlan.user_id == current_user.id
    ).order_by(models.NutritionPlan.created_at.desc()).first()
    
    workout_plan = db.query(models.WorkoutPlan).filter(
        models.WorkoutPlan.user_id == current_user.id
    ).order_by(models.WorkoutPlan.created_at.desc()).first()
    
    return {
        "nutrition_plan": nutrition_plan.plan_data if nutrition_plan else None,
        "workout_plan": workout_plan.plan_data if workout_plan else None
    }