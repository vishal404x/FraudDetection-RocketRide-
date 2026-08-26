from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./dev.db"
    SECRET_KEY: str = "replace-me-with-secure-random"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    APPROVAL_THRESHOLD: float = 500000.0  # amounts >= this require approval by default

    class Config:
        env_file = ".env"

settings = Settings()
