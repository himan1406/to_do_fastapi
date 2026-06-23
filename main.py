from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, Literal
import time

app = FastAPI()

todo = []
_id_counter = 1

def next_id():
    global _id_counter
    current = _id_counter
    _id_counter += 1
    return current 

class TodoCreate(BaseModel):
    title: str = Field(min_length = 1, strip_whitespace = True)
    description: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high"]] = "medium"

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high"]] = None
    completed: Optional[bool] = None

class TodoReplace(BaseModel):
    title: str
    description: Optional[str] = ""
    priority: Optional[Literal["low", "medium", "high"]] = "medium"
    completed: Optional[bool] = False

@app.get("/todo")
def get_all():
    return todo

@app.get("/todo/{todo_id}")
def get_todo_by_id(todo_id: int):
    task = next((t for t in todo if t["id"] == todo_id ), None)
    if task is None:
        raise HTTPException(status_code = 404, detail = "todo not found")
    return task

@app.post("/todo", status_code = 201)
def create_todo(body: TodoCreate):
    task = {
        "id": next_id(),
        "title": body.title,
        "description": body.description,
        "priority": body.priority,
        "completed": False,
        "created_at": int(time.time()),
    }
    find_title = next((t for t in todo if t["title"] == body.title), None)
    if find_title is None:
        todo.append(task)
    else:
        raise HTTPException(status_code = 409, detail = "duplicate title")
    return task

@app.put("/todo/{todo_id}")
def replace_todo(todo_id: int, body: TodoReplace):
    task = next((t for t in todo if t["id"] == todo_id), None)
    if task is None:
        raise HTTPException(status_code = 404, detail = "todo not found")
    if body.title is not None:
        if any(t["title"] == body.title and t["id"] != todo_id for t in todo):
            raise HTTPException(status_code=409, detail="duplicate title")
    task["title"] = body.title
    task["description"] = body.description
    task["priority"] = body.priority
    task["completed"] = body.completed
    return task

@app.patch("/todo/{todo_id}")
def patch_todo(todo_id: int, body: TodoUpdate):
    task = next((t for t in todo if t["id"] == todo_id), None)
    if task is None:
        raise HTTPException(status_code = 404, detail= "todo not found")
    if body.title is not None:
        task["title"] = body.title
    if body.description is not None:
        task["description"] = body.description
    if body.priority is not None:
        task["priority"] = body.priority
    if body.completed is not None:
        task["completed"] = body.completed
    return task
    
@app.delete("/todo/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    global todo
    task = next((t for t in todo if t["id"] == todo_id), None)
    if task is None:
        raise HTTPException(status_code = 404, detail = "todo not found")
    todo = [t for t in todo if t["id"] != todo_id]
    return None

app.mount("/static", StaticFiles(directory="static"), name="static")
 
 
@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")


