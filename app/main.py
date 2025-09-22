from fastapi import FastAPI
import models, database
from routers import users

# Create DB tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="AI Fitness Planner")

# Register routers
app.include_router(users.router)