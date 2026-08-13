from fastapi import FastAPI,Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from routers import accounts, courses, students, teachers
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.middleware.sessions import SessionMiddleware
from starlette.applications import Starlette
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
from fastapi.staticfiles import StaticFiles
# from core.middleware import BasicAuthBackend
# from celery_worker import write_log_celery

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")


app = FastAPI()

templates = Jinja2Templates(directory="templates/home/")



app.add_middleware(SessionMiddleware,secret_key=SECRET_KEY)

# app.add_middleware(AuthenticationMiddleware, backend=BasicAuthBackend())

app.mount("/assets", StaticFiles(directory="assets"),name="assets")



@app.get("/",response_class=HTMLResponse)
def home(request:Request):
     return templates.TemplateResponse(request=request, name="index2.html")

@app.get("/about",response_class=HTMLResponse)
def about(request:Request):
     return templates.TemplateResponse(request=request, name="about.html")

app.include_router(courses.router,  prefix="/cms")
app.include_router(students.router, prefix="/cms")
app.include_router(teachers.router, prefix="/cms")
app.include_router(accounts.router, prefix="/cms")





