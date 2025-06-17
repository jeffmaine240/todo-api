from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

class User(BaseModel):
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(
        unique=False,
        nullable=False
    )
    
    email: Mapped[str] = mapped_column(
        unique=True,
        nullable=False
    )
    
    password_hash: Mapped[str] = mapped_column(
        nullable=False
    )
    tasks: Mapped[list["Task"]] = relationship(back_populates="user") # type: ignore
    