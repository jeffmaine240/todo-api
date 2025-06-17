from typing import Optional
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
import datetime as dt
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from jose import jwt, JWTError
from fastapi.exceptions import HTTPException
from fastapi import Depends, status
import redis

from db.database import get_db
from schema.token import TokenData, TokenType
from schema.user import UserRegister, UserLogin
from core.config import Config
from models import User

oauth2_scheme = HTTPBearer()

class UserService:

    def __init__(self):
        self.pwdContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.redisClient = redis.Redis.from_url(Config.REDIS_URL, decode_responses=True) 

    def _hash_password(self, plainPassword: str) -> str:
        """Securely hash a password using bcrypt."""

        return self.pwdContext.hash(plainPassword)
    

    def _verify_password(self, plainPassword: str, hashedPassword: str) -> bool:
        """Verify a password against its hashed version."""

        return self.pwdContext.verify(plainPassword, hashedPassword)
    

    def _create_token(self, uuid: str, type: TokenType) -> str:

        expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(
            minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        data = {
            "uuid": str(uuid),
            "exp": expires,
            "type": type.value
        }
        encodedJwt = jwt.encode(data, Config.SECRET_KEY, Config.ALGORITHM)
        return encodedJwt
    
    def _verify_token(self, token: str, token_type: TokenType) -> TokenData:

        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
            if payload.get("type") != token_type.value:
                raise HTTPException(
                    detail="Invalid token type", status_code=status.HTTP_400_BAD_REQUEST
                )
            
            if "uuid" not in payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return TokenData(uuid=payload.get("uuid"))

        except JWTError as e:
            raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

    def get_user_with_uuid(self, uuid, db: Session):
        try:
            user = db.query(User).filter(User.uuid == uuid).first()
            if user:
                return user
        except SQLAlchemyError as e:
            return None
    
    
    def create_user(self, data: UserRegister, db:Session):
        try:
            exist = db.query(User).filter(User.email == data.email).first()
            if exist:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email registered already")
            
            data_dict = data.model_dump(exclude="password")
            data_dict["password_hash"] = self._hash_password(data.password)
            new_user = User(**data_dict)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user

        except SQLAlchemyError as e:
            print("sqlerror:", e)
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Failed to create user due to database error"
            )
    

    

    def authenticate_user(self, data: UserLogin, db: Session):
        try:
            user = db.query(User).filter(User.email == data.email).first()
            if not user or not self._verify_password(data.password, user.password_hash):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            return user
        
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service unavailable",
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred"
            )
    
    # def _isRefreshTokenActive(self, refreshToken: str) -> bool:
    #     """Check if refresh token is valid (not blacklisted).

    #     Args:
    #         refreshToken: Token to check

    #     Returns:
    #         bool: True if token is active
    #     """
    #     blacklisted = self.redisClient.get(f"blacklisted_token:{refreshToken}")
    #     return blacklisted is None
    
    def get_current_user(self, credentials: HTTPAuthorizationCredentials=Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[User]:
        try:
            token = credentials.credentials
            token_data = self._verify_token(token=token, token_type=TokenType.ACCESS)
            uuid = token_data.uuid

            user = self.get_user_with_uuid(uuid=uuid, db=db)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="user not found, app secret key and algorithm may have been exposed",
                )
            return user

        except Exception as e:
            print(f"Error in get_current_user: {e}")
            if isinstance(e, HTTPException):
                raise e
            else:

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An unexpected error occurred while retrieving the current user"
                )

user_service = UserService()