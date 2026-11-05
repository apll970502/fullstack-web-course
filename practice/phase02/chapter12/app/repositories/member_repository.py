from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Member
from app.schemas import MemberPatch, MemberUpdate


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
    except Exception:
        db.rollback()
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
    except Exception:
        db.rollback()
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
    except Exception:
        db.rollback()
        raise


def delete_member(db: Session, member: Member):
    try:
        db.delete(member)
        db.commit()
    except Exception:
        db.rollback()
        raise