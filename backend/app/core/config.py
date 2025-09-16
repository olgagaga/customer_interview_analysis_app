from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator
from typing import List, Optional, Union


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    PROJECT_NAME: str = "Customer Interview Analysis API"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/interviews"

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] | List[str] | str = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]):
        if isinstance(v, str):
            # Accept JSON-style list or comma-separated string
            value = v.strip()
            if value.startswith("[") and value.endswith("]"):
                # Remove brackets and split by comma
                items = [i.strip().strip('"').strip("'") for i in value[1:-1].split(",") if i.strip()]
                return items
            if "," in value:
                return [i.strip() for i in value.split(",") if i.strip()]
            # Single origin string
            return [value]
        return v


settings = Settings() 