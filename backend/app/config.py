from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM (Groq — mandatory)
    groq_api_key: str = ""
    model_name: str = "gemma2-9b-it"

    # Database
    database_url: str = "sqlite:///./hcp_crm.db"

    # CORS
    cors_origins: str = "http://localhost:5173"


settings = Settings()
