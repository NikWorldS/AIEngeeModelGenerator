from fastapi import FastAPI

from dotenv import load_dotenv
from pathlib import Path

from app.core.logging_config import setup_logging


setup_logging()
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

from .routers import test_route
from .routers import script_generator


app = FastAPI()

app.include_router(test_route.router, prefix="/test")
app.include_router(script_generator.router, prefix="/script")


@app.get("/")
async def root():
    return {"message": "This is root page and nothing more"}
