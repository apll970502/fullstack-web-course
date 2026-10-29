from fastapi import FastAPI

app = FastAPI()

members = [
    {"id": 1, "name": "Kim", "email": "kim@example.com"},
    {"id": 2, "name": "Lee", "email": "lee@example.com"},
]


courses = [
    {"id": 1, "title": "Database", "instructor": "Kim"},
    {"id": 2, "title": "Frontend", "instructor": "Lee"},
    {"id": 3, "title": "Backend", "instructor": "Park"},
]


@app.get("/")
def read_root():
    return {"message": "Hello FastAPI"}


@app.get("/members")
def read_members():
    return members


@app.get("/courses")
def read_courses():
    return courses
