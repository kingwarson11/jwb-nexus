import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://jwb_user:jwb_pass@localhost:5432/jwb_nexus")
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # Kept as a plain string field on purpose: pydantic-settings auto-parses env vars
    # as JSON for list-typed fields, which breaks on a plain comma-separated value
    # like "https://a.com,http://localhost:5173". We parse it ourselves instead.
    cors_origins_raw: str = os.getenv("CORS_ORIGINS", "http://localhost:5173")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    class Config:
        env_file = ".env"


settings = Settings()
