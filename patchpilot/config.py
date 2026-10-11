from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")
    serpapi_api_key: str = ""
    groq_api_key: str = ""
    nvidia_api_key: str = ""
    llm_provider: str = ""
    llm_model: str = ""
    neatlogs_api_key: str = ""
    database_path: str = str(ROOT / ".data" / "patchpilot.db")
    port: int = 8017

    @property
    def provider(self):
        return self.llm_provider or ("groq" if self.groq_api_key else "nvidia")

    @property
    def model(self):
        return self.llm_model or (
            "openai/gpt-oss-120b" if self.provider == "groq" else "meta/llama-3.3-70b-instruct"
        )

    @property
    def llm_key(self):
        return self.groq_api_key if self.provider == "groq" else self.nvidia_api_key
