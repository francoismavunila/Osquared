from fastapi import APIRouter, HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from app.schemas.Exception import CustomError
from app.services.chatbot_service import handle_initial_message, generate_persona_response
from app.models.chat import ChatRequest
router = APIRouter()

@router.get("/initial-message/{persona}")
def initial_message(persona: str, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        print(current_user)
        message = handle_initial_message(current_user, persona)
        return {"message": message}
    except CustomError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token or token expired or invalid input")
    
@router.post("/chat")
def get_chat_response(request: ChatRequest):
    if not request.user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    response = generate_persona_response(request.user_message)
    return {"response": response}