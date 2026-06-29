from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from routers import todo, auth

app = FastAPI(title="Todo API", version="2.0.0")

# Include routers
app.include_router(auth.router)
app.include_router(todo.router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")
