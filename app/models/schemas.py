from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ActivityLevelEnum(str, Enum):
    sedentary = "sedentary"
    lightly_active = "lightly_active"
    moderately_active = "moderately_active"
    very_active = "very_active"
    extremely_active = "extremely_active"

class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"
    other = "Other"

class GoalEnum(str, Enum):
    fat_loss = "Fat loss"
    muscle_build = "Muscle build"
    stay_active = "Stay active"

# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: int
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Profile Schemas
class UserProfileCreate(BaseModel):
    height: float
    weight: float
    age: int
    gender: GenderEnum
    activity_level: ActivityLevelEnum

class UserProfile(BaseModel):
    id: int
    user_id: int
    height: float
    weight: float
    age: int
    gender: str
    activity_level: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Goals Schemas
class UserGoalsCreate(BaseModel):
    goal_type: GoalEnum
    target_weight: float
    target_days: int
    user_notes: Optional[str] = None

class UserGoals(BaseModel):
    id: int
    user_id: int
    goal_type: str
    target_weight: float
    target_days: int
    user_notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Plan Generation Schemas
class GeneratePlansRequest(BaseModel):
    user_id: int

class NutritionPlanResponse(BaseModel):
    id: int
    user_id: int
    plan_data: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True

class WorkoutPlanResponse(BaseModel):
    id: int
    user_id: int
    plan_data: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Chat Schemas
class ChatMessage(BaseModel):
    user_id: int
    message: str

class ChatResponse(BaseModel):
    response: str
    created_at: datetime

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None