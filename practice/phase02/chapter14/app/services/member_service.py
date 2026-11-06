import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories import member_repository
from app.schemas import MemberCreate, MemberPatch, MemberUpdate

logger = logging.getLogger(__name__)


def _get_or_404(db: Session, member_id: int):
    member = member_repository.find_by_id(db, member_id)
    if member is None:
        # 처리 가능한 비정상 상황 = WARNING
        logger.warning("member not found: member_id=%s", member_id)
        raise HTTPException(status_code=404, detail="Member not found")
    return member


def get_members_service(db: Session):
    return member_repository.find_all(db)


def get_member_service(db: Session, member_id: int):
    logger.info("member lookup started: member_id=%s", member_id)
    return _get_or_404(db, member_id)


def create_member_service(db: Session, payload: MemberCreate):
    # 1차 방어: 미리 조회해서 중복이면 409
    existing = member_repository.find_by_email(db, str(payload.email))
    if existing is not None:
        logger.warning("duplicate email: email=%s", payload.email)
        raise HTTPException(status_code=409, detail="Email already exists")
    try:
        member = member_repository.create_member(
            db,
            payload.name,
            str(payload.email),
            payload.age,
        )
    except IntegrityError:
        # 최종 방어선: DB UNIQUE 제약 위반(동시 요청 등)도 409 로 번역
        logger.warning("duplicate email (db constraint): email=%s", payload.email)
        raise HTTPException(status_code=409, detail="Email already exists")
    logger.info("member created: member_id=%s", member.member_id)
    return member


def update_member_service(db: Session, member_id: int, payload: MemberUpdate):
    member = _get_or_404(db, member_id)
    try:
        updated = member_repository.update_member(db, member, payload)
    except IntegrityError:
        logger.warning("duplicate email on update: member_id=%s", member_id)
        raise HTTPException(status_code=409, detail="Email already exists")
    logger.info("member updated: member_id=%s", member_id)
    return updated


def patch_member_service(db: Session, member_id: int, payload: MemberPatch):
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        logger.warning("empty patch request: member_id=%s", member_id)
        raise HTTPException(status_code=400, detail="At least one field is required")
    member = _get_or_404(db, member_id)
    try:
        patched = member_repository.patch_member(db, member, payload)
    except IntegrityError:
        logger.warning("duplicate email on patch: member_id=%s", member_id)
        raise HTTPException(status_code=409, detail="Email already exists")
    # 값(비밀정보 가능성)은 남기지 않고 바뀐 필드 이름만 남긴다
    logger.info("member patched: member_id=%s fields=%s", member_id, sorted(changes))
    return patched


def delete_member_service(db: Session, member_id: int):
    member = _get_or_404(db, member_id)
    member_repository.delete_member(db, member)
    logger.info("member deleted: member_id=%s", member_id)
