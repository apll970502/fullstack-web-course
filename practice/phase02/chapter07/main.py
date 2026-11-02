import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field

from common.db import get_connection

app = FastAPI(title="Chapter 07 - POST /members")


class MemberCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(ge=0, le=150)


class MemberResponse(MemberCreate):
    id: int


@app.get("/members/{member_id}", response_model=MemberResponse)
def get_member(member_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT member_id AS id, name, email, age "
                "FROM members WHERE member_id = %s",
                (member_id,),
            )
            row = cursor.fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다.")
    return {"id": row[0], "name": row[1], "email": row[2], "age": row[3]}


@app.post("/members", response_model=MemberResponse, status_code=201)
def create_member(member: MemberCreate):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 1) 중복 이메일 확인 -> 409
            cursor.execute(
                "SELECT member_id FROM members WHERE email = %s",
                (member.email,),
            )
            if cursor.fetchone():
                raise HTTPException(status_code=409, detail="이미 등록된 이메일입니다.")

            # 2) parameterized INSERT + RETURNING
            cursor.execute(
                """
                INSERT INTO members (name, email, age)
                VALUES (%s, %s, %s)
                RETURNING member_id AS id, name, email, age
                """,
                (member.name, member.email, member.age),
            )
            row = cursor.fetchone()

            # 3) 성공했을 때만 확정
            conn.commit()

            return {"id": row[0], "name": row[1], "email": row[2], "age": row[3]}
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


@app.get("/courses/{course_id}", response_model=CourseResponse)
def get_course(course_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, instructor, capacity FROM courses WHERE id = %s",
                (course_id,),
            )
            row = cursor.fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="강좌를 찾을 수 없습니다.")
    return {"id": row[0], "title": row[1], "instructor": row[2], "capacity": row[3]}


@app.post("/courses", response_model=CourseResponse, status_code=201)
def create_course(course: CourseCreate):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 1) 중복 강좌(같은 제목 + 같은 강사) 확인 -> 409
            cursor.execute(
                "SELECT id FROM courses WHERE title = %s AND instructor = %s",
                (course.title, course.instructor),
            )
            if cursor.fetchone():
                raise HTTPException(status_code=409, detail="이미 등록된 강좌입니다.")

            # 2) parameterized INSERT + RETURNING
            cursor.execute(
                """
                INSERT INTO courses (title, instructor, capacity)
                VALUES (%s, %s, %s)
                RETURNING id, title, instructor, capacity
                """,
                (course.title, course.instructor, course.capacity),
            )
            row = cursor.fetchone()

            # 3) 성공했을 때만 확정
            conn.commit()

            return {"id": row[0], "title": row[1], "instructor": row[2], "capacity": row[3]}
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        print("DB ERROR:", repr(e))
        raise HTTPException(status_code=500, detail="강좌 등록 중 오류가 발생했습니다.")
    finally:
        conn.close()
