from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import Task

router = APIRouter()

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: Optional[int] = None
    assigned_to: Optional[int] = None
    status: str = "pending"
    priority: str = "medium"
    task_type: str = "general"
    due_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    task_type: Optional[str] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    project_id: Optional[int] = None
    assigned_to: Optional[int] = None
    status: str
    priority: str
    task_type: str
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(db: AsyncSession = Depends(get_db)):
    """Get all tasks"""
    # In a real app, you'd query the database
    # For now, return mock data
    return [
        {
            "id": 1,
            "title": "Follow up with lead",
            "description": "Call potential client about proposal",
            "project_id": 1,
            "assigned_to": 1,
            "status": "pending",
            "priority": "high",
            "task_type": "sales_call",
            "due_date": datetime.now(),
            "completed_at": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]

@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    """Create a new task"""
    # In a real app, you'd create the task in the database
    # For now, return mock data
    return {
        "id": 1,
        "title": task.title,
        "description": task.description,
        "project_id": task.project_id,
        "assigned_to": task.assigned_to,
        "status": task.status,
        "priority": task.priority,
        "task_type": task.task_type,
        "due_date": task.due_date,
        "completed_at": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific task"""
    # In a real app, you'd query the database
    # For now, return mock data
    return {
        "id": task_id,
        "title": "Follow up with lead",
        "description": "Call potential client about proposal",
        "project_id": 1,
        "assigned_to": 1,
        "status": "pending",
        "priority": "high",
        "task_type": "sales_call",
        "due_date": datetime.now(),
        "completed_at": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_db)):
    """Update a task"""
    # In a real app, you'd update the task in the database
    # For now, return mock data
    return {
        "id": task_id,
        "title": task.title or "Follow up with lead",
        "description": task.description or "Call potential client about proposal",
        "project_id": 1,
        "assigned_to": 1,
        "status": task.status or "pending",
        "priority": task.priority or "high",
        "task_type": task.task_type or "sales_call",
        "due_date": task.due_date or datetime.now(),
        "completed_at": task.completed_at,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

@router.delete("/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a task"""
    # In a real app, you'd delete the task from the database
    return {"message": f"Task {task_id} deleted successfully"}

@router.post("/{task_id}/complete")
async def complete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """Mark a task as completed"""
    # In a real app, you'd update the task status in the database
    return {
        "message": f"Task {task_id} marked as completed",
        "completed_at": datetime.now()
    } 