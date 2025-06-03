from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .. import models, schemas, crud, database
from typing import List

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=schemas.Task)
async def create_task(task: schemas.TaskCreate, project_id: int, db: AsyncSession = Depends(database.get_db)):
    return await crud.create_task(db, task, project_id)

@router.get("/{task_id}", response_model=schemas.Task)
async def get_task(task_id: int, db: AsyncSession = Depends(database.get_db)):
    task = await crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# To be implemented: CRUD endpoints for tasks 