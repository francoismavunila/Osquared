from datetime import datetime
import uuid
from fastapi import HTTPException
from openai import OpenAI
import os
from dotenv import load_dotenv
from app.schemas.chat import Evaluation
from app.db import db
from app.schemas.Exception import CustomError

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
        )
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
        )
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
        )
    }
}

def generate_conversation_id(user_name: str, persona: str) -> str:
    return f"user_{user_name}_persona_{persona}"

def get_initial_message(user_name, persona) -> str:
    if persona not in personas:
        raise CustomError("Persona not found")

    persona_data = personas[persona]
    messages = [
        {"role": "developer", "content": f"You are {persona_data['name']}. {persona_data['description']} {persona_data['behavior']}."},
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
def generate_persona_response(user_message, history=[]):
    # print("history on generate persona", history)
    persona = personas["scammer"]
    messages = [{'role': entry['role'], 'content': entry['content']} for entry in history]
    messages.insert(0, {"role": "developer", "content": f"You are {persona['name']}. {persona['description']} {persona['behavior']}."})
    messages.append({'role': 'user', 'content': user_message})

    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Evaluate user response
def evaluate_user_response(user_response, persona_response):
    if not isinstance(user_response, str) or not user_response.strip():
        raise ValueError("Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]")
    
    scoring_prompt = (
        f"Evaluate the following user response to a scammer's message:\n\n"
        f"Scammer's message: {persona_response}\n"
        f"User's response: {user_response}\n\n"
        f"Score the user's response on a scale of 1 to 10 based on how effectively they avoided falling for the scam, "
        f"and provide feedback on their actions. Consider the following points:\n"
        f"- Did the user recognize the scam?\n"
        f"- Did the user avoid providing sensitive information?\n"
        f"- Did the user respond appropriately to the scammer?\n\n"
        f"Examples of good responses:\n"
        f"- 'I don't share personal information online.'\n"
        f"- 'This seems suspicious, I will report it.'\n"
        f"- 'I will contact my bank directly to verify this.'\n\n"
        f"Examples of poor responses:\n"
        f"- 'Here is my password.'\n"
        f"- 'I clicked the link.'\n"
        f"- 'I provided my credit card details.'"
    )

    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": "You are an educator providing responses in a cybersecurity simulation aimed at teaching children about online safety. Your responses should be educational, friendly, and easy to understand."},
                {"role": "user", "content": scoring_prompt}
            ],
            max_tokens=150,
            temperature=0.7,
            response_format=Evaluation,
        )
        response = completion.choices[0].message.parsed
        print(response.score)
        return response.score, response.feedback
    except Exception as e:
        return 0, f"Error evaluating response: {str(e)}"