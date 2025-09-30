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

def get_user_profile(db: Session, user_id: int):
    return db.query(models.UserProfile).filter_by(user_id=user_id).first()

def create_user_profile(db: Session, profile_in: schemas.UserProfileCreate, user_id: int):
    profile = models.UserProfile(**profile_in.model_dump(), user_id=user_id)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

def update_user_profile(db: Session, profile_in: schemas.UserProfileUpdate, user_id: int):
    profile = get_user_profile(db, user_id)
    if not profile:
        return None
    for k, v in profile_in.model_dump(exclude_unset=True).items():
        setattr(profile, k, v)
    db.commit()
    db.refresh(profile)
    return profile

def delete_user_profile(db: Session, user_id: int):
    profile = get_user_profile(db, user_id)
    if profile:
        db.delete(profile)
        db.commit()
    return profile




