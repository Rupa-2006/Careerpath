from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import Db
from app.models import Region, Stream, Subject
from app.schemas import RegionOut, StreamOut, SubjectOut

router = APIRouter(prefix="/reference", tags=["reference"])


@router.get("/states", response_model=list[RegionOut])
def states(db: Db):
    return db.scalars(select(Region).order_by(Region.name)).all()


@router.get("/streams", response_model=list[StreamOut])
def streams(db: Db):
    return db.scalars(select(Stream).options(selectinload(Stream.subjects)).order_by(Stream.sort_order)).all()


@router.get("/subjects", response_model=list[SubjectOut])
def subjects(db: Db):
    return db.scalars(select(Subject).order_by(Subject.name)).all()
