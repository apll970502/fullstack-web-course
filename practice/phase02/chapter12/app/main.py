from fastapi import FastAPI

from app.routers import member_router

app = FastAPI(title="Chapter 12 - ORM CRUD")
app.include_router(member_router.router)
