from pydantic import BaseModel,Field
from typing import List, Optional, Dict


class Recommendation(BaseModel):
    title: str
    description: str
    source: str
    relevance: float