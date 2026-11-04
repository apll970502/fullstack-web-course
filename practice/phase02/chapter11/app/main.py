"""ORM 조회 연습: python -m app.main  (chapter11 폴더에서 실행)"""
from sqlalchemy import select, text

from app.db import SessionLocal
from app.models import Member


def show(m: Member | None) -> None:
    print(None if m is None else (m.id, m.name, m.email, m.age))


with SessionLocal() as session:
    print("\n=== 1) 전체 회원 ===")
    for m in session.scalars(select(Member).order_by(Member.id)).all():
        show(m)

    print("\n=== 2) id=11 조회 (ORM) ===")
    orm_member = session.scalar(select(Member).where(Member.id == 11))
    show(orm_member)

    print("\n=== 3) 같은 조회 (Raw SQL) ===")
    raw = session.execute(
        text("SELECT id, name, email, age FROM members WHERE id = :id"), {"id": 11}
    ).one()
    print(tuple(raw))
    same = orm_member is not None and tuple(raw) == (
        orm_member.id, orm_member.name, orm_member.email, orm_member.age
    )
    print("Raw SQL == ORM Object:", same)

    print("\n=== 4) 없는 회원 (id=999999) ===")
    show(session.scalar(select(Member).where(Member.id == 999999)))
