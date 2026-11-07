from datetime import timedelta

from fastapi import APIRouter, HTTPException, Request, status

from app.api.auth import client_ip
from app.api.catalog import student_subjects
from app.api.deps import Db
from app.assistant import Student, answer
from app.assistant_ai import reword
from app.core.security import is_rate_limited, key_for, record_event
from app.schemas import AssistantIn, AssistantOut

router = APIRouter(tags=["assistant"])

MESSAGES_PER_HOUR = 60
WINDOW = timedelta(hours=1)


@router.post("/assistant/messages", response_model=AssistantOut)
def message(data: AssistantIn, request: Request, db: Db) -> AssistantOut:
    """Nothing the student types is saved: the chat lives only in their open page."""
    key = key_for("assistant", client_ip(request))
    if is_rate_limited(db, key, MESSAGES_PER_HOUR, WINDOW):
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "That's a lot of questions for one hour. Please try again later.")
    record_event(db, key)

    subjects = ",".join(str(item) for item in data.subject_ids)
    student = Student(student_subjects(db, data.stream_id, subjects), data.region_id)
    reply = answer(db, data.message, student, data.lang)
    used_ai = reword(data.message, reply)
    return AssistantOut(
        intent=reply.intent, text=reply.text, cards=reply.cards, next_questions=reply.next_questions, used_ai=used_ai,
    )
