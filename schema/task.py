from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from fastapi import HTTPException, status
from datetime import datetime, timezone
from enum import Enum

from schema.response import StandardResponse

class TaskType(Enum):
    """Enum for task status."""
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'

    def __str__(self):
        return self.value


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    due_date: int = Field(
        ...,
        description="Due date as Unix timestamp (seconds since epoch)",
        examples=[1767139199]  # 2025-12-31T23:59:59Z
    )
    priority: int = Field(default=1, ge=1, le=5)

    

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, value: int) -> int:
        now = int(datetime.now(timezone.utc).timestamp())
        if value <= now:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Due date must be in the future")
        return value


class TaskUpdate(BaseModel):
    title: Optional[str] = None  
    description: Optional[str] = None  
    due_date: Optional[int] = None 
    priority: Optional[int] = Field(
        default=None, ge=1, le=5, description="Priority level (1=lowest, 5=highest)"
    )

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, value: int) -> int:
        now = int(datetime.now(timezone.utc).timestamp())
        if value <= now:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Due date must be in the future")
        return value


class TaskData(TaskCreate):
    """Data model for task output."""
    uuid: UUID
    user_uuid: UUID
    status: TaskType
    created_at: datetime
    updated_at: datetime
    status_change: Optional[int]

class TaskOut(BaseModel):
    task: TaskData

class TaskListOut(BaseModel):
    tasks: list[TaskData]


class TaskStatus(BaseModel):
    status: TaskType

    @field_validator('status')
    @classmethod
    def validate_status(cls, value: TaskType) -> TaskType:
        if not isinstance(value, TaskType):
            raise ValueError("Invalid task status")
        return value
    
class TaskResponse(StandardResponse):
    data: TaskOut

class TaskListResponse(StandardResponse):
    data: TaskListOut
