from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from ...core.database import get_db
from ...core.langraph_workflow import workflow_manager
from ...models import models, schemas
from ...utils import helpers
from ..dependencies import get_current_user

router = APIRouter()

@router.post("/chat", response_model=schemas.ChatResponse)
def chat_with_ai(
    message: schemas.ChatMessage,
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
    
    # Get latest plans
    nutrition_plan = db.query(models.NutritionPlan).filter(
        models.NutritionPlan.user_id == current_user.id
    ).order_by(models.NutritionPlan.created_at.desc()).first()
    
    workout_plan = db.query(models.WorkoutPlan).filter(
        models.WorkoutPlan.user_id == current_user.id
    ).order_by(models.WorkoutPlan.created_at.desc()).first()
    
    if not profile or not goals:
        raise HTTPException(
            status_code=400,
            detail="User profile and goals must be set before chatting"
        )
    
    # Prepare user data for chat
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
        "nutrition_plan": nutrition_plan.plan_data if nutrition_plan else None,
        "workout_plan": workout_plan.plan_data if workout_plan else None,
        "chat_messages": [],
        "chat_query": None,
        "chat_response": None,
        "error_message": None
    }
    
    # Get AI response
    response = workflow_manager.chat_with_AI(user_data, message.message)
    # Ensure response is JSON serializable
    try:
        # If response is a string, try to parse it as JSON
        if isinstance(response, str):
            response_json = json.loads(response)
        else:
            response_json = response
    except (json.JSONDecodeError, TypeError):
        # Handle non-JSON output gracefully
        response_json = {
            "error": "AI returned an unexpected response. Please try again later.",
            "raw_response": str(response)
        }

    chat_history = models.ChatHistory(
        user_id=current_user.id,
        message=message.message,
        response=json.dumps(response_json),  # Save as JSON string
    )
    db.add(chat_history)
    db.commit()
    db.refresh(chat_history)

    return schemas.ChatResponse(
        response=json.dumps(response_json),
        created_at=chat_history.created_at,  # type: ignore
    )   

@router.get("/chat/history")
def get_chat_history(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    history = db.query(models.ChatHistory).filter(
        models.ChatHistory.user_id == current_user.id
    ).order_by(models.ChatHistory.created_at.desc()).limit(limit).all()
    
    return [
        {
            "message": chat.message,
            "response": chat.formatted_output,
            "created_at": chat.created_at
        }
        for chat in history
    ]