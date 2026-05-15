from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    """
    Класс с настройками и параметрами для запуска. Считывает `.env` файл.
    """
    app_name: str = "EngeeModelGeneratorAPI v0.1"

    ollama_model_name: str

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "base_collection"

    generation_timeout_seconds: int = 120

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str
    postgres_user: str
    postgres_password: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
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

    @property
    def generation_timeout(self) -> int:
        return self.generation_timeout_seconds

    @property
    def postgres_url(self) -> str | URL:
        return URL.create(
            "postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )

@lru_cache
def get_settings() -> Settings:
    return Settings()
