from pydantic import BaseModel,Field
from typing import List, Optional, Dict


class UserProfile(BaseModel):
    user_id: str
    interests: List[str]
    preferences: Optional[Dict] = {}
    demographics: Optional[Dict] = {}