"""업무 규칙(존재 확인, 중복 검사, 빈 PATCH)을 담당한다. SQL 은 모른다."""
from fastapi import HTTPException

from app.repositories import member_repository


def _get_or_404(member_id: int) -> dict:
    member = member_repository.find_by_id(member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다.")
    return member


def get_members() -> list[dict]:
    return member_repository.find_all()


def get_member(member_id: int) -> dict:
    return _get_or_404(member_id)


def create_member(data) -> dict:
    if member_repository.exists_by_email(str(data.email)):
        raise HTTPException(status_code=409, detail="이미 등록된 이메일입니다.")
    return member_repository.create(data)


def replace_member(member_id: int, data) -> dict:
    return _update(member_id, data.model_dump())


def patch_member(member_id: int, data) -> dict:
    changes = data.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="수정할 필드가 하나도 없습니다.")
    return _update(member_id, changes)


def _update(member_id: int, changes: dict) -> dict:
    _get_or_404(member_id)
    if "email" in changes and member_repository.exists_by_email(
        str(changes["email"]), exclude_member_id=member_id
    ):
        raise HTTPException(status_code=409, detail="이미 등록된 이메일입니다.")
    return member_repository.update(member_id, changes)


def delete_member(member_id: int) -> None:
    if member_repository.delete(member_id) is None:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다.")
