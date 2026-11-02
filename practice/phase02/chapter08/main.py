import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field, model_validator

from common.db import get_connection

app = FastAPI(title="Chapter 08 - PUT/PATCH /members")


# ---------------------------------------------------------------
# Schema
#   MemberUpdate : PUT   - 수정 가능한 전체 필드를 요구
#   MemberPatch  : PATCH - 생략은 허용, 명시적 null 은 422
# ---------------------------------------------------------------
class MemberUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(ge=0, le=150)


class MemberPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    age: int | None = Field(default=None, ge=0, le=150)

    @model_validator(mode="after")
    def reject_explicit_null(self):
        # model_fields_set = 이번 요청에 실제로 들어온 필드 이름 목록
        for field in self.model_fields_set:
            if getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class MemberResponse(MemberUpdate):
    id: int


# ---------------------------------------------------------------
# DB 함수 (commit / rollback 은 endpoint 가 결정)
# ---------------------------------------------------------------
def to_dict(row) -> dict:
    return {"id": row[0], "name": row[1], "email": row[2], "age": row[3]}


def select_member(cursor, member_id: int) -> dict | None:
    cursor.execute(
        "SELECT id, name, email, age FROM members WHERE id = %s",
        (member_id,),
    )
    row = cursor.fetchone()
    return to_dict(row) if row else None


def email_taken_by_other(cursor, email: str, member_id: int) -> bool:
    """자기 자신은 제외하고 같은 이메일이 있는지 확인한다."""
    cursor.execute(
        "SELECT id FROM members WHERE email = %s AND id <> %s",
        (email, member_id),
    )
    return cursor.fetchone() is not None


def update_member_row(cursor, member_id: int, changes: dict) -> dict:
    """changes 에 들어 있는 컬럼만 UPDATE. 컬럼명은 허용 목록에서만 고른다."""
    allowed_fields = {"name": "name", "email": "email", "age": "age"}

    set_parts = []
    values = []
    for field, value in changes.items():
        set_parts.append(f"{allowed_fields[field]} = %s")  # 컬럼명: 허용 목록
        values.append(str(value) if field == "email" else value)  # 값: %s 파라미터
    values.append(member_id)

    cursor.execute(
        f"""
        UPDATE members
        SET {', '.join(set_parts)}
        WHERE id = %s
        RETURNING id, name, email, age
        """,
        values,
    )
    return to_dict(cursor.fetchone())


def apply_update(member_id: int, changes: dict) -> dict:
    """PUT / PATCH 공통: 존재(404) -> 이메일 중복(409) -> UPDATE -> commit."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            if select_member(cursor, member_id) is None:
                raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다.")

            if "email" in changes and email_taken_by_other(
                cursor, str(changes["email"]), member_id
            ):
                raise HTTPException(status_code=409, detail="이미 등록된 이메일입니다.")

            updated = update_member_row(cursor, member_id, changes)
            conn.commit()
            return updated
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        print("DB ERROR:", repr(e))
        raise HTTPException(status_code=500, detail="회원 수정 중 오류가 발생했습니다.")
    finally:
        conn.close()


# ---------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------
@app.get("/members/{member_id}", response_model=MemberResponse)
def get_member(member_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            member = select_member(cursor, member_id)
    finally:
        conn.close()

    if member is None:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다.")
    return member


@app.put("/members/{member_id}", response_model=MemberResponse)
def put_member(member_id: int, member: MemberUpdate):
    return apply_update(member_id, member.model_dump())


@app.patch("/members/{member_id}", response_model=MemberResponse)
def patch_member(member_id: int, member: MemberPatch):
    changes = member.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="수정할 필드가 하나도 없습니다.")
    return apply_update(member_id, changes)


# ---------------------------------------------------------------
# 독립 실습: PUT / PATCH /courses/{id}
#   중복 조건 = 같은 title + instructor (자기 자신 제외) -> 409
# ---------------------------------------------------------------
class CourseUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    instructor: str = Field(min_length=1, max_length=100)
    capacity: int = Field(gt=0, le=1000)


class CoursePatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    instructor: str | None = Field(default=None, min_length=1, max_length=100)
    capacity: int | None = Field(default=None, gt=0, le=1000)

    @model_validator(mode="after")
    def reject_explicit_null(self):
        for field in self.model_fields_set:
            if getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class CourseResponse(CourseUpdate):
    id: int


def course_to_dict(row) -> dict:
    return {"id": row[0], "title": row[1], "instructor": row[2], "capacity": row[3]}


def select_course(cursor, course_id: int) -> dict | None:
    cursor.execute(
        "SELECT id, title, instructor, capacity FROM courses WHERE id = %s",
        (course_id,),
    )
    row = cursor.fetchone()
    return course_to_dict(row) if row else None


def course_taken_by_other(cursor, title: str, instructor: str, course_id: int) -> bool:
    cursor.execute(
        "SELECT id FROM courses WHERE title = %s AND instructor = %s AND id <> %s",
        (title, instructor, course_id),
    )
    return cursor.fetchone() is not None


def update_course_row(cursor, course_id: int, changes: dict) -> dict:
    allowed_fields = {"title": "title", "instructor": "instructor", "capacity": "capacity"}
    set_parts = [f"{allowed_fields[f]} = %s" for f in changes]
    values = list(changes.values()) + [course_id]
    cursor.execute(
        f"""
        UPDATE courses
        SET {', '.join(set_parts)}
        WHERE id = %s
        RETURNING id, title, instructor, capacity
        """,
        values,
    )
    return course_to_dict(cursor.fetchone())


def apply_course_update(course_id: int, changes: dict) -> dict:
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            current = select_course(cursor, course_id)
            if current is None:
                raise HTTPException(status_code=404, detail="강좌를 찾을 수 없습니다.")

            # PATCH 는 안 보낸 값을 기존 값으로 채워 최종 title+instructor 로 중복 검사
            final_title = changes.get("title", current["title"])
            final_instructor = changes.get("instructor", current["instructor"])
            if course_taken_by_other(cursor, final_title, final_instructor, course_id):
                raise HTTPException(status_code=409, detail="이미 등록된 강좌입니다.")

            updated = update_course_row(cursor, course_id, changes)
            conn.commit()
            return updated
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        print("DB ERROR:", repr(e))
        raise HTTPException(status_code=500, detail="강좌 수정 중 오류가 발생했습니다.")
    finally:
        conn.close()


@app.get("/courses/{course_id}", response_model=CourseResponse)
def get_course(course_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            course = select_course(cursor, course_id)
    finally:
        conn.close()

    if course is None:
        raise HTTPException(status_code=404, detail="강좌를 찾을 수 없습니다.")
    return course


@app.put("/courses/{course_id}", response_model=CourseResponse)
def put_course(course_id: int, course: CourseUpdate):
    return apply_course_update(course_id, course.model_dump())


@app.patch("/courses/{course_id}", response_model=CourseResponse)
def patch_course(course_id: int, course: CoursePatch):
    changes = course.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="수정할 필드가 하나도 없습니다.")
    return apply_course_update(course_id, changes)
