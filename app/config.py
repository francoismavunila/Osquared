import os
from pydantic import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use Pydantic for settings
class Settings(BaseSettings):
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your_secret_key")

    class Config:
        env_file = ".env"

# Instantiate the settings
settings = Settings()
