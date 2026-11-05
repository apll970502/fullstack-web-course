from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import MemberCreate, MemberPatch, MemberResponse, MemberUpdate
from app.services import member_service

router = APIRouter(prefix="/members", tags=["members"])


@router.get("", response_model=list[MemberResponse])
def get_members(db: Session = Depends(get_db)):
    return member_service.get_members_service(db)


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(member_id: int, db: Session = Depends(get_db)):
    return member_service.get_member_service(db, member_id)


@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(payload: MemberCreate, db: Session = Depends(get_db)):
    return member_service.create_member_service(db, payload)


@router.put("/{member_id}", response_model=MemberResponse)
def update_member(member_id: int, payload: MemberUpdate, db: Session = Depends(get_db)):
    return member_service.update_member_service(db, member_id, payload)


@router.patch("/{member_id}", response_model=MemberResponse)
def patch_member(member_id: int, payload: MemberPatch, db: Session = Depends(get_db)):
    return member_service.patch_member_service(db, member_id, payload)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, db: Session = Depends(get_db)):
    member_service.delete_member_service(db, member_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
