from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from models.user import User
from schema.response import ErrorResponse
from service.task import task_service
from service.user import user_service
from schema.task import TaskCreate, TaskListResponse, TaskOut, TaskData, TaskListOut, TaskResponse, TaskStatus, TaskUpdate, TaskType
from db.database import get_db
from utils.response import success_response


task_router = APIRouter(prefix="/tasks", tags=["Task"])


@task_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskResponse,
    responses={
        422: {
            'model': ErrorResponse,
            'description': 'Unprocessable Entity, such as when the due date is in the past or priority is out of range'
        },
        500: {
            'model': ErrorResponse,
            'description': 'Internal server error, such as database connection issues or unexpected errors'
        }
    }
    )
def create_task(data: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    task = task_service.create_task(task_data=data, db=db, user_uuid=current_user.uuid)
    response = success_response(
        data=TaskOut(
                task= TaskData(title=task.title,
                        description=task.description,
                        status=task.status,
                        uuid=task.uuid,
                        user_uuid=task.user_uuid,
                        due_date=task.due_date,
                        priority=task.priority,
                        status_change=task.status_change,
                        created_at=task.created_at,
                        updated_at=task.updated_at)

        ).model_dump(),
        message="Task created successfully",
        status_code=status.HTTP_201_CREATED
    )
    return response


@task_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=TaskListResponse,
    responses={
        500: {
            'model': ErrorResponse,
            'description': 'Internal server error, such as database connection issues or unexpected errors'
        }
    }
)
def list_tasks(status_filter: Optional[TaskType]=None, current_user: User = Depends(user_service.get_current_user), db: Session = Depends(get_db)):
    tasks = task_service.list_tasks(user_uuid=current_user.uuid, db=db, status_filter=status_filter)
    response = success_response(
        data=TaskListOut(tasks=[TaskData(
            uuid=task.uuid,
            title=task.title,
            description=task.description,
            status=task.status,
            user_uuid=task.user_uuid,
            due_date=task.due_date,
            priority=task.priority,
            status_change=task.status_change,
            created_at=task.created_at,
            updated_at=task.updated_at
        ) for task in tasks]).model_dump(),
        message="Tasks retrieved successfully",
        status_code=status.HTTP_200_OK
    )
    return response


@task_router.get(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=TaskResponse,
    responses={
        404: {
            'model': ErrorResponse,
            'description': 'Not Found, such as when the task does not exist or the user does not have access to it'
        },
        422: {
            'model': ErrorResponse,
            'description': 'Error when a random string is inputed ad task id instead of UUID'
        }
    }
)
def get_task(task_id: str, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    task = task_service.get_task(task_id=task_id, db=db, user_uuid=current_user.uuid)
    response = success_response(
        data=TaskOut(
            task=TaskData(
                uuid=task.uuid,
                title=task.title,
                description=task.description,
                status=task.status,
                user_uuid=task.user_uuid,
                due_date=task.due_date,
                priority=task.priority,
                status_change=task.status_change,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
        ).model_dump(),
        message="Task retrieved successfully",
        status_code=status.HTTP_200_OK
    )

    return response
    



@task_router.put(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=TaskResponse,
    responses={
        404: {
            'model': ErrorResponse,
            'description': 'Not Found, such as when the task does not exist or the user does not have access to it'
        },
        422: {
            'model': ErrorResponse,
            'description': 'Unprocessable Entity, such as when the due date is in the past or priority is out of range'
        },
        500: {
            'model': ErrorResponse,
            'description': 'Internal server error, such as database connection issues or unexpected errors'
        }
    }
)
def update_task(task_id: str, task_data: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    task = task_service.update_task(task_id=task_id, task_data=task_data, user_uuid=current_user.uuid, db=db)
    response = success_response(
        data=TaskOut(
            task=TaskData(
                uuid=task.uuid,
                title=task.title,
                description=task.description,
                status=task.status,
                user_uuid=task.user_uuid,
                due_date=task.due_date,
                priority=task.priority,
                status_change=task.status_change,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
        ).model_dump(),
        message="Task updated successfully",
        status_code=status.HTTP_200_OK
    )
    return response
    


@task_router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {
            'model': ErrorResponse,
            'description': 'Not Found, such as when the task does not exist or the user does not have access to it'
        },
        500: {
            'model': ErrorResponse,
            'description': 'Internal server error, such as database connection issues or unexpected errors'
        }
    }
)
def delete_task(task_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    task_deleted = task_service.delete_task(task_id=task_id, user_uuid=current_user.uuid, db=db)

    if isinstance(task_deleted, dict) and "detail" in task_deleted:
        return 



@task_router.put("/{task_id}/status")
def update_task_status(task_id: str, data: TaskStatus, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    task = task_service.update_task_status(task_id=task_id, data=data, user_uuid=current_user.uuid, db=db)
    response = success_response(
        data=TaskOut(
            task=TaskData(
                uuid=task.uuid,
                title=task.title,
                description=task.description,
                status=task.status,
                user_uuid=task.user_uuid,
                due_date=task.due_date,
                priority=task.priority,
                status_change=task.status_change,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
        ).model_dump(),
        message="Task status updated successfully",
        status_code=status.HTTP_200_OK
    )
    return response