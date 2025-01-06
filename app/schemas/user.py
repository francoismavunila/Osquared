from pydantic import BaseModel

class UserResponse(BaseModel):
    username: str

    class Config:
        orm_mode = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
