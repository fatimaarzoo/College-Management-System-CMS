from fastapi import APIRouter, Depends, HTTPException, status,Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.database import get_db
from schemas import StudentAdd, StudentResponse, StudentUpdate
from database.models import Student, Course
from pydantic import ValidationError
from .accounts import get_current_user

router = APIRouter(prefix="/students", tags=["Students"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_model=list[StudentResponse])
def get_students(request: Request,db: Session = Depends(get_db)):
    ''' Returns all Students and thier details. '''
    try:
        std = db.query(Student).order_by(Student.id.desc()).all()
        if not std:
            raise HTTPException(status_code=404, detail="No Students found")
        return templates.TemplateResponse(request=request, name="students/students.html", context={"std":std})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/add-student",response_class=HTMLResponse)
def add_student_page(request: Request , db: Session = Depends(get_db)):
        return templates.TemplateResponse(request=request, name="students/enroll_students.html",context={})


@router.post("/add-student", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def enroll_student(student: StudentAdd, db: Session = Depends(get_db),user = Depends(get_current_user)):
    """ 
        Send request Student details through post function of API to create an objectand then to database after data validation 
        
        Args*:
            Enter Students details in the request body 
            firstname(str)
            lastname(str)
            semester(int)
            contact(str)
            email(email)
        
        Returns:
            Student object: Student details of the Student you just entered with some additional columns.
    """
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
        # return templates.TemplateResponse(request=request, name="students/enroll_students.html", context={"std":StudentResponse.model_validate(std)})
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
    
@router.get("/update_student/{id}",response_class=HTMLResponse)
def update_student_page(request: Request ,id:int, db: Session = Depends(get_db)):
    std = db.query(Student).filter(Student.id ==id).first()
    return templates.TemplateResponse(request=request, name="students/update_student.html",context={'std':std})
 
@router.put("/update_student/{id}", response_model=StudentResponse)
def update_student(request:Request,id: int, student: StudentUpdate, db: Session = Depends(get_db),user = Depends(get_current_user)):
    """ 
        Updates an object. Send request Student details through put (replace the whole objects with a newer function u write) function of API to update an object.
        
        Args*:
            Enter the id of the student u want to update
            id(int): Student id
            Enter Students details in the request body 
            firstname(str)
            lastname(str)
            semester(int)
            dept(str)
            email(email)
            contact(str)
            start_date(datetime)
            end_date(datetime)
            
        Returns:
            Student object: Student details of the Student you just entered with some additional columns.
    """
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
        # return templates.TemplateResponse(request=request, name="students/update_student.html",context={'std':StudentResponse.model_validate(std)})
        
    except (ValueError, IntegrityError) as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/select_course/{id}",response_class=HTMLResponse)
def add_student_page(request: Request ,id:int, db: Session = Depends(get_db)):
    std = db.get(Student, id)
    crs = db.query(Course).all()
    return templates.TemplateResponse(request=request, name="students/select_course.html",context={"std":std,"crs":crs})
   
@router.get("/{id}", response_model=StudentResponse)
def find_student(request:Request,id: int, db: Session = Depends(get_db)):
    """ Args*:
            Accepts specific Student id as a parameter 
            id(int) : id of the Student
        
        Returns:
            Student object: Student details of the Student with that id.
    """
    try:
        std = db.query(Student).filter(Student.id == id).first()
        if not std:
            raise HTTPException(status_code=404, detail=f"Student of id={id} not found")
        return templates.TemplateResponse(request=request, name="students/student_details.html", context={"std":std})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    
@router.patch("/{student_id}/course/{course_id}")
def select_course(student_id: int, course_id: int, db: Session = Depends(get_db),user = Depends(get_current_user)):
    """ 
        Selects or adds the courses the student is intrested in. 
        One student can select multiple courses
        
        Args*:
           Takes student id and course id to add the course to course to the student
           student_id(int) : Id of student that have to select the course , takes single parameter
           course_id(int)  : Id of course that have to be added to the student , takes single parameter
        
        Returns:
            Student id and all the courses that student have selected along with the courses name
    """
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
        return {"student": std.id, "course_ids": [(c.id, c.name) for c in std.courses],"status":200}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



@router.delete("/{id}")
def delete_student(id: int, db: Session = Depends(get_db),user = Depends(get_current_user)):
    """
    Deletes one student(object) details
    
    Args*:
        Enter id of the student you want to delete the details or object of
        id(int) : id of the desired student 
          
    Returns:
        Successful message on successful deletion  
    
    """
    try:
        std = db.query(Student).filter(Student.id == id).first()
        if not std:
            return {"message": "Student not found"}
        db.delete(std)
        db.commit()
        return {"message": "Student deleted successfully","status":200}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
