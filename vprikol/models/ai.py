from typing import List
from pydantic import BaseModel

class AIResponse(BaseModel):
    lines: List[str]
