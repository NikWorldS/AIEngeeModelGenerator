from qdrant_client import QdrantClient

from app.core.config import get_settings


settings = get_settings()

qdrant_local_client = QdrantClient(
    url=settings.qdrant_url,
)

def get_qdrant_client() -> QdrantClient:
    return qdrant_local_client