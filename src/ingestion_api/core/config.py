from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Ingestion API"

    environment: str = "dev"

    database_url: str

    alembic_database_url: str

    upload_dir: str = "./data/uploads"

    embedding_model: str = (
        'intfloat/multilingual-e5-base'
    )

    openai_api_key: str

    llm_model: str = "gpt-3.5-turbo"

    embedding_dimensions: int = 768

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
