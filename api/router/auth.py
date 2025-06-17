from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import datetime as dt

from models.user import User
from schema.response import ErrorResponse, SuccessResponse
from schema.token import TokenType
from db.database import get_db
from service.user import user_service
from utils.response import success_response
from schema.user import UserOut, UserData, UserLogin, UserRegister, UserResponse


auth_router = APIRouter(prefix="/auth",tags=["Auth"])


@auth_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
        responses={
        409: {
            'model': ErrorResponse,
            'description': 'Conflict error, such as when a user with the same email already exists'
        },
        500: {
            'model': ErrorResponse,
            'description': 'Internal server error, such as database connection issues or unexpected errors'
        }
    })
def register(
    data: UserRegister,
    db: Session=Depends(get_db)
):
    
    user = user_service.create_user(data=data, db=db)

    access_token = user_service._create_token(uuid=user.uuid, type=TokenType.ACCESS)
    refresh_token = user_service._create_token(uuid=user.uuid, type=TokenType.REFRESH)


    response = success_response(
        data=UserOut(
            user=UserData(
                uuid=user.uuid,
                username=user.username,
                email=user.email
            ),
            accessToken=access_token,
        ).model_dump(),
        message="user registered successfully",
        status_code=status.HTTP_201_CREATED,
    )

    if isinstance(response, JSONResponse):
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            expires=dt.timedelta(days=30),
            httponly=True,
            secure=True,
            samesite="none",
        )
    
    return response



@auth_router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
    responses={
        401: {
            'model': ErrorResponse,
            'description': 'Unauthorized error, such as when the user credentials are invalid'
        },
        500: {
            'model': ErrorResponse,
            'description': 'Internal server error, such as database connection issues or unexpected errors'
        }
    })

def login(data: UserLogin, db: Session = Depends(get_db)):
    user = user_service.authenticate_user(data=data, db=db)
    

    access_token = user_service._create_token(uuid=user.uuid, type=TokenType.ACCESS)
    refresh_token = user_service._create_token(uuid=user.uuid, type=TokenType.REFRESH)

    response = success_response(
        data=UserOut(
            user=UserData(
                uuid=user.uuid,
                username=user.username,
                email=user.email
            ),
            accessToken=access_token,
        ).model_dump(),
        message="user logged in successfully",
        status_code=status.HTTP_200_OK,
    )
    print("Logged in ")
    if isinstance(response, JSONResponse):
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            expires=dt.timedelta(days=30),
            httponly=True,
            secure=True,
            samesite="none",
        )
    
    return response


@auth_router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse,
    responses={
        401: {
            'model': ErrorResponse,
            'description': 'Unauthorized error, such as when the user is not logged in or the refresh token is missing'
        },
        500: {
            'model': ErrorResponse,
            'description': 'Internal server error, such as database connection issues or unexpected errors'
        }
    })
def logout_user(request: Request, response: Response,
                        current_user: User = Depends(user_service.get_current_user)) -> success_response:

    refresh_token = request.cookies.get("refresh_token")
    user_service.redisClient.setex(
        f"blacklisted_token:{refresh_token}", dt.timedelta(days=30), "blacklisted"
    )
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided, please login again",
        )

    response.delete_cookie(
        key="refreshToken",
        path="/",
        domain=None,
        httponly=True,
        samesite="none",
        secure=True,
    )

    return success_response(
        data=None,
        message="Student logged out successfully",
        status_code=status.HTTP_200_OK,
    )


