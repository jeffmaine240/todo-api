from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuration settings for the application.
    """
    # General settings
    APP_NAME: str
    APP_VERSION: str
    APP_DESCRIPTION: str
    
    # Database settings
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # Security Settings
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_REFRESH_EXPIRY: int
    DEBUG_MODE: bool

    # Redis settings
    REDIS_URL: str

    class Config:
        env_file = ".env"

Config = Settings()