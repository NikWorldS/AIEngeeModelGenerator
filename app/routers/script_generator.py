from concurrent.futures.thread import ThreadPoolExecutor
from fastapi import APIRouter, HTTPException
from grpc import FutureTimeoutError
from pydantic import BaseModel, Field

from app.services.main_pipeline_with_RAG import MainPipeline


router = APIRouter()
main_pipeline = MainPipeline()

executor = ThreadPoolExecutor(max_workers=2)

class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=2000)

class GenerateResponse(BaseModel):
    script: str

@router.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest):
    try:
        future = executor.submit(main_pipeline.generate_script, request.prompt)
        script = future.result(timeout=40)
    except FutureTimeoutError:
        raise HTTPException(status_code=504, detail="Model timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

    return GenerateResponse(script=script)