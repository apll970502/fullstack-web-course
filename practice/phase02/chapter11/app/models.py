"""실제 PostgreSQL public.members 구조를 그대로 옮긴 Model.

실제 구조 (information_schema 로 확인):
  id integer PK NOT NULL / name varchar(50) NOT NULL / email varchar(100) UNIQUE NOT NULL
  age integer NULL / joined_at date NULL
"""
from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    joined_at: Mapped[date | None] = mapped_column(Date, nullable=True)
