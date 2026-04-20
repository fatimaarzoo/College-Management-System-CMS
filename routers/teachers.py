from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from database import get_db
from schemas import TeacherAdd, TeacherResponse
from models import Teacher, Course

router = APIRouter(prefix="/teachers", tags=["Teachers"])

@router.get("/", response_model=List[TeacherResponse])
def get_teachers(db: Session = Depends(get_db)):
    try:
        tea = db.query(Teacher).order_by(Teacher.id.desc()).all()
        if not tea:
            raise HTTPException(status_code=404, detail="No teachers found")
        return tea
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}", response_model=TeacherResponse)
def find_teacher(id: int, db: Session = Depends(get_db)):
    try:
        tea = db.query(Teacher).filter(Teacher.id == id).first()
        if not tea:
            raise HTTPException(status_code=404, detail="Teacher not found")
        return tea
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=TeacherResponse)
def add_teacher(teacher: TeacherAdd, db: Session = Depends(get_db)):
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
def choose_course(teacher_id: int, course_id: int, db: Session = Depends(get_db)):
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
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id}", response_model=TeacherResponse)
def update_teacher(id: int, teacher: TeacherAdd, db: Session = Depends(get_db)):
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

@router.delete("/{id}")
def delete_teacher(id: int, db: Session = Depends(get_db)):
    try:
        tea = db.query(Teacher).filter(Teacher.id == id).first()
        if tea is None:
            return {"message": "Teacher not found"}
        db.delete(tea)
        db.commit()
        return {"message": f"Teacher with id {id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))