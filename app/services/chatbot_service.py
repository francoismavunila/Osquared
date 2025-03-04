from datetime import datetime
import uuid
from fastapi import HTTPException
from openai import OpenAI
import os
from dotenv import load_dotenv
from app.schemas.chat import Evaluation
from app.db import db
from app.schemas.Exception import CustomError
from typing import List, Dict
from pydantic import BaseModel

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)
# Persona definition
personas = {
    "scammer": {
        "name": "Dave",
        "description": (
            "A manipulative individual who employs deceptive tactics to steal personal or sensitive information from children on social media. "
            "They create urgency, fear, or false opportunities to extract details like passwords, credit card numbers, location, scammer links, "
            "or confidential data. Known for impersonating trusted entities and sending fraudulent links or requests."
        ),
        "behavior": (
            "Uses alarming or enticing language, sends fake links, and requests sensitive information. "
            "Employs emotional manipulation, such as pretending to be a distressed relative or a credible official."
        ),
        "initial_message": (
            "Hello! This is an urgent message from your bank. We have detected suspicious activity on your account. "
            "Please click the link below to verify your identity and secure your account immediately: [fake-bank-link.com]"
        ),
        "goals": [
            "privacy",
            "password_security",
            "personal_info_sharing",
            "phishing_awareness",
            "link_verification",
            "emotional_manipulation",
            "scam_detection"
        ]
    },
    "bully": {
        "name": "JakeTheKing99",
        "description": (
            "An aggressive individual who targets children on social media to intimidate, humiliate, or emotionally hurt them. "
            "They use insults, threats, and harassment to cause distress, often targeting a child's appearance, abilities, or interests. "
            "Bullies thrive on making others feel inferior and powerless."
        ),
        "behavior": (
            "Sends mean comments, spreads rumors, makes personal attacks, and encourages others to exclude or mock the victim. "
            "Uses private messages or public posts to embarrass the target, often escalating to threats of violence or harm."
        ),
        "initial_message": (
            "Wow, I can't believe people actually hang out with you. You're such a loser. Maybe you should just stay offline — no one would even notice."
        ),
        "goals": [
            "self-esteem",
            "emotional_resilience",
            "conflict_response",
            "online_harassment",
            "block_and_report",
            "social_inclusion",
            "critical_thinking"
        ]
    },
    "family_friend": {
        "name": "Aunt Mary",
        "description": (
            "A well-meaning individual who cares about the child’s well-being and shares advice, stories, and encouragement. "
            "They maintain a supportive and respectful approach to communication, acting as a trusted confidant or mentor."
        ),
        "behavior": (
            "Uses positive, caring language to offer guidance, advice, or emotional support. "
            "They may share helpful resources, life lessons, or encouragement to motivate the child."
        ),
        "initial_message": (
            "Hey there! I hope you've been doing well. Remember, no matter how hard things get, you always have people who care about you. "
            "Keep your head up! Let me know if you need anything."
        ),
        "goals": [
            "mental_health",
            "self-awareness",
            "relationship_building",
            "empathy",
            "support_systems",
            "life_skills",
            "self-expression"
        ]
    }
}


def generate_conversation_id(user_name: str, persona: str) -> str:
    return f"user_{user_name}_persona_{persona}"

def get_initial_message(user_name, persona) -> str:
    if persona not in personas:
        raise CustomError("Persona not found")

    persona_data = personas[persona]
    persona_prompt = f"""
    You are {persona_data['name']}. {persona_data['description']} {persona_data['behavior']}

    Your task is to engage in a simulated conversation with a user to assess their responses in the following key areas: {', '.join(persona_data['goals'])}. 

    Each area represents an important skill or awareness that the user should demonstrate to stay safe and make informed decisions online. Your goal is to ensure that each of these areas is tested through natural conversation.

    Once you have sufficiently tested all the key areas, you must recognize that the session is complete. End the conversation by thanking the user for their time and providing a brief closing message that summarizes the importance of the areas covered. Be positive and encouraging in your closing statement.

    For example:
    - "Thank you for your time! We've covered some important areas to help you stay safe online, such as privacy, recognizing scams, and protecting personal information. Remember to stay cautious and keep your information secure!"
    - "Thanks for chatting with me! You did great in handling some tough scenarios. Keep practicing online safety, and don't forget to report anything suspicious!"

    Ensure the conversation feels natural and engaging. Do not prematurely end the session before all the key areas have been tested.
    """
    print(persona_prompt)
    messages = [
        {"role": "developer", "content": persona_prompt},
        {"role": "user", "content": f"generate the initial message to send to {user_name}"}
    ]

    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        message = completion.choices[0].message.content
        
        return completion.choices[0].message.content
    except Exception as e:
        raise CustomError(f"Error generating response from server llm: {str(e)}")
   

def handle_initial_message(user_name: str, persona: str) -> list:
    if persona not in personas:
        raise CustomError("Persona not found")
    conversation_id = generate_conversation_id(user_name, persona)
    print(conversation_id)
    
    # Check if the conversation already exists
    conversation = db["chats"].find_one({"conversation_id": conversation_id})
    
    if not conversation:
        # If no conversation, create a new one with an initial message
        print("no conv")
        initial_message = get_initial_message(user_name, persona)
        new_conversation = {
            "conversation_id": conversation_id,
            "user_id": user_name,
            "persona": persona,
            "messages": [{"role": "assistant", "content": initial_message, "message_id": str(uuid.uuid4())}],
            "created_at": datetime.utcnow()
        }
        db["chats"].insert_one(new_conversation)
        conversation = new_conversation
    
    return conversation["messages"]


