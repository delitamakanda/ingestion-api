from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ingestion API"

    environment: str = "dev"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ingestion_api"

    alembic_database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ingestion_api"

    upload_dir: str = "./data/uploads"

    processing_version: str = "1.0.0"

    parser_version: str = "1.0.0"

    chunking_version: str = "1.0.0"

    metadata_version: str = "1.0.0"

    embedding_model: str = "intfloat/multilingual-e5-base"

    openai_api_key: str

    llm_model: str = "gpt-6.1-terra"

    embedding_dimensions: int = 768

    reranker_model: str = "BAAI/bge-reranker-v2-m3"

    reranker_candidates: int = 10

    reranker_top_k: int = 5

    redis_url: str = "redis://localhost:6379/0"

    ingestion_max_attempts: int = 3

    jwt_secret_key: str

    jwt_algorithm: str = "HS256"

    jwt_access_token_expires_minutes: int = 30

    login_ip_limit: int = 20

    login_email_limit: int = 5

    login_rate_limit_window_seconds: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
