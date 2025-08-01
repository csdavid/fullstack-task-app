import os
from dotenv import load_dotenv

# Load environment variables before importing anything else
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database import get_database_session
from app.crud import UserRepository, TaskRepository
from app.schemas import (
    User,
    UserCreate,
    UserUpdate,
    UserWithTasks,
    Task,
    TaskCreate,
    TaskUpdate,
    TaskWithOwner,
)

from typing import List, Optional
import uuid
from datetime import datetime


app = FastAPI(
    title="Task Management API",
    description="A production-ready task management API built with FastAPI",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "helthy", "message": "Task Management API is running"}


# User endpoints
@app.post("/users", response_model=User)
async def create_user(
    user_data: UserCreate, session: AsyncSession = Depends(get_database_session)
):
    user_repo = UserRepository(session)

    # Check if user already exists
    existing_user = await user_repo.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_username = await user_repo.get_by_username(user_data.username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    return await user_repo.create(user_data)


@app.get("/users/{user_id}", response_model=UserWithTasks)
async def get_user(user_id: int, session: AsyncSession = Depends(get_database_session)):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


# Task endpoints
@app.post("/users/{user_id}/tasks", response_model=Task)
async def create_task(
    user_id: int,
    task_data: TaskCreate,
    session: AsyncSession = Depends(get_database_session),
):
    user_repo = UserRepository(session)
    task_repo = TaskRepository(session)

    # Verify user exists
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return await task_repo.create(task_data, user_id)


@app.get("/users/{user_id}/tasks", response_model=List[Task])
async def get_user_tasks(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    completed: Optional[bool] = Query(None),
    priority: Optional[str] = Query(None, pattern="^(low|medium|high)$"),
    search: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_database_session),
):
    user_repo = UserRepository(session)
    task_repo = TaskRepository(session)

    # Verify user exists
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return await task_repo.get_user_tasks(
        owner_id=user_id,
        skip=skip,
        limit=limit,
        completed=completed,
        priority=priority,
        search=search,
    )


@app.get("/tasks/{task_id}", response_model=TaskWithOwner)
async def get_task(task_id: int, session: AsyncSession = Depends(get_database_session)):
    task_repo = TaskRepository(session)
    task = await task_repo.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    return task


@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    session: AsyncSession = Depends(get_database_session),
):
    task_repo = TaskRepository(session)
    task = await task_repo.update(task_id, task_data)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    return task


@app.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int, session: AsyncSession = Depends(get_database_session)
):
    task_repo = TaskRepository(session)
    deleted = await task_repo.delete(task_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    return {"message": "Task deleted successfully"}


@app.get("/users/{user_id}/tasks/stats")
async def get_task_stats(
    user_id: int, session: AsyncSession = Depends(get_database_session)
):
    user_repo = UserRepository(session)
    task_repo = TaskRepository(session)

    # Verify user exists
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return await task_repo.get_task_stats(user_id)


@app.get("/")
async def root():
    return {"message": "Task Management API", "version": "2.0.0"}


# For demo
@app.get("/tasks", response_model=List[Task])
async def get_demo_tasks(session: AsyncSession = Depends(get_database_session)):
    user_repo = UserRepository(session)
    task_repo = TaskRepository(session)

    demo_user = await user_repo.get_by_username("demo")
    if not demo_user:
        demo_user_data = UserCreate(
            email="demo@example.com", username="demo", full_name="Demo User"
        )
        demo_user = await user_repo.create(demo_user_data)

    return await task_repo.get_user_tasks(demo_user.id)


@app.post("/tasks", response_model=Task)
async def create_demo_task(
    task_data: TaskCreate, session: AsyncSession = Depends(get_database_session)
):
    user_repo = UserRepository(session)
    task_repo = TaskRepository(session)

    # Get or create demo user
    demo_user = await user_repo.get_by_username("demo")
    if not demo_user:
        demo_user_data = UserCreate(
            email="demo@example.com", username="demo", full_name="Demo User"
        )
        demo_user = await user_repo.create(demo_user_data)

    return await task_repo.create(task_data, demo_user.id)
