from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories import member_repository
from app.schemas import MemberCreate, MemberPatch, MemberUpdate


def _get_or_404(db: Session, member_id: int):
    member = member_repository.find_by_id(db, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


def get_members_service(db: Session):
    return member_repository.find_all(db)


def get_member_service(db: Session, member_id: int):
    return _get_or_404(db, member_id)


def create_member_service(db: Session, payload: MemberCreate):
    # 1차 방어: 미리 조회해서 중복이면 409
    existing = member_repository.find_by_email(db, str(payload.email))
    if existing is not None:
        raise HTTPException(status_code=409, detail="Email already exists")
    try:
        return member_repository.create_member(
            db,
            payload.name,
            str(payload.email),
            payload.age,
        )
    except IntegrityError:
        # 최종 방어선: DB UNIQUE 제약 위반(동시 요청 등)도 409 로 번역
        raise HTTPException(status_code=409, detail="Email already exists")


def update_member_service(db: Session, member_id: int, payload: MemberUpdate):
    member = _get_or_404(db, member_id)
    try:
        return member_repository.update_member(db, member, payload)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Email already exists")


def patch_member_service(db: Session, member_id: int, payload: MemberPatch):
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="At least one field is required")
    member = _get_or_404(db, member_id)
    try:
        return member_repository.patch_member(db, member, payload)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Email already exists")


def delete_member_service(db: Session, member_id: int):
    member = _get_or_404(db, member_id)
    member_repository.delete_member(db, member)
