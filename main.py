from fastapi import FastAPI
from dotenv import load_dotenv
import os
from app.routes import user

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# register the user chat
app.include_router(user.router)