from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from core.config import Config
from api.router import router
from utils.response import error_response, success_response

app = FastAPI(
    title=Config.APP_NAME,
    description=Config.APP_DESCRIPTION,
    version=Config.APP_VERSION,
)

#cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router, prefix="/api")


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException) -> error_response:
    """
    Custom exception handler for HTTP exceptions.
    This function handles HTTP exceptions raised in the
    application and returns a standardized JSON response.

    Args:
        request (Request): request object
        exc (HTTPException): exception object

    Returns:
        JSONResponse: details about the exception
    """

    response = error_response(
        message=str(exc.detail),
        status_code=exc.status_code,
        errors=str(exc.__class__.__name__),
    )
    return response


@app.get("/")
def health_check() -> success_response:
    return success_response(
        data={"message": "API is running"},
        message="API is running",
        status_code=200,
    )