import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from schema.task import TaskCreate, TaskStatus, TaskUpdate, TaskType
from models import Task


class TaskService:

    def create_task(self, task_data: TaskCreate, db: Session, user_uuid: UUID):
        try:
            task = Task(**task_data.model_dump(), status=TaskType.PENDING.value, user_uuid=user_uuid)
            db.add(task)
            db.commit()
            db.refresh(task)

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create task due to database error"
            )
        return task
    

    
    def list_tasks(self, user_uuid: UUID, db: Session, status_filter: Optional[TaskType] = None):
        try:
            if status_filter:
                tasks = db.query(Task).filter(Task.user_uuid == user_uuid, Task.status == status_filter.value).all()
            else:
                tasks = db.query(Task).filter(Task.user_uuid == user_uuid).all()
            return tasks
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve tasks due to database error"
            )

    def get_task(self, task_id: UUID, db: Session, user_uuid: UUID):
        try:
            task = db.query(Task).filter_by(uuid=task_id, user_uuid=user_uuid).first()
            if not task:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found for the given ID under this user")
            return task
        except SQLAlchemyError as e:
            print("error:", e.args)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="User id can't be a random, a uuid type is required"
            )
        

    def update_task(self, task_id: str, task_data: TaskUpdate, user_uuid: UUID, db: Session):

        try:
            task = db.query(Task).filter_by(uuid=task_id, user_uuid=user_uuid).first()
            if not task:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found for the given ID under this user")
            
            if task_data.due_date is not None:
                now = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
                if task_data.due_date <= now:
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Due date must be in the future")
            
            for key, value in task_data.model_dump(exclude_unset=True).items():
                if value is not None:
                    setattr(task, key, value)
            
            db.commit()
            db.refresh(task)
            return task
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update task due to database error"
            )
        

    def delete_task(self, task_id: UUID, user_uuid: UUID, db: Session):
        try:
            task = db.query(Task).filter(Task.user_uuid==user_uuid, Task.uuid == task_id).first()
            print(f"task: {task}")
            if not task:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found for the given ID under this user")
            db.delete(task)
            db.commit()
            return {"detail": "Task deleted successfully"}
        
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Failed to delete task due to database error"
            )
    
    def update_task_status(self, task_id: str, data: TaskStatus, user_uuid: UUID, db: Session):

        try:
            task = db.query(Task).filter_by(uuid=task_id, user_uuid=user_uuid).first()
            if not task:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found for the given ID under this user")
            task.status = data.status.value
            task.status_change = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
            db.commit()
            db.refresh(task)
            return task
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update task status due to database error"
            )

task_service = TaskService()