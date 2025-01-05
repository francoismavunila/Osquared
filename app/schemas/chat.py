from pydantic import BaseModel

class Evaluation(BaseModel):
    score: str
    feedback: str