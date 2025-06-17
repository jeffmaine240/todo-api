from uuid import UUID
from sqlalchemy import BigInteger, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from .base import BaseModel
from schema.task import TaskType


class Task(BaseModel):
    __tablename__ = 'tasks' 

    title: Mapped[str] = mapped_column(nullable=False)
    description:  Mapped[str] = mapped_column(nullable=True)
    status:  Mapped[str] = mapped_column(nullable=False, default=TaskType.PENDING.value)  
    user_uuid: Mapped[UUID] = mapped_column(ForeignKey("users.uuid"))
    priority: Mapped[int] = mapped_column(default=1)
    due_date: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        comment="Unix timestamp (seconds since epoch)"
    )
    
    status_change: Mapped[int] = mapped_column(
        BigInteger,
        nullable=True,
        comment="Last status change as epoch seconds"
    )
    
    # Relationship (many-to-one: Task -> User)
    user: Mapped["User"] = relationship(back_populates="tasks") # type: ignore


    def __repr__(self):
        return f"Task(task_id={self.uuid}, title={self.title}, description={self.description}, status={self.status})"