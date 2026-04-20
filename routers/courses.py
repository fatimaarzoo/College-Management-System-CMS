from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import RequestValidationError
from database import get_db
from schemas import CourseAdd, CourseUpdate, CourseResponse
from models import Course, Teacher
from pydantic import PositiveInt
from typing import List

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("/",response_model=List[CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    try:
        crs = db.query(Course).order_by(Course.id.desc()).all()
        if not crs:
            return {"message":"Sorry! Courses not found"}
        return crs
    except Exception:
        raise HTTPException(status_code=500, detail="Sorry something went wrong")

@router.get("/{id}",response_model=CourseResponse)
def find_course(id: PositiveInt, db: Session = Depends(get_db)):
    try:
        crs = db.query(Course).filter(Course.id == id).first()
        if not crs:
            return {"message":"Sorry! That Course cannot be found"}
        return crs
    except Exception:
        raise HTTPException(status_code=500, detail="Sorry something went wrong")

@router.post("/",response_model=CourseResponse)
def add_course(course: CourseAdd, db: Session = Depends(get_db)):
    try:
        if course.name is None:
            return {"error": "Enter a name!"}
        crs = Course(name=course.name)
        db.add(crs)
        db.commit()
        db.refresh(crs)
        return crs
    except RequestValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except (ValueError, IntegrityError) as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id}",response_model=CourseResponse)
def update_course(id: PositiveInt, update_crs: CourseUpdate, db: Session = Depends(get_db)):
    try:
        crs = db.get(Course,id)
        if crs is None:
            return {"message":"Course not found with that id"}
        tea = db.query(Teacher).filter(Teacher.id == update_crs.incharge_id).first()
        if not tea:
            return {"Teacher not found with that id"}
        crs.name = update_crs.name
        crs.incharge_id = update_crs.incharge_id
        crs.incharge = tea
        crs.teachers = [tea]
        db.commit()
        db.refresh(crs)
        return crs
    except RequestValidationError as e:
        raise HTTPException(status_code=422, detail="Bad request")
    except (ValueError, IntegrityError) as e:
        db.rollback()
        raise HTTPException(status_code=422, detail="Bad request")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id}")
def delete_course(id: PositiveInt, db: Session = Depends(get_db)):
    try:
        crs = db.get(Course,id)
        if crs is None:
            return {"message":"Course not found with that id"}
        db.delete(crs)
        db.commit()
        return {"message": f"Course with id={id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{course_id}/students")
def students_in_course(course_id: PositiveInt, db: Session = Depends(get_db)):
    try:
        crs = db.get(Course,course_id)
        if crs is None:
            return {"message":"Course not found with that id"}
        std = crs.students
        if not std:
            return {"message":"No Students found"}
        return {"students": [(s.firstname + s.lastname, s.id, s.dept) for s in std]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))