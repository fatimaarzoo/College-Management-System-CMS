from sqlalchemy import Column,Integer,String,ForeignKey,DateTime,Boolean
from database.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
import uuid

#role=??? dictionary???
# role ={
#  1 : "Student",
#  2 : "Teacher"
#  3 : "Others"
# }

class User(Base):
    __tablename__ = "User"
    
    id       = Column(Integer,primary_key=True)
    username = Column(String(200),nullable=False,unique=True)
    password = Column(String(500),nullable=False)
    mail     = Column(String(200))
    role     = Column(String(50),nullable=True) # add access and refresh token column here #Sir said so
    
    student  = relationship("Student",back_populates="user",uselist=False)
    teacher  = relationship("Teacher",back_populates="user",uselist=False)
    session  = relationship("SessionTable",back_populates="user",uselist=False)

class TokenTable(Base):#change name
    __tablename__ = "token"
    
    user_id      =  Column(Integer)
    access_token = Column(String(450),primary_key=True)
    refresh_token= Column(String(450),nullable=False)
    status       = Column(Boolean)#claude said no need to add status but idk 
    created_date = Column(DateTime,default=datetime.now(timezone.utc))
    
class SessionTable(Base):
    __tablename__ = "session"
    
    id            = Column(String(200),primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id       = Column(Integer, ForeignKey("User.id"))
    user          = relationship("User",back_populates="session")
    device        = Column(String(200), nullable=True)   
    ip_address    = Column(String(200), nullable=True)
    login_time    = Column(DateTime, default=datetime.now(timezone.utc))
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active     = Column(Boolean, default=True)
    
    
class Student(Base):
    __tablename__ = "Student"
    
    id        = Column(Integer,primary_key=True,index=True)
    firstname = Column(String(50),nullable=True)
    lastname  = Column(String(50),nullable=True)
    semester  = Column(Integer)
    courses   = relationship("Course",secondary='student_course',back_populates='students',passive_deletes=True)
    #........................#class name ..........#object name
    dept      = Column(String(10))
    email     = Column(String(50),nullable=True,unique=True)
    contact   = Column(Integer,nullable=True)
    start_date= Column(DateTime)
    end_date  = Column(DateTime)
    
    user_id   = Column(Integer,ForeignKey("User.id"))
    user      = relationship("User",back_populates="student")

    def __repr__(self):
        return f"{self.firstname} + {self.lastname}"
    
class Teacher(Base):
    __tablename__ = "Teacher"
    
    id     = Column(Integer,primary_key=True,index=True)
    subject= Column(String(100),nullable=True)
    name   = Column(String(100),nullable=True)
    email  = Column(String(50),unique=True,nullable=True)
    contact= Column(String(15),nullable=True,unique=False)
    
    user_id= Column(Integer,ForeignKey("User.id"))
    user      = relationship("User",back_populates="teacher")
    
    dept_id= Column(Integer,ForeignKey('Department.dept_id'))
    dept   = relationship('Department',back_populates='faculty',foreign_keys=[dept_id])
    
    hod_dept_id = Column(Integer,ForeignKey('Department.dept_id'))
    hod_dept    = relationship('Department', back_populates='hod',foreign_keys=[hod_dept_id])
    
    #one to many/// one teacher can teach many course
    courses = relationship('Course',back_populates="incharge",foreign_keys="Course.incharge_id")

    #many to many
    tea_courses = relationship('Course',secondary='teacher_course',back_populates='teachers')
    
    #.....................#class name ..........#object name
    joined_date = Column(DateTime)
    
    def __repr__(self):
        return f"{self.name}"
    
    
class Department(Base):
    __tablename__ = "Department"
    
    dept_id   = Column(Integer,primary_key=True,index=True)
    dept_name = Column(String(200),nullable=True)
    
    # one to many // 1 dept <<< many teachers 
    faculty   = relationship('Teacher',back_populates='dept',foreign_keys='Teacher.dept_id')
    hod       = relationship('Teacher',back_populates='hod_dept',foreign_keys='Teacher.hod_dept_id')
    
    def __repr__(self):
        return f"{self.dept_name}"
    
    
class Course(Base):
    __tablename__ = "Course"
    
    id   = Column(Integer,primary_key=True,index=True)
    name = Column(String(100))
    
    #one to many
    incharge_id  = Column(Integer,ForeignKey('Teacher.id',ondelete="SET NULL"),nullable=True)
    incharge = relationship('Teacher',back_populates="courses",passive_deletes=True)
    
    #many to many [Teachers]
    teachers = relationship('Teacher',secondary='teacher_course',back_populates='tea_courses')
    
    #many to many one student can have many courses and one course can have many students
    students = relationship("Student",secondary='student_course',back_populates='courses')
    
    def __repr__(self):
        return f"{self.name}"
    
#...................................................


#relationship //association table od student and course
class StudentCourse(Base):#many to many
    __tablename__ = "student_course"
    
    id = Column(Integer,primary_key=True)
    student_id =Column('student_id',Integer,ForeignKey('Student.id',ondelete="CASCADE"))
    course_id = Column('course_id',Integer,ForeignKey('Course.id',ondelete="CASCADE"))


#pivot table

class TeacherCourse(Base):
    __tablename__ = "teacher_course"
    
    id      = Column(Integer,primary_key=True)
    teacher = Column('teacher_id',Integer,ForeignKey('Teacher.id',ondelete="CASCADE") )
    course  = Column('course_id',Integer,ForeignKey('Course.id',ondelete="CASCADE"))
    

# class Attendence(Base):
#     __tablename__ = "attendence"
    
#     id = Column(Integer,primary_key=True)
#     attendence = Column()
#     date = Column(Datetime)


# -----------------------------------

class Taskslog(Base):
    __tablename__ = "tasks_log"
    
    id        = Column(Integer,primary_key=True)
    name      = Column(String(300),nullable=True)
    task_id   = Column(String(300),nullable=True)
    status    = Column(String(100),nullable=True)
    result    = Column(String(300),nullable=True)
    fail_flag = Column(Integer,nullable=True ,default=0,insert_default=0)