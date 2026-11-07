from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Translation

Lang = Literal["en", "te"]


def text_map(db: Session, entity_type: str, ids: list[int], lang: str) -> dict[tuple[int, str], str]:
    """{(record id, field): translated text}. Anything missing simply stays in English."""
    if lang == "en" or not ids:
        return {}
    rows = db.execute(
        select(Translation.entity_id, Translation.field, Translation.text).where(
            Translation.entity_type == entity_type, Translation.entity_id.in_(ids), Translation.language == lang
        )
    )
    return {(entity_id, field): text for entity_id, field, text in rows}
