"""DB 접근만 담당한다. HTTP(HTTPException 등)는 모른다."""
from psycopg.rows import dict_row

from app.db import get_connection

COLUMNS = "id, name, email, age"


def find_all() -> list[dict]:
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(f"SELECT {COLUMNS} FROM members ORDER BY id")
            return cur.fetchall()


def find_by_id(member_id: int) -> dict | None:
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"SELECT {COLUMNS} FROM members WHERE id = %s",
                (member_id,),
            )
            return cur.fetchone()


def exists_by_email(email: str, exclude_member_id: int | None = None) -> bool:
    """exclude_member_id 가 있으면 그 회원(자기 자신)은 제외하고 검사한다."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            if exclude_member_id is None:
                cur.execute("SELECT 1 FROM members WHERE email = %s", (email,))
            else:
                cur.execute(
                    "SELECT 1 FROM members WHERE email = %s AND id <> %s",
                    (email, exclude_member_id),
                )
            return cur.fetchone() is not None


def create(data) -> dict:
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"""
                INSERT INTO members (name, email, age)
                VALUES (%s, %s, %s)
                RETURNING {COLUMNS}
                """,
                (data.name, str(data.email), data.age),
            )
            return cur.fetchone()  # with 블록이 정상 종료되면 commit


def update(member_id: int, changes: dict) -> dict | None:
    """changes 에 있는 컬럼만 UPDATE. 컬럼명은 허용 목록에서만 고른다."""
    allowed_fields = {"name": "name", "email": "email", "age": "age"}
    set_parts = []
    values = []
    for field, value in changes.items():
        set_parts.append(f"{allowed_fields[field]} = %s")
        values.append(str(value) if field == "email" else value)
    values.append(member_id)

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"""
                UPDATE members
                SET {', '.join(set_parts)}
                WHERE id = %s
                RETURNING {COLUMNS}
                """,
                values,
            )
            return cur.fetchone()


def delete(member_id: int) -> dict | None:
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"DELETE FROM members WHERE id = %s RETURNING {COLUMNS}",
                (member_id,),
            )
            return cur.fetchone()
