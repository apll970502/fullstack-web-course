"""HTTP 입구. URL / Method / Schema / Status Code 만 다룬다."""
from fastapi import APIRouter, Response, status

from app.schemas import MemberCreate, MemberPatch, MemberResponse, MemberUpdate
from app.services import member_service

router = APIRouter(prefix="/members", tags=["members"])


@router.get("", response_model=list[MemberResponse])
def get_members():
    return member_service.get_members()


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(member_id: int):
    return member_service.get_member(member_id)


@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(member: MemberCreate):
    return member_service.create_member(member)


@router.put("/{member_id}", response_model=MemberResponse)
def put_member(member_id: int, member: MemberUpdate):
    return member_service.replace_member(member_id, member)


@router.patch("/{member_id}", response_model=MemberResponse)
def patch_member(member_id: int, member: MemberPatch):
    return member_service.patch_member(member_id, member)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int):
    member_service.delete_member(member_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
