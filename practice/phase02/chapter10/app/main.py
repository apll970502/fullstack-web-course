"""애플리케이션 조립만 담당한다."""
from fastapi import FastAPI

from app.routers import members

app = FastAPI(title="Chapter 10 - Layered Backend")
app.include_router(members.router)
