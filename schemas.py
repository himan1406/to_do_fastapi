from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class TodoCreate(BaseModel):
    title: str = Field(min_length = 1, strip_whitespace = True)
    description: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high"]] = "medium"

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(default = None, min_length = 1)
    description: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high"]] = None
    completed: Optional[bool] = None

class TodoReplace(BaseModel):
    title: str = Field(min_length = 1, strip_whitespace = True)
    description: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high"]] = "medium"
    completed: bool = False

class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str
    completed: bool
    created_at: datetime

    model_config = {"from_attributes": True}