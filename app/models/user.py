from pydantic import BaseModel, Field

class User(BaseModel):
    username: str
    password: str
