from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import TimeoutError
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging

from app.services.main_pipeline_with_RAG import MainPipeline


logger = logging.getLogger(__name__)
router = APIRouter()
main_pipeline = MainPipeline()

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
        script = future.result(timeout=40)
        logger.info(f"Generated script succeded")
    except TimeoutError:
        logger.warning(f"Generation timed out")
        raise HTTPException(status_code=504, detail="Model timeout")
    except Exception as e:
        logger.warning(f"Generation failed")
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

    return GenerateResponse(script=script)