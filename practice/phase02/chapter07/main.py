import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field

from common.db import get_connection

app = FastAPI(title="Chapter 07 - POST /members")


# ---------------------------------------------------------------
# Members: 입력/출력 모델
# ---------------------------------------------------------------
class MemberCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(ge=0, le=150)


class MemberResponse(MemberCreate):
    id: int


# ---------------------------------------------------------------
# Members: DB 함수 (SQL 은 여기에만 둔다)
#   - cursor 를 받아서 실행만 한다.
#   - commit / rollback 은 호출한 endpoint 가 결정한다. (Transaction 경계)
# ---------------------------------------------------------------
def email_exists(cursor, email: str) -> bool:
    cursor.execute("SELECT member_id FROM members WHERE email = %s", (email,))
    return cursor.fetchone() is not None


def insert_member(cursor, member: MemberCreate) -> dict:
    """parameterized INSERT + RETURNING. 생성된 row 를 dict 로 반환한다."""
    cursor.execute(
        """
        INSERT INTO members (name, email, age)
        VALUES (%s, %s, %s)
        RETURNING member_id AS id, name, email, age
        """,
        (member.name, member.email, member.age),
    )
    row = cursor.fetchone()
    return {"id": row[0], "name": row[1], "email": row[2], "age": row[3]}


def select_member(cursor, member_id: int) -> dict | None:
    cursor.execute(
        "SELECT member_id AS id, name, email, age FROM members WHERE member_id = %s",
        (member_id,),
    )
    row = cursor.fetchone()
    if row is None:
        return None
    return {"id": row[0], "name": row[1], "email": row[2], "age": row[3]}


# ---------------------------------------------------------------
# Members: Endpoint
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


@app.post("/members", response_model=MemberResponse, status_code=201)
def create_member(member: MemberCreate):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 1) 중복 이메일 확인 -> 409
            if email_exists(cursor, member.email):
                raise HTTPException(status_code=409, detail="이미 등록된 이메일입니다.")

            # 2) INSERT
            created = insert_member(cursor, member)

            # 3) 성공했을 때만 확정
            conn.commit()

            return created
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        print("DB ERROR:", repr(e))  # Uvicorn 로그에서 원인 확인용
        raise HTTPException(status_code=500, detail="회원 등록 중 오류가 발생했습니다.")
    finally:
        conn.close()


# ---------------------------------------------------------------
# 혼자 해보기: POST /courses  (중복 조건 = 같은 title + instructor)
# ---------------------------------------------------------------
class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    instructor: str = Field(min_length=1, max_length=100)
    capacity: int = Field(gt=0, le=1000)


class CourseResponse(CourseCreate):
    id: int


def course_exists(cursor, title: str, instructor: str) -> bool:
    cursor.execute(
        "SELECT id FROM courses WHERE title = %s AND instructor = %s",
        (title, instructor),
    )
    return cursor.fetchone() is not None


def insert_course(cursor, course: CourseCreate) -> dict:
    cursor.execute(
        """
        INSERT INTO courses (title, instructor, capacity)
        VALUES (%s, %s, %s)
        RETURNING id, title, instructor, capacity
        """,
        (course.title, course.instructor, course.capacity),
    )
    row = cursor.fetchone()
    return {"id": row[0], "title": row[1], "instructor": row[2], "capacity": row[3]}


def select_course(cursor, course_id: int) -> dict | None:
    cursor.execute(
        "SELECT id, title, instructor, capacity FROM courses WHERE id = %s",
        (course_id,),
    )
    row = cursor.fetchone()
    if row is None:
        return None
    return {"id": row[0], "title": row[1], "instructor": row[2], "capacity": row[3]}


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


@app.post("/courses", response_model=CourseResponse, status_code=201)
def create_course(course: CourseCreate):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            if course_exists(cursor, course.title, course.instructor):
                raise HTTPException(status_code=409, detail="이미 등록된 강좌입니다.")

            created = insert_course(cursor, course)
            conn.commit()
            return created
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        print("DB ERROR:", repr(e))
        raise HTTPException(status_code=500, detail="강좌 등록 중 오류가 발생했습니다.")
    finally:
        conn.close()
