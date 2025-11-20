from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", env_file=None, extra="ignore")

    ENV: str = "dev"  # dev|prod
    JWT_SECRET: str = "change-me"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRES_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRES_DAYS: int = 7
    PASSWORD_SCHEME: str = "bcrypt"  # bcrypt|pbkdf2_sha256
    ALLOWED_ORIGINS: str = "*"  # comma-separated for CORS
    REDIS_URL: str = "redis://localhost:6379/0"

    @field_validator("JWT_SECRET")
    @classmethod
    def _validate_jwt_secret(cls, v: str, info):  # noqa: ANN001
        # In prod, require non-default secret
        env = info.data.get("ENV", "dev")
        if env == "prod" and v == "change-me":
            raise ValueError("JWT_SECRET must be set in production")
        return v


settings = AppSettings()
