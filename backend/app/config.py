import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://jwb_user:jwb_pass@localhost:5432/jwb_nexus")
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    cors_origins: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

    class Config:
        env_file = ".env"


settings = Settings()
