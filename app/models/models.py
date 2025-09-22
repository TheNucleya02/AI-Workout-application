from sqlalchemy import Column, String, Integer, Float, Date, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

# 1. Users table
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    fitness_goals = relationship("FitnessGoal", back_populates="user")
    nutrition_goals = relationship("NutritionGoal", back_populates="user")
    nutrition_logs = relationship("NutritionLog", back_populates="user")

# 2. User Profile
class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    age = Column(Integer)
    gender = Column(String(20))
    height_cm = Column(Float)
    weight_kg = Column(Float)
    activity_level = Column(
        Enum('Moderately active', 'Slightly active', 'Extremely active', name='activity_level_enum'),
        nullable=False
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="profile")

# 3. Fitness Goals
class FitnessGoal(Base):
    __tablename__ = "fitness_goals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    goal_type = Column(
        Enum('Fat loss', 'Muscle gain', 'Stay active', name='goal_type_enum'),
        nullable=False
    ) 
    target_weight = Column(Float, nullable=True)
    target_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="fitness_goals")

# 4. Nutrition Goals
class NutritionGoal(Base):
    __tablename__ = "nutrition_goals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    calories_per_day = Column(Integer)
    protein_g = Column(Float)
    carbs_g = Column(Float)
    fats_g = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="nutrition_goals")