# Generate persona response
def generate_persona_response(user_message, user_name, persona):
    if persona not in personas:
        raise CustomError("Persona not found")
    
    conversation_id = generate_conversation_id(user_name, persona)
    conversation = db["chats"].find_one({"conversation_id": conversation_id})
    
    if not conversation:
        raise CustomError("Conversation not found")
    persona_data = personas[persona]
    persona_prompt = f"""
    You are {persona_data['name']}. {persona_data['description']} {persona_data['behavior']}

    Your task is to engage in a simulated conversation with a user to assess their responses in the following key areas: {', '.join(persona_data['goals'])}. 

    Each area represents an important skill or awareness that the user should demonstrate to stay safe and make informed decisions online. Your goal is to ensure that each of these areas is tested through natural conversation.

    Once you have sufficiently tested all the key areas, you must recognize that the session is complete. End the conversation by thanking the user for their time and providing a brief closing message that summarizes the importance of the areas covered. Be positive and encouraging in your closing statement.

    For example:
    - "Thank you for your time! We've covered some important areas to help you stay safe online, such as privacy, recognizing scams, and protecting personal information. Remember to stay cautious and keep your information secure!"
    - "Thanks for chatting with me! You did great in handling some tough scenarios. Keep practicing online safety, and don't forget to report anything suspicious!"

    Ensure the conversation feels natural and engaging. Do not prematurely end the session before all the key areas have been tested.
    """
    # print(persona_prompt)
    history = conversation["messages"][-12:] if len(conversation["messages"]) >= 12 else conversation["messages"]
    messages = [{'role': entry['role'], 'content': entry['content']} for entry in history]
    messages.insert(0, {"role": "developer", "content": persona_prompt})
    messages.append({'role': 'user', 'content': user_message})

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        response_message = completion.choices[0].message.content
        print("usage one:", completion.usage)
        persona_last_message = conversation["messages"][-1]['content']
        score, feedback = evaluate_user_response(user_message, persona_last_message, persona_data['goals'])
        
        # Update the conversation with the new messages
        db["chats"].update_one(
            {"conversation_id": conversation_id},
            {"$push": {"messages": {"role": "user", "content": user_message, "message_id": str(uuid.uuid4())}}}
        )
        db["chats"].update_one(
            {"conversation_id": conversation_id},
            {"$push": {"messages": {"role": "assistant", "content": response_message, "message_id": str(uuid.uuid4())}}}
        )
        
        # Update user profile with new scores
        updated_scores = update_user_profile(user_name, score)
        
        return response_message, updated_scores, feedback
    except Exception as e:
        return f"Error generating response: {str(e)}"

class ScoreItem(BaseModel):
    goal: str
    score: int

def update_user_profile(user_name: str, new_scores: List[ScoreItem]) -> Dict[str, int]:
    user = db["users"].find_one({"username": user_name})
    if not user:
        raise CustomError("User not found")
    print(new_scores)
    updated_scores = user.get("scores", {})
    for score_item in new_scores:
        key = score_item.goal
        value = score_item.score
        if key in updated_scores:
            updated_scores[key] = (updated_scores[key] + value) // 2
        else:
            updated_scores[key] = value

    db["users"].update_one(
        {"username": user_name},
        {"$set": {"scores": updated_scores}}
    )
    
    return updated_scores
   
# Evaluate user response

def  evaluate_user_response(user_response, persona_response, persona_goals):
    print("here")
    if not isinstance(user_response, str) or not user_response.strip():
        raise ValueError("Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]")
    
    # Build dynamic scoring prompt based on persona's goals
    scoring_prompt = (
        f"Evaluate the following user (child) response to a message:\n\n"
        f"Persona's message: {persona_response}\n"
        f"User's response: {user_response}\n\n"
        f"Score the user's response on a scale of 1 to 10 for each of the following categories: {', '.join(persona_goals)}.\n"
        f"Provide feedback on how well the child handled each goal.\n"
        f"- provide examples of how best they should have responded incase the response was not appropriate?\n"
        f"Provide the score against the goal or goals that were tested as a json and a summary of the feedback."
        "format response to be like this {\"scores\": {\"privacy\": 80, \"passwords\": 70, "
            "\"personal_info\": 90}, \"feedback\": \"Great job! You demonstrated strong awareness of privacy risks by refusing to click on the suspicious link. Keep up the good work!\"}"
    )

    # Call the LLM to get the evaluation
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "developer", "content": "You are an educator providing responses in a cybersecurity simulation aimed at teaching children about online safety. Your responses should be educational, friendly, and easy to understand."},
                {"role": "user", "content": scoring_prompt}
            ],
            temperature=0.7,
            response_format=Evaluation,
        )
        
        # Parse the LLM response
        print("usage two:", completion.usage)
        response = completion.choices[0].message.parsed
        # print(response)
        feedback = response.feedback
        scores = response.scores  
        return scores, feedback

    except Exception as e:
        return {}, f"Error evaluating response: {str(e)}"
