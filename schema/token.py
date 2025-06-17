from enum import Enum
from uuid import UUID
from pydantic import BaseModel

class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"

class TokenData(BaseModel):
    uuid: UUID

class Token(BaseModel):
    accessToken: str
    tokenType: str 