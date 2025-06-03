from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .. import models, schemas, crud, database
from typing import List

router = APIRouter(prefix="/goals", tags=["goals"])

@router.post("/", response_model=schemas.Goal)
async def create_goal(goal: schemas.GoalCreate, project_id: int, db: AsyncSession = Depends(database.get_db)):
    return await crud.create_goal(db, goal, project_id)

@router.get("/{goal_id}", response_model=schemas.Goal)
async def get_goal(goal_id: int, db: AsyncSession = Depends(database.get_db)):
    goal = await crud.get_goal(db, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal

# To be implemented: CRUD endpoints for goals 