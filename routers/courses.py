from fastapi import APIRouter, Depends, HTTPException,Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import RequestValidationError
from database.database import get_db
from schemas import CourseAdd, CourseUpdate, CourseResponse
from database.models import Course, Teacher, User
from pydantic import PositiveInt
from typing import List
from .accounts import get_current_user,get_current_user_second


router = APIRouter(prefix="/courses", tags=["Courses"])
templates = Jinja2Templates(directory="templates")


@router.get("/",response_model=List[CourseResponse])
def get_courses(request: Request , db: Session = Depends(get_db)):
    """
    Method returns all courses
    """
    try:
        crs = db.query(Course).order_by(Course.id.desc()).all()
        if not crs:
           raise HTTPException(status_code=404, detail="Sorry courses could not be found")
        return templates.TemplateResponse(request=request, name="courses/courses.html", context={"crs":crs})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/add_course",response_class=HTMLResponse)
def add_course_page(request:Request):
    return templates.TemplateResponse(request=request, name="courses/add_course.html",context={})

@router.post("/add_course",response_model=CourseResponse)
def add_course(request:Request,course: CourseAdd, db: Session = Depends(get_db),user = Depends(get_current_user)):
    """
    Method adds one course 
    """
    try:
        if course.name is None:
            return {"error": "Enter a name!"}
        crs = Course(name=course.name)
        db.add(crs)
        db.commit()
        db.refresh(crs)
        course = crs
        # content=jsonable_encoder(course)
        # return JSONResponse(status_code=200, content={'course':course})
        return templates.TemplateResponse(request=request, name="courses/add_course.html", status_code=200)
    except RequestValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except (ValueError, IntegrityError) as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/update-course/{id}",response_class=HTMLResponse)
def update_course_page(request:Request,id: PositiveInt, db: Session = Depends(get_db)):
    crs = db.get(Course,id)
    return templates.TemplateResponse(request=request, name="courses/update-course.html",context={'crs':crs})

@router.put("/update-course/{id}",response_model=CourseResponse)#user depends,
def update_course(id: PositiveInt, update_crs: CourseUpdate, db: Session = Depends(get_db),user = Depends(get_current_user)):
    """
    Method updates the selected course
    """
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
        # return templates.TemplateResponse(request=request, name="courses/update-course.html",context={'crs':crs} ,status_code=200)
    except RequestValidationError as e:
        raise HTTPException(status_code=422, detail="Bad request")
    except (ValueError, IntegrityError) as e:
        db.rollback()
        raise HTTPException(status_code=422, detail="Bad request")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
   
@router.delete("/delete/{id}")
def delete_course(id: PositiveInt, db: Session = Depends(get_db),user = Depends(get_current_user)):#
    """
    Method deletes the selected course
    """
    try:
        crs = db.get(Course,id)
        if crs is None:
            return {"message":"Course not found with that id"}
        db.delete(crs)
        db.commit()
        return JSONResponse(status_code=200, content={"message": f"Course with id={id} deleted successfully"})
        # return {"message": f"Course with id={id} deleted successfully", "status": 200}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/{id}",response_model=CourseResponse)
def course_page(request:Request,id:int,db : Session = Depends(get_db)):
    """
    Method returns selected course
    """
    token = request.cookies.get("access_token")
    user_id= get_current_user_second(token)    
    user = db.query(User).filter(User.id == int(user_id)).first()
    print(user.role)

    try:
        crs = db.query(Course).filter(Course.id == id).first()
        if not crs:
            raise HTTPException(status_code=500, detail="Sorry the course could not be found")
        return templates.TemplateResponse(request=request, name="courses/course_detail.html",context={'crs':crs, 'user':user or None})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{course_id}/students")
def students_in_course(request:Request,course_id: PositiveInt, db: Session = Depends(get_db)):
    try:
        crs = db.get(Course,course_id)
        if crs is None:
            return {"message":"Course not found with that id"}
        std = crs.students
        if not std:
            return {"message":"No Students found"}
        return templates.TemplateResponse(request=request, name="courses/course_detail.html",context={"students": [(s.firstname + s.lastname, s.id, s.dept) for s in std],"std":std})
        return {"students": [(s.firstname + s.lastname, s.id, s.dept) for s in std]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



