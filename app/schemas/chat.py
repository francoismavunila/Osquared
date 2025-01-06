from pydantic import BaseModel, Field
from typing import List

class ScoreItem(BaseModel):
    goal: str = Field(..., description="The name of the goal being scored.")
    score: int = Field(
        ...,
        description="The score for the goal (expected to be between 1 and 10)."
    )

class Evaluation(BaseModel):
    scores: List[ScoreItem] = Field(
        ...,
        description="A list of scores, each containing a goal and its corresponding score."
    )
    feedback: str = Field(
        ...,
        description="A feedback message summarizing the user's performance and providing suggestions for improvement."
    )

    class Config:
        schema_extra = {
            "type": "object",
            "properties": {
                "scores": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "goal": {
                                "type": "string",
                                "description": "The name of the goal being scored."
                            },
                            "score": {
                                "type": "integer",
                                "description": "The score for the goal (expected to be between 1 and 10)."
                            }
                        },
                        "required": ["goal", "score"]
                    },
                    "description": "A list of dynamic scores, each containing a goal name and its score."
                },
                "feedback": {
                    "type": "string",
                    "description": "A feedback message summarizing the user's performance."
                }
            },
            "required": ["scores", "feedback"],
            "example": {
                "scores": [
                    {"goal": "privacy", "score": 8},
                    {"goal": "passwords", "score": 7},
                    {"goal": "personal_info", "score": 9}
                ],
                "feedback": "Great job! You demonstrated strong awareness of privacy risks by refusing to click on the suspicious link."
            }
        }
