import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Business AI Agent"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "dev-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = "sqlite:///./app.db"
    chroma_persist_directory: str = "./data/chroma"
    documents_directory: str = "./data/documents"
    openai_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
