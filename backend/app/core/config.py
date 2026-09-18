from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    # Aplicación
    app_name: str = "Business AI Agent"
    api_v1_prefix: str = "/api/v1"
    port: int = Field(default=8000, alias="PORT")
    allowed_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        alias="ALLOWED_ORIGINS",
    )

    # Seguridad
    secret_key: str = "dev-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    # Base de datos
    database_url: str = "sqlite:///./app.db"
    tenant_id: int = Field(default=1, alias="TENANT_ID")
    business_name: str = Field(default="Flash Bites", alias="BUSINESS_NAME")

    # ChromaDB
    chroma_persist_directory: str = "./data/chroma"

    # Documentos para RAG
    documents_directory: str = "./documents"

    # Gemini
    gemini_api_key: str = Field(
        default="",
        alias="GEMINI_API_KEY",
    )

    gemini_model: str = Field(
        default="gemini-2.5-flash",
        alias="GEMINI_MODEL",
    )

    # Ambiente
    environment: str = Field(
        default="development",
        alias="ENVIRONMENT",
    )


settings = Settings()