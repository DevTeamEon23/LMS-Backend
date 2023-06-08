from .config import env_file
from pydantic import BaseSettings


class Settings(BaseSettings):
    DBNAME: str  # database name
    PG_USER: str  # user of the database
    PG_PASSWORD: str  # password of the database
    PG_HOST: str  # hostname of the database
    PG_PORT: int = 3306  # port number of the database

    SERVER_RELOAD: bool = False  # Default server reload mode
    DEBUG: bool  # Whether to enable debug
    DOCS_URL: str = "/docs"
    OPENAPI_URL: str = "/openapi.json"
    REDOC_URL: str = "/redoc"

    JWT_SECRECT: str = "ADSHGFKKFHKKHJDHJKKDHHDKLDDUUS"

    class Config:
        env_file = env_file


# Instance Object
settings = Settings()
