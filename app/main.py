from fastapi import FastAPI

from app.core.logging_config import setup_logging

setup_logging()

from .routers import test_route
from .routers import script_generator


app = FastAPI()

app.include_router(test_route.router, prefix="/test")
app.include_router(script_generator.router, prefix="/script")


@app.get("/")
async def root():
    return {"message": "This is root page and nothing more"}
