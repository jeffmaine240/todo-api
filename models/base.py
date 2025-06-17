from uuid import UUID, uuid4
from sqlalchemy import func
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base

class BaseModel(Base):
    __abstract__ = True

    uuid: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
        index=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(),  # Database-side timestamp
        server_default=func.now()
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now(),
        server_onupdate=func.now()
    )


    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id}>"

    def __str__(self):
        return self.__repr__()