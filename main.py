import psycopg2
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, Literal
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import time


load_dotenv()

db_pool = psycopg2.pool.SimpleConnectionPool(
    1, 10,
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    host=os.environ.get("DB_HOST", "localhost"),
    database=os.environ.get("DB_NAME", "todo-app")
)

def get_db():
    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        db_pool.putconn(conn)

app = FastAPI()
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
def get_all(cursor = Depends(get_db)):
    cursor.execute("SELECT * FROM todos ORDER BY id")
    return cursor.fetchall()

@app.get("/todo/{todo_id}")
def get_todo_by_id(todo_id: int, cursor = Depends(get_db)):
    cursor.execute("SELECT * FROM todos WHERE id = %s;", (todo_id,))
    task = cursor.fetchone()
    if task is None:
        raise HTTPException(status_code = 404, detail = "todo not found")
    return task

@app.post("/todo", status_code = 201)
def create_todo(body: TodoCreate, cursor = Depends(get_db)):
    cursor.execute("SELECT id FROM todos WHERE title = %s;", (body.title,))
    find_title = cursor.fetchone()
    if find_title is not None:
        raise HTTPException(status_code = 409, detail = "duplicate title")

    post_query = """INSERT INTO todos (title, description, priority, created_at, completed) VALUES (%s, %s, %s, %s, %s) RETURNING *;"""
    cursor.execute(post_query, (
        body.title,
        body.description,
        body.priority,
        time.time(),
        False
    ))
    task = cursor.fetchone()
    return task

@app.put("/todo/{todo_id}")
def replace_todo(todo_id: int, body: TodoReplace, cursor = Depends(get_db)):
    cursor.execute("SELECT * FROM todos WHERE id = %s;", (todo_id,))
    task = cursor.fetchone()
    if task is None:
        raise HTTPException(status_code = 404, detail = "todo not found")
    if body.title is not None:
        cursor.execute("SELECT id from todos where title = %s and id != %s;", (body.title, todo_id))
        find_title = cursor.fetchone()
        if find_title:
            raise HTTPException(status_code = 409, detail = "duplicate title")
    
    put_query = """UPDATE todos SET title = %s, description = %s, priority = %s, completed = %s WHERE id = %s RETURNING *;"""

    cursor.execute(put_query, (
        body.title,
        body.description,
        body.priority,
        body.completed,
        todo_id
    ))

    return cursor.fetchone()

@app.patch("/todo/{todo_id}")
def patch_todo(todo_id: int, body: TodoUpdate, cursor = Depends(get_db)):
    cursor.execute("SELECT * FROM todos WHERE id = %s;", (todo_id,))
    task = cursor.fetchone()
    if task is None:
        raise HTTPException(status_code = 404, detail= "todo not found")
    if body.title is not None:
        cursor.execute("SELECT id from todos where title = %s and id != %s;", (body.title, todo_id))
        find_title = cursor.fetchone()
        if find_title:
            raise HTTPException(status_code = 409, detail = "duplicate tile")

    updates = []
    values = []

    if body.title is not None:
        updates.append("title = %s")
        values.append(body.title)
    if body.description is not None:
        updates.append("description = %s")
        values.append(body.description)
    if body.priority is not None:
        updates.append("priority = %s")
        values.append(body.priority)
    if body.completed is not None:
        updates.append("completed = %s")
        values.append(body.completed)

    if not updates:
        return task

    patch_query = f"UPDATE todos SET {', '.join(updates)} WHERE id = %s RETURNING *;"
    values.append(todo_id)
    cursor.execute(patch_query, tuple(values))
    return cursor.fetchone()
    
@app.delete("/todo/{todo_id}", status_code=204)
def delete_todo(todo_id: int, cursor = Depends(get_db)):
    cursor.execute("DELETE FROM todos WHERE id = %s RETURNING id;", (todo_id,))
    deleted = cursor.fetchone()
    if deleted is None:
        raise HTTPException(status_code = 404, detail = "todo not found")
    return None

app.mount("/static", StaticFiles(directory="static"), name="static")
 
 
@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")


