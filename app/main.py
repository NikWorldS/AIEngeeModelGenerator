from fastapi import FastAPI

from .routers import test_route


app = FastAPI()

app.include_router(test_route.router, prefix="/test")


@app.get("/")
async def root():
    return {"message": "This is root page and nothing more"}


