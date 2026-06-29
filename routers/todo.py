from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import crud
from schemas import TodoCreate, TodoUpdate, TodoReplace, TodoResponse
from routers.deps import get_current_user
from models import User

router = APIRouter(prefix="/todo", tags=["todos"])

@router.get("", response_model=List[TodoResponse])
def read_todos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.get_todos(db, user_id=current_user.id)

@router.get("/{todo_id}", response_model=TodoResponse)
def read_todo(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = crud.get_todo_by_id(db, todo_id, user_id=current_user.id)
    if todo is None:
        raise HTTPException(status_code=404, detail="todo not found")
    return todo

@router.post("", status_code=201, response_model=TodoResponse)
def create_todo(body: TodoCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing_todo = crud.get_todo_by_title(db, body.title, user_id=current_user.id)
    if existing_todo is not None:
        raise HTTPException(status_code=409, detail="Duplicate title")
    return crud.create_todo(db, body, user_id=current_user.id)

@router.put("/{todo_id}", response_model=TodoResponse)
def replace_todo(todo_id: int, body: TodoReplace, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = crud.get_todo_by_id(db, todo_id, user_id=current_user.id)
    if todo is None:
        raise HTTPException(status_code=404, detail="todo not found")
    
    existing_todo = crud.get_todo_by_title_exclude(db, body.title, todo_id, user_id=current_user.id)
    if existing_todo is not None:
        raise HTTPException(status_code=409, detail="Duplicate title")
        
    return crud.replace_todo(db, todo, body)

@router.patch("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, body: TodoUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = crud.get_todo_by_id(db, todo_id, user_id=current_user.id)
    if todo is None:
        raise HTTPException(status_code=404, detail="todo not found")
        
    if body.title is not None:
        existing_todo = crud.get_todo_by_title_exclude(db, body.title, todo_id, user_id=current_user.id)
        if existing_todo is not None:
            raise HTTPException(status_code=409, detail="Duplicate title")
            
    return crud.update_todo(db, todo, body)

@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = crud.get_todo_by_id(db, todo_id, user_id=current_user.id)
    if todo is None:
        raise HTTPException(status_code=404, detail="todo not found")
    crud.delete_todo(db, todo)
    return None
