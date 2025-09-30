from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class UserProfileBase(BaseModel):
    age: int
    height_cm: float
    weight_kg: float
    gender: str
    activity_level: str
    goal_type: str
    target_weight: float
    target_days: int

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(BaseModel):
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    gender: Optional[str] = None
    activity_level: Optional[str] = None
    goal_type: Optional[str] = None
    target_weight: Optional[float] = None
    target_days: Optional[int] = None

class UserProfile(UserProfileBase):
    id: int
    user_id: int
    class Config:
        orm_mode = True
