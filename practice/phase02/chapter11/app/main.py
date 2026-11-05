from sqlalchemy import select

from app.db import SessionLocal
from app.models import Member

with SessionLocal() as session:
    # STEP 07: 전체 회원
    stmt = select(Member).order_by(Member.member_id)
    members = session.scalars(stmt).all()
    for member in members:
        print(member.member_id, member.name, member.email, member.age)

    # STEP 08: 1번 회원
    stmt = select(Member).where(Member.member_id == 1)
    member = session.scalar(stmt)
    print(member.name)
    print(member.email)

    # STEP 09: 없는 회원
    stmt = select(Member).where(Member.member_id == 999999)
    member = session.scalar(stmt)
    print(member)