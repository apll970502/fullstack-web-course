from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select

from app.db import SessionLocal
from app.models import Member

app = FastAPI(title="Chapter 11 - ORM 조회")


class MemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    member_id: int
    name: str
    email: str
    age: int


@app.get("/members", response_model=list[MemberResponse])
def get_members():
    with SessionLocal() as session:
        return session.scalars(select(Member).order_by(Member.member_id)).all()


@app.get("/members/{member_id}", response_model=MemberResponse)
def get_member(member_id: int):
    with SessionLocal() as session:
        member = session.scalar(select(Member).where(Member.member_id == member_id))
    if member is None:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다.")
    return member