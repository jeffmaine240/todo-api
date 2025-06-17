from uuid import UUID
from pydantic import BaseModel, EmailStr

from schema.response import StandardResponse


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserData(BaseModel):
    uuid: UUID
    username: str
    email: str

    class Config:
        orm_mode = True

class UserOut(BaseModel):
    user: UserData
    accessToken: str


class UserResponse(StandardResponse):
    data: UserOut