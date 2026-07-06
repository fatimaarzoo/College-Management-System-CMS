from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates 
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from database.database import get_db
from schemas import TeacherAdd, TeacherResponse
from database.models import Teacher, Course
from .accounts import get_current_user

router = APIRouter(prefix="/teachers", tags=["Teachers"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_model=List[TeacherResponse])
def get_teachers(request: Request , db: Session = Depends(get_db)):
    try:
        tea = db.query(Teacher).order_by(Teacher.id.desc()).all()
        if not tea:
            raise HTTPException(status_code=404, detail="No teachers found")
        # return HTMLResponse()
        return templates.TemplateResponse(request=request, name="teachers/instructor.html", context={"tea":tea})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/add_teacher",response_class=HTMLResponse)
def add_teacher_page(request: Request , db: Session = Depends(get_db)):
        return templates.TemplateResponse(request=request, name="teachers/add_teacher.html",context={})

@router.get("/choose_course/{id}",response_class=HTMLResponse)
def choose_course_page(id : int,request: Request , db: Session = Depends(get_db)):
        tea = db.query(Teacher).filter(Teacher.id == id).first()
        crs = db.query(Course).all()       
        return templates.TemplateResponse(request=request, name="teachers/add_course_teacher.html",context={'tea':tea,'crs':crs})
    
@router.get("/update",response_class=HTMLResponse)
def update_teacher_page(request: Request , db: Session = Depends(get_db)):
        return templates.TemplateResponse(request=request, name="teachers/update_teacher.html",context={})

@router.get("/{id}",response_model=TeacherResponse)
def find_teacher(request: Request ,id: int, db: Session = Depends(get_db)):
    try:
        tea = db.query(Teacher).filter(Teacher.id == id).first()
        if not tea:
            raise HTTPException(status_code=404, detail="Teacher not found")
        return templates.TemplateResponse(request=request, name="teachers/ins_details.html", context={"tea":tea})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add_teacher", response_model=TeacherResponse)
def add_teacher(teacher: TeacherAdd, db: Session = Depends(get_db),user = Depends(get_current_user)):
    try:
        tea = Teacher(
            name=teacher.name,
            subject=teacher.subject,
            email=teacher.email,
            contact=teacher.contact,
        )
        db.add(tea)
        db.commit()
        db.refresh(tea)
        return tea
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{teacher_id}/course/{course_id}")
def choose_course(request:Request ,teacher_id: int, course_id: int, db: Session = Depends(get_db),user = Depends(get_current_user)):
    try:
        tea = db.get(Teacher, teacher_id)
        crs = db.get(Course, course_id)
        if not tea:
            return {"message": "Teacher not found"}
        if not crs:
            return {"message": "Course not found"}
        if crs.incharge_id is not None:
            return {"message": "A teacher is already teaching the course"}
        if crs not in tea.courses:
            tea.courses.append(crs)
            crs.incharge_id = teacher_id
            tea.tea_courses.append(crs)
            db.commit()
        return {"teacher_id": tea.id, "course_ids": [c.id for c in tea.courses]}
        # return templates.TemplateResponse(request=request, name="teachers/add_course_teacher.html", context={"tea":tea})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id}", response_model=TeacherResponse)
def update_teacher(id: int, teacher: TeacherAdd, db: Session = Depends(get_db),user = Depends(get_current_user)):
    try:
        tea = db.query(Teacher).filter(Teacher.id == id).first()
        if tea is None:
            return {"message": "Teacher not found"}
        tea.name        = teacher.name
        tea.subject     = teacher.subject
        tea.email       = teacher.email
        tea.contact     = teacher.contact
        tea.joined_date = teacher.joined_date
        db.commit()
        db.refresh(tea)
        return TeacherResponse.model_validate(tea)
    except (ValueError, IntegrityError) as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{id}")
def delete_teacher(id: int, db: Session = Depends(get_db),user = Depends(get_current_user)):
    try:
        tea = db.query(Teacher).filter(Teacher.id == id).first()
        if tea is None:
            return {"message": "Teacher not found"}
        db.delete(tea)
        db.commit()
        return {"message": f"Teacher with id {id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
