from sqlalchemy.orm import Session
from . import models, schemas, utils

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id:int):
    return db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=utils.hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not utils.verify_password(password, user.hashed_password):
        return None
    return user

def create_user_profile(user_profile: schemas.UserProfileCreate, db: Session):
    db_user_profile = models.UserProfile(
        age = user_profile.age,
        height_cm = user_profile.age,
        weight_kg = user_profile.age,
        gender = user_profile.age,
        activity_level = user_profile.age,
        goal_type = user_profile.age,
        target_weight = user_profile.age,
        target_days = user_profile.age
    )
    db.add(db_user_profile)
    db.commit()
    db.refresh(db_user_profile)
    return db_user_profile



