from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Primary LLM Provider Configuration
    # Supported providers: ollama (default local), mock, openai, anthropic, google
    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "qwen3:4b"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Optional External API Provider Keys (leave empty for local Ollama)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: Optional[str] = "gpt-4o"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: Optional[str] = "claude-3-5-sonnet-20241022"
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_MODEL: Optional[str] = "gemini-1.5-pro"

    # Interview Evaluation Configuration
    HUMAN_REVIEW_THRESHOLD: float = 5.0

    # Adaptive difficulty thresholds (composite score out of 10)
    DIFFICULTY_UPGRADE_THRESHOLD: float = 8.0
    DIFFICULTY_DOWNGRADE_THRESHOLD: float = 5.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
