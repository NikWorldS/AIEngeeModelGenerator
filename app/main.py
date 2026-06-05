from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.logging_config import setup_logging

setup_logging()

from app.routers import test_route
from app.routers import script_generator
from app.core.setup.app_context import build_app_context, shutdown_app_context


@asynccontextmanager
async def lifespan(app: FastAPI):
    context = build_app_context()
    app.state.context = context
    try:
        yield
    finally:
        shutdown_app_context(context)

app = FastAPI(lifespan=lifespan)

app.include_router(test_route.router, prefix="/test")
app.include_router(script_generator.router, prefix="/script")


@app.get("/")
async def root():
    return {"message": "This is root page and nothing more"}
