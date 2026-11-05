import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Member
from app.schemas import MemberPatch, MemberUpdate

logger = logging.getLogger(__name__)


def _log_failure(action: str, error: Exception) -> None:
    """예상된 제약 위반은 WARNING, 예상 못한 오류는 Stack Trace 까지 남긴다."""
    if isinstance(error, IntegrityError):
        logger.warning("integrity error while %s", action)
    else:
        logger.exception("unexpected error while %s", action)


def find_all(db: Session):
    stmt = select(Member).order_by(Member.member_id)
    return db.scalars(stmt).all()


def find_by_id(db: Session, member_id: int):
    return db.get(Member, member_id)


def create_member(db: Session, name: str, email: str, age: int):
    member = Member(name=name, email=email, age=age)
    try:
        db.add(member)
        db.commit()
        db.refresh(member)
        return member
    except Exception as e:
        db.rollback()
        _log_failure("creating member", e)
        raise


def find_by_email(db: Session, email: str):
    stmt = select(Member).where(Member.email == email)
    return db.scalar(stmt)


def update_member(db: Session, member: Member, payload: MemberUpdate):
    member.name = payload.name
    member.email = str(payload.email)
    member.age = payload.age
    try:
        db.commit()
        db.refresh(member)
        return member
    except Exception as e:
        db.rollback()
        _log_failure("updating member", e)
        raise


def patch_member(db: Session, member: Member, payload: MemberPatch):
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        if field == "email":
            value = str(value)
        setattr(member, field, value)
    try:
        db.commit()
        db.refresh(member)
        return member
    except Exception as e:
        db.rollback()
        _log_failure("patching member", e)
        raise


def delete_member(db: Session, member: Member):
    try:
        db.delete(member)
        db.commit()
    except Exception as e:
        db.rollback()
        _log_failure("deleting member", e)
        raise
