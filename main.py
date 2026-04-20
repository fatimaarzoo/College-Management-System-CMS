from fastapi import FastAPI
from routers import courses, students, teachers

app = FastAPI()


app.include_router(courses.router,  prefix="/cms")
app.include_router(students.router, prefix="/cms")
app.include_router(teachers.router, prefix="/cms")

