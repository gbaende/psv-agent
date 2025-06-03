from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .. import models, schemas, crud, database
from typing import List

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=schemas.Project)
async def create_project(project: schemas.ProjectCreate, owner_id: int, db: AsyncSession = Depends(database.get_db)):
    return await crud.create_project(db, project, owner_id)

@router.get("/{project_id}", response_model=schemas.Project)
async def get_project(project_id: int, db: AsyncSession = Depends(database.get_db)):
    project = await crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# To be implemented: CRUD endpoints for projects 