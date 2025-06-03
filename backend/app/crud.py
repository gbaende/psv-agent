from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas

async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_project(db: AsyncSession, project_id: int):
    result = await db.execute(select(models.Project).where(models.Project.id == project_id))
    return result.scalar_one_or_none()

async def create_project(db: AsyncSession, project: schemas.ProjectCreate, owner_id: int):
    db_project = models.Project(**project.dict(), owner_id=owner_id)
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project

async def get_task(db: AsyncSession, task_id: int):
    result = await db.execute(select(models.Task).where(models.Task.id == task_id))
    return result.scalar_one_or_none()

async def create_task(db: AsyncSession, task: schemas.TaskCreate, project_id: int):
    db_task = models.Task(**task.dict(), project_id=project_id)
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

async def get_goal(db: AsyncSession, goal_id: int):
    result = await db.execute(select(models.Goal).where(models.Goal.id == goal_id))
    return result.scalar_one_or_none()

async def create_goal(db: AsyncSession, goal: schemas.GoalCreate, project_id: int):
    db_goal = models.Goal(**goal.dict(), project_id=project_id)
    db.add(db_goal)
    await db.commit()
    await db.refresh(db_goal)
    return db_goal

# Similar CRUD for Project, Task, Goal (to be expanded) 