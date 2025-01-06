from pydantic import BaseModel
from typing import List, Dict, Union


class User(BaseModel):
    username: str
    password: str
    scores: List[Dict[str, int]]
