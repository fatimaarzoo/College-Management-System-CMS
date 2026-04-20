from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from schemas import StudentAdd, StudentResponse, StudentUpdate
from models import Student, Course
from pydantic import ValidationError

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("/", response_model=list[StudentResponse])
def get_students(db: Session = Depends(get_db)):
    try:
        std = db.query(Student).order_by(Student.id.desc()).all()
        if not std:
            raise HTTPException(status_code=404, detail="No Students found")
        return std
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}", response_model=StudentResponse)
def find_student(id: int, db: Session = Depends(get_db)):
    try:
        std = db.query(Student).filter(Student.id == id).first()
        if not std:
            raise HTTPException(status_code=404, detail=f"Student of id={id} not found")
        return std
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def enroll_student(student: StudentAdd, db: Session = Depends(get_db)):
    try:
        std = Student(
            firstname=student.firstname,
            lastname=student.lastname,
            semester=student.semester,
            contact=student.contact,
            email=student.email,
        )
        db.add(std)
        db.commit()
        db.refresh(std)
        return StudentResponse.model_validate(std)
    except HTTPException:
        raise
    except ValidationError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student already exists")
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
@router.patch("/{student_id}/course/{course_id}")
def select_course(student_id: int, course_id: int, db: Session = Depends(get_db)):
    try:
        std = db.get(Student, student_id)
        crs = db.get(Course, course_id)
        if not std:
            return {"message": "Student not found"}
        if not crs:
            return {"message": "Course not found"}
        if crs not in std.courses:
            std.courses.append(crs)
        db.commit()
        return {"student": std.id, "course_ids": [(c.id, c.name) for c in std.courses]}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id}", response_model=StudentResponse)
def update_student(id: int, student: StudentUpdate, db: Session = Depends(get_db)):
    try:
        std = db.query(Student).filter(Student.id ==id).first()
        if not std:
            raise HTTPException(status_code=404, detail="Student not found")
        std.firstname  = student.firstname
        std.lastname   = student.lastname
        std.semester   = student.semester
        std.dept       = student.dept
        std.email      = student.email
        std.contact    = student.contact
        std.start_date = student.start_date
        std.end_date   = student.end_date
        db.commit()
        db.refresh(std)
        return StudentResponse.model_validate(std)
    except (ValueError, IntegrityError) as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id}")
def delete_student(id: int, db: Session = Depends(get_db)):
    try:
        std = db.query(Student).filter(Student.id == id).first()
        if not std:
            return {"message": "Student not found"}
        db.delete(std)
        db.commit()
        return {"message": "Student deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))