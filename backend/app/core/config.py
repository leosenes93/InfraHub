import json
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    project_name: str = "InfraHub"
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"

    postgres_user: str = "infrahub"
    postgres_password: str = "change-me"
    postgres_db: str = "infrahub"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    database_url: str

    redis_host: str = "redis"
    redis_port: int = 6379
    redis_url: str = "redis://redis:6379/0"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7

    backend_cors_origins: str = "[]"

    initial_admin_email: str = "admin@infrahub.io"
    initial_admin_password: str = "change-me"
    initial_admin_full_name: str = "Administrador InfraHub"

    @property
    def cors_origins(self) -> list[str]:
        try:
            return json.loads(self.backend_cors_origins)
        except json.JSONDecodeError:
            return []


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
