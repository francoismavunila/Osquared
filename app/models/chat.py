from pydantic import BaseModel
from typing import List
from datetime import datetime

class ChatRequest(BaseModel):
    user_message: str
    

class Message(BaseModel):
    sender: str
    text: str
    message_id: str

class Conversation(BaseModel):
    conversation_id: str
    user_id: str
    persona: str
    messages: List[Message]
    created_at: datetime
