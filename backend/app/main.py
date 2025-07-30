from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

app = FastAPI(
    title="Task Management API",
    description="A modern task management API built with FastAPI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None


class Task(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime


tasks_db: List[Task] = []


@app.get("/")
async def root():
    return {"message": "Task Management API", "version": "1.0.0"}


@app.get("/tasks", response_model=List[Task])
async def get_tasks():
    return tasks_db


@app.post("/tasks", response_model=Task)
async def create_task(task: TaskCreate):
    new_task = Task(
        id=str(uuid.uuid4()),
        title=task.title,
        description=task.description,
        created_at=datetime.now(),
    )
    tasks_db.append(new_task)
    return new_task


@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskCreate):
    for task in tasks_db:
        if task.id == task_id:
            task.title = task_update.title
            task.description = task_update.description
            return task
    return {"error": "Task not found"}


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    global tasks_db
    tasks_db = [task for task in tasks_db if task.id != task_id]
    return {"message": "Task deleted"}
