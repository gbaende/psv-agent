from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import Project

router = APIRouter()

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

@router.get("/", response_model=List[ProjectResponse])
async def get_projects(db: AsyncSession = Depends(get_db)):
    """Get all projects"""
    # In a real app, you'd query the database
    # For now, return mock data
    return [
        {
            "id": 1,
            "name": "Q4 Sales Campaign",
            "description": "End of year sales push",
            "start_date": datetime.now(),
            "end_date": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]

@router.post("/", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db: AsyncSession = Depends(get_db)):
    """Create a new project"""
    # In a real app, you'd create the project in the database
    # For now, return mock data
    return {
        "id": 1,
        "name": project.name,
        "description": project.description,
        "start_date": project.start_date,
        "end_date": project.end_date,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific project"""
    # In a real app, you'd query the database
    # For now, return mock data
    return {
        "id": project_id,
        "name": "Q4 Sales Campaign",
        "description": "End of year sales push",
        "start_date": datetime.now(),
        "end_date": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int, project: ProjectUpdate, db: AsyncSession = Depends(get_db)):
    """Update a project"""
    # In a real app, you'd update the project in the database
    # For now, return mock data
    return {
        "id": project_id,
        "name": project.name or "Q4 Sales Campaign",
        "description": project.description or "End of year sales push",
        "start_date": project.start_date or datetime.now(),
        "end_date": project.end_date,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

@router.delete("/{project_id}")
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a project"""
    # In a real app, you'd delete the project from the database
    return {"message": f"Project {project_id} deleted successfully"} 