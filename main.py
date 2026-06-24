from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
 
from database import get_db
from models import Todo
from schemas import TodoCreate, TodoUpdate, TodoReplace, TodoResponse
 
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Todo API", version="2.0.0")

@app.get("/todo", response_model = List[TodoResponse])
def get_all(db: Session = Depends(get_db)):
    return db.query(Todo).order_by(Todo.id).all()

@app.get("/todo/{todo_id}", response_model = TodoResponse)
def get_todo_by_id(todo_id: int, db: Session = Depends(get_db)):
    task = db.query(Todo).filter(Todo.id == todo_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail = "todo not found")
    return task

@app.post("/todo", status_code = 201, response_model = TodoResponse)
def create_todo(body: TodoCreate, db: Session = Depends(get_db)):
    find_title = db.query(Todo).filter(Todo.title == body.title).first()
    if find_title is not None:
        raise HTTPException(status_code = 409, detail = "Duplicate title")
    
    task = Todo(
        title = body.title,
        description = body.description,
        priority = body.priority,
        completed = False,
        due_date = body.due_date,
    )
    db.add(task)
    db.flush()
    db.refresh(task)
    return task

@app.put("/todo/{todo_id}", response_model = TodoResponse)
def replace_todo(todo_id: int, body: TodoReplace, db: Session = Depends(get_db)):
    task = db.query(Todo).filter(Todo.id == todo_id).first()
    if task is None:
        raise HTTPException(status_code = 404, detail = "todo not found")
    
    find_title = db.query(Todo).filter(Todo.title == body.title, Todo.id != todo_id).first()
    if find_title:
        raise HTTPException(status_code = 409, detail = "Duplicate title")

    task.title = body.title
    task.description = body.description
    task.priority = body.priority
    task.completed = body.completed
    task.due_date = body.due_date
    db.flush()
    db.refresh(task)
    return task

@app.patch("/todo/{todo_id}", response_model = TodoResponse)
def patch_todo(todo_id: int, body: TodoUpdate, db: Session = Depends(get_db)):
    task = db.query(Todo).filter(Todo.id == todo_id).first()
    if task is None:
        raise HTTPException(status_code = 404, detail = "todo not found")
    
    if body.title is not None:
        find_title = db.query(Todo).filter(Todo.title == body.title, Todo.id != todo_id).first()
        if find_title:
            raise HTTPException(status_code = 409, detail = "Duplicate title")
    
    if body.title is not None:
        task.title = body.title
    if body.description is not None:
        task.description = body.description
    if body.priority is not None:
        task.priority = body.priority
    if body.completed is not None:
        task.completed = body.completed
    if body.due_date is not None:
        task.due_date = body.due_date
    
    db.flush()
    db.refresh(task)
    return task
    
    
@app.delete("/todo/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    task = db.query(Todo).filter(Todo.id == todo_id).first()
    if task is None:
        raise HTTPException(status_code = 404, detail = "todo not found")

    db.delete(task)
    return None
    
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")

