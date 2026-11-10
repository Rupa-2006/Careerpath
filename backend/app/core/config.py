from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    environment: str = "development"
    database_url: str = "postgresql+psycopg://postgres@127.0.0.1:5433/careerpath"
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    session_days: int = 14
    # Shows records still waiting for review, clearly labelled. Never turn this on for real students.
    show_unpublished: bool = False
    # Optional AI rewording of answers, for trying out on this computer only. See assistant_ai_on.
    assistant_ai: bool = False
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"
    # "local" runs a free model on this computer through Ollama. No data leaves the machine.
    assistant_ai_provider: str = "gemini"
    local_ai_url: str = "http://127.0.0.1:11434"
    local_ai_model: str = "llama3.2:3b"
    # Account emails (reset codes). Empty SMTP_HOST means laptop mode: emails are printed, not sent.
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""

    @field_validator("environment")
    @classmethod
    def known_environment(cls, value: str) -> str:
        if value not in {"development", "production"}:
            raise ValueError("ENVIRONMENT must be development or production")
        return value

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def visible_statuses(self) -> tuple[str, ...]:
        if self.show_unpublished and not self.is_production:
            return ("published", "verified", "pending_verification")
        return ("published",)

    @property
    def assistant_ai_on(self) -> bool:
        if not self.assistant_ai:
            return False
        if self.assistant_ai_provider == "local":
            return True   # a model on this computer: nothing is sent to an outside company
        return bool(self.gemini_api_key) and not self.is_production

    @property
    def origins(self) -> set[str]:
        return {origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
