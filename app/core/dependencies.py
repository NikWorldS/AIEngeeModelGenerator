from concurrent.futures import Executor

from fastapi import Request
from qdrant_client import QdrantClient

from app.services.main_pipeline_with_RAG import MainPipeline


def get_qdrant_client(request: Request) -> QdrantClient:
    return request.app.state.context.qdrant_client

def get_pipeline(request: Request) -> MainPipeline:
    return request.app.state.context.pipeline

def get_executor(request: Request) -> Executor:
    return request.app.state.context.executor