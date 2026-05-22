import time
import uuid
from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import TimeoutError
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import logging

from app.db.repositories.requests import create_request, mark_request_error, mark_request_success
from app.db.session import get_db_session
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
def generate(request: GenerateRequest, db_session: Session = Depends(get_db_session)):
    logger.info("Generate request received")
    request_id = uuid.uuid4()
    create_request(db_session, request_id, request.prompt)
    start_time = time.monotonic()
    try:
        future = executor.submit(main_pipeline.generate_script, request.prompt)
        script = future.result(timeout=settings.generation_timeout)
        logger.info(f"Generated script succeded")
    except TimeoutError:
        duration = time.monotonic() - start_time
        logger.warning(f"Generation timeout after {settings.generation_timeout}s")
        mark_request_error(db_session, request_id, duration, "Generation Timeout", f"Generation timeout after {settings.generation_timeout}s")
        raise HTTPException(status_code=504, detail="Generation timeout")
    except Exception as e:
        duration = time.monotonic() - start_time
        logger.warning(f"Generation failed with error: {str(e)}")
        mark_request_error(db_session, request_id, duration, type(e).__name__, str(e))
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")
    else:
        duration = time.monotonic() - start_time
        mark_request_success(db_session, request_id, script, duration)

    return GenerateResponse(script=script)