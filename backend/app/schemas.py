from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class UserBase(BaseModel):
    name: str
    email: str
    slack_id: Optional[str]

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

class ProjectBase(BaseModel):
    name: str
    description: Optional[str]

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    owner_id: int
    class Config:
        orm_mode = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str]
    completed: bool = False

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    project_id: int
    class Config:
        orm_mode = True

class GoalBase(BaseModel):
    description: str
    week_start: date
    achieved: bool = False

class GoalCreate(GoalBase):
    pass

class Goal(GoalBase):
    id: int
    project_id: int
    class Config:
        orm_mode = True 