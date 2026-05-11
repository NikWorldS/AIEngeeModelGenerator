from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Класс с настройками и параметрами для запуска. Считывает `.env` файл.
    """
    app_name: str = "EngeeModelGeneratorAPI v0.1"

    ollama_model_name: str

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "base_collection"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def qdrant_url(self) -> str:
        return f"http://{self.qdrant_host}:{self.qdrant_port}"

    @property
    def qdrant_collection_name(self) -> str:
        return self.qdrant_collection_name

    @property
    def ollama_model_name(self) -> str:
        return self.ollama_model_name

@lru_cache
def get_settings() -> Settings:
    return Settings()
