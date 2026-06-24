from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key = True, index = True)
    title = Column(String, nullable = False, unique = True)
    description = Column(String, nullable = False)
    priority = Column(String, nullable = False, default = "medium")
    completed = Column(Boolean, nullable = False, default = False)
    created_at = Column(DateTime(timezone=True), server_default = func.now(), nullable = False)
    due_date = Column(DateTime(timezone=True), nullable = True)
    