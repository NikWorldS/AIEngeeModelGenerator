import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.requests import Request


def create_request(
    session: Session,
    request_id: uuid.UUID,
    request_text: str,
) -> Request:
    """
    Создаёт запись о запросе.
    :param session: Session, сессия db
    :param request_id: UUID, id в формате uuid
    :param request_text: str, текст запроса
    :return: Request
    """
    request = Request(
        request_id=request_id,
        request_text=request_text,
        status="pending",
    )
    session.add(request)
    session.commit()
    session.refresh(request)
    return request


def mark_request_error(
    session: Session,
    request_id: uuid.UUID,
    duration: float,
    error_type: str,
    error_message: str,
) -> Request | None:
    """
    Изменяет статус запроса (по request_id) на `error`.
    :param session: Session, сессия db
    :param request_id: UUID, id в формате uuid
    :param duration: float, длительность обработки запроса
    :param error_type: str, тип (или заголовок) ошибки
    :param error_message: str, сообщение ошибки
    :return: Request
    """
    request = _get_request_by_request_id(session, request_id)
    if request is None:
        return None

    request.duration = duration
    request.response_text = None
    request.error_type = error_type
    request.error_message = error_message
    request.status = "error"
    session.commit()
    session.refresh(request)
    return request


def mark_request_success(
    session: Session,
    request_id: uuid.UUID,
    response_text: str,
    duration: float,
) -> Request | None:
    """
    Изменяет статус запроса (по request_id) на `success`.
    :param session: Session, сессия db
    :param request_id: UUID, id в формате uuid
    :param response_text: str, текст ответа
    :param duration: float, длительность обработки
    :return: Request
    """
    request = _get_request_by_request_id(session, request_id)
    if request is None:
        return None

    request.response_text = response_text
    request.duration = duration
    request.error_type = None
    request.error_message = None
    request.status = "success"
    session.commit()
    session.refresh(request)
    return request


def _get_request_by_request_id(session: Session, request_id: uuid.UUID) -> Request | None:
    return session.scalar(select(Request).where(Request.request_id == request_id))
