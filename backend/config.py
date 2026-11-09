from functools import cached_property
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Always read backend/.env, whichever folder the server is started from.
ENV_FILE = Path(__file__).resolve().parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    cors_origins: str = "http://localhost:5173"
    # Vercel rejects request bodies over 4.5 MB, so stay below that.
    max_upload_mb: int = 4

    # Optional AI suggestions via Groq. Leave the key empty to disable the feature.
    groq_api_key: SecretStr | None = None
    groq_model: str = "openai/gpt-oss-120b"
    groq_timeout_seconds: float = 45.0

    @cached_property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    @property
    def ai_enabled(self) -> bool:
        return bool(self.groq_api_key and self.groq_api_key.get_secret_value().strip())


settings = Settings()
