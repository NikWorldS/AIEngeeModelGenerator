from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from qdrant_client import QdrantClient

from app.core.config import get_settings
from app.services.main_pipeline_with_RAG import MainPipeline
from app.vector_db.client import create_qdrant_client
from app.vector_db.qdrant_restore import QdrantRestore
from app.vector_db.retriever import QdrantRetriever
from app.vector_db.qdrant_bootstrap import QdrantBootstrap


@dataclass
class AppContext:
    qdrant_client: QdrantClient
    pipeline: MainPipeline
    executor: ThreadPoolExecutor

def build_app_context() -> AppContext:
    settings = get_settings()

    qdrant_client = create_qdrant_client()

    restore_service = QdrantRestore(
        client=qdrant_client,
        collection_name=settings.qdrant_collection_name,
    )

    qdrant_bootstrap = QdrantBootstrap(
        client=qdrant_client,
        restore_service=restore_service,
        collection_name=settings.qdrant_collection_name,
    )
    qdrant_bootstrap.ensure_ready()

    retriever = QdrantRetriever(
        client=qdrant_client,
        collection_name=settings.qdrant_collection_name,
    )

    executor = ThreadPoolExecutor(max_workers=2)

    pipeline = MainPipeline(
        settings=settings,
        retriever=retriever,
    )

    return AppContext(
        qdrant_client,
        pipeline,
        executor,
    )

def shutdown_app_context(context: AppContext):
    context.executor.shutdown(wait=False, cancel_futures=True)
    context.qdrant_client.close()
    raise