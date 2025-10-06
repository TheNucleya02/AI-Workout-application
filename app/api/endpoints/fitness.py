from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.langraph_workflow import workflow_manager
from ...models import models, schemas
from ...utils import helpers
from ..dependencies import get_current_user

router = APIRouter()

@router.post("/generate-nutrition-plan")
def generate_nutrition_plan(
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
            detail="User profile and goals must be set before generating a nutrition plan"
        )

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

    result_state = workflow_manager.generate_nutrition_plan(user_data)
    nutrition_plan_data = result_state.get("nutrition_plan", {})

    # If the model returned fallback text (non-JSON), try to extract JSON
    if "plan_text" in nutrition_plan_data:
        plan_text = nutrition_plan_data["plan_text"]
        plan_raw = plan_text.get("plan_data", {}).get("plan_raw", "")

        # Attempt to extract JSON from raw LLM output
        parsed_json, error = helpers.extract_json_from_plan_raw(plan_raw)

        if parsed_json:
            nutrition_json = parsed_json
        else:
            # Keep a record of the error and raw content
            nutrition_json = {"error": error, "raw_content": plan_raw}

    else:
        # Model already returned structured JSON
        nutrition_json = nutrition_plan_data


    nutrition_plan = models.NutritionPlan(
        user_id=current_user.id,
        plan_data=nutrition_json,
    )
    db.add(nutrition_plan)
    db.commit()
    db.refresh(nutrition_plan)

    return {
        "nutrition_plan": nutrition_json
    }

@router.post("/generate-workout-plan")
def generate_workout_plan(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate, parse, and store a structured workout plan."""
    
    # Fetch user info
    profile = db.query(models.UserProfile).filter(
        models.UserProfile.user_id == current_user.id
    ).first()
    goals = db.query(models.UserGoals).filter(
        models.UserGoals.user_id == current_user.id
    ).first()
    nutrition_plan = db.query(models.NutritionPlan).filter(
        models.NutritionPlan.user_id == current_user.id
    ).order_by(models.NutritionPlan.created_at.desc()).first()

    if not profile or not goals or not nutrition_plan:
        raise HTTPException(
            status_code=400,
            detail="User profile, goals, and nutrition plan must be set before generating a workout plan"
        )

    # Prepare state for LLM
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
        "nutrition_plan": nutrition_plan.plan_data,
        "workout_plan": None,
        "chat_messages": [],
        "chat_query": None,
        "chat_response": None,
        "error_message": None
    }

    # Generate workout plan via LLM
    result_state = workflow_manager.generate_workout_plan(user_data)
    workout_plan_data = result_state.get("workout_plan", {})

    # Handle unstructured response
    if "plan_text" in workout_plan_data:
        plan_text = workout_plan_data.get("plan_text", "")
        if isinstance(plan_text, dict):
            plan_raw = plan_text.get("plan_data", {}).get("plan_raw", "")
        else:
            plan_raw = plan_text

        parsed_json, error = helpers.extract_json_from_plan_raw(plan_raw)

        if parsed_json:
            workout_json = parsed_json
        else:
            workout_json = {"error": error, "raw_content": plan_raw}

    else:
        # Already structured JSON
        workout_json = workout_plan_data


    workout_plan = models.WorkoutPlan(
        user_id=current_user.id,
        plan_data=workout_json,
    )
    db.add(workout_plan)
    db.commit()
    db.refresh(workout_plan)

    return {
        "workout_plan": workout_json
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
        "nutrition_plan":  nutrition_plan if nutrition_plan else None,
        "workout_plan": workout_plan if workout_plan else None
    }