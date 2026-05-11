from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import TimeoutError
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging

from app.services.main_pipeline_with_RAG import MainPipeline
from app.core.config import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()
main_pipeline = MainPipeline(settings)


executor = ThreadPoolExecutor(max_workers=2)

class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=2000)

class GenerateResponse(BaseModel):
    script: str

@router.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest):
    logger.info("Generate request received")
    try:
        future = executor.submit(main_pipeline.generate_script, request.prompt)
        script = future.result(timeout=settings.generation_timeout)
        logger.info(f"Generated script succeded")
    except TimeoutError:
        logger.warning(f"Generation timeout after {settings.generation_timeout}s")
        raise HTTPException(status_code=504, detail="Generation timeout")
    except Exception as e:
        logger.warning(f"Generation failed with error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

    return GenerateResponse(script=script)