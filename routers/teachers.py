from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates 
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from database.database import get_db
from database.models import User
from schemas import TeacherAdd, TeacherResponse
from database.models import Teacher, Course
from .accounts import get_current_user,get_current_user_second
from services.teacher import *

router = APIRouter(prefix="/teachers", tags=["Teachers"])
templates = Jinja2Templates(directory="templates")

@router.get("/api", response_model=List[TeacherResponse])
def get_all_teachers(db: Session = Depends(get_db)):
    try:
        tea= get_teachers(db)
        return tea
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_class=HTMLResponse,include_in_schema=False)
def get_teachers_page(request: Request , db: Session = Depends(get_db)):
    try:
        tea= get_teachers(db)
        return templates.TemplateResponse(request=request, name="teachers/instructor.html",context={'tea':tea})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/add_teacher",response_class=HTMLResponse,include_in_schema=False)
def add_teacher_page(request: Request ,teacher: TeacherAdd, db: Session = Depends(get_db),user = Depends(get_current_user)):
        tea = add_teacher(teacher,db,user)
        return templates.TemplateResponse(request=request, name="teachers/add_teacher.html",context={'tea':tea})

@router.get("/choose_course/{id}",response_class=HTMLResponse,include_in_schema=False)
def choose_course_page(id : int,request: Request , db: Session = Depends(get_db)):
        tea = db.query(Teacher).filter(Teacher.id == id).first()
        crs = db.query(Course).all()       
        return templates.TemplateResponse(request=request, name="teachers/add_course_teacher.html",context={'tea':tea,'crs':crs})
    
@router.get("/update",response_class=HTMLResponse)
def update_teacher_page(request: Request ,id: int, teacher: TeacherAdd, db: Session = Depends(get_db),user = Depends(get_current_user),include_in_schema=False):
        tea = update_teacher(id,teacher,db,user)
        return templates.TemplateResponse(request=request, name="teachers/update_teacher.html",context={})

@router.get("/{id}",response_model=TeacherResponse)
def find_teacher(request: Request ,id: int, db: Session = Depends(get_db)):
    
    try:
        token = request.cookies.get("access_token")
        user_id= get_current_user_second(token)    
        user = db.query(User).filter(User.id == int(user_id)).first()
        print(user.role)    
        # user =request.user
        # print(user.id)
        tea = db.query(Teacher).filter(Teacher.id == id).first()
        if not tea:
            raise HTTPException(status_code=404, detail="Teacher not found")
        return templates.TemplateResponse(request=request, name="teachers/ins_details.html", context={"tea":tea,"user":user})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add_teacher", response_model=TeacherResponse)
def add_teacher(teacher: TeacherAdd, db: Session = Depends(get_db),user = Depends(get_current_user)):
    try:
        tea= add_teacher_service(teacher,db,user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{teacher_id}/course/{course_id}")
def select_course(teacher_id: int, course_id: int, db: Session = Depends(get_db),user = Depends(get_current_user)):
    try:
        tea = choose_course_service(teacher_id,course_id,db,user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id}", response_model=TeacherResponse)
def update_teacher(id: int, teacher: TeacherAdd, db: Session = Depends(get_db),user = Depends(get_current_user)):
    tea = update_teacher_service(id,teacher,db,user)
        
@router.delete("/delete/{id}")
def delete_teacher(id: int, db: Session = Depends(get_db),user = Depends(get_current_user)):
    try:
        message = delete_teacher_service(id,db,user)
        return message
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))