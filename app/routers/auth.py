from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_jwt_auth import AuthJWT
from app.models.user import User
from app.schemas.user import UserResponse, TokenResponse
from app.utils.hash import hash_password, verify_password
from app.db import db

router = APIRouter()

# User Registration
@router.post("/register", response_model=UserResponse)
def register(user: User):
    existing_user = db["users"].find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = hash_password(user.password)
    db["users"].insert_one({"username": user.username, "password": hashed_password})

    return {"username": user.username}

# User Login
@router.post("/login", response_model=TokenResponse)
def login(user: User, Authorize: AuthJWT = Depends()):
    db_user = db["users"].find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    access_token = Authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}
