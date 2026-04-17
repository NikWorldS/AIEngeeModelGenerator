from fastapi import APIRouter

router = APIRouter()

@router.get("/useless_endpoint")
async def useless_endpoint():
    return {"message": "This is just useless page and nothing more"}