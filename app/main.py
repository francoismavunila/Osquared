from fastapi import FastAPI
from pydantic import BaseSettings
from fastapi_jwt_auth import AuthJWT
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth
import os

# App Initialization
app = FastAPI()

# CORS Settings
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Settings class
class Settings(BaseSettings):
    authjwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your_secret_key")
    
    class Config:
        env_file = ".env"

# Configure FastAPI JWT Auth
@AuthJWT.load_config
def get_config():
    return Settings()

# Include Routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])

# Root Route
@app.get("/")
def read_root():
    return {"message": "Welcome to the Child User Management API"}
