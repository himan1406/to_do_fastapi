from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class TodoCreate(BaseModel):
    title: str = Field(min_length = 1, strip_whitespace = True)
    description: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high"]] = "medium"
    due_date: Optional[datetime] = None

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(default = None, min_length = 1)
    description: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high"]] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None

class TodoReplace(BaseModel):
    title: str = Field(min_length = 1, strip_whitespace = True)
    description: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high"]] = "medium"
    completed: bool = False
    due_date: Optional[datetime] = None

class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str
    completed: bool
    created_at: datetime
    due_date: Optional[datetime] = None

    model_config = {"from_attributes": True}