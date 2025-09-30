from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import crud, schemas, auth, models
from .database import get_db, engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {'message' :" Root is Working Fine "}

@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = crud.create_user(db=db, user=user)
    return new_user

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_data = {"sub": user.username}
    access_token = auth.create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user

@app.get("/profile", response_model=schemas.UserProfile)
def get_profile(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    profile = crud.get_user_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@app.post("/profile", response_model=schemas.UserProfile)
def create_profile(profile_in: schemas.UserProfileCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if crud.get_user_profile(db, current_user.id):
        raise HTTPException(status_code=400, detail="Profile already exists")
    return crud.create_user_profile(db, profile_in, current_user.id)

@app.put("/profile", response_model=schemas.UserProfile)
def update_profile(profile_in: schemas.UserProfileUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    updated = crud.update_user_profile(db, profile_in, current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Profile not found")
    return updated

@app.delete("/profile", status_code=204)
def delete_profile(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    deleted = crud.delete_user_profile(db, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Profile not found")




