from fastapi import APIRouter

from .auth import auth_router
from .task import task_router

router = APIRouter(prefix=f"/v1")

router.include_router(auth_router)
router.include_router(task_router)