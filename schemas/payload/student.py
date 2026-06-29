from pydantic import BaseModel, EmailStr
from datetime import datetime

class StudentAdd(BaseModel):
    firstname : str
    lastname  : str
    semester  : int
    email     : EmailStr
    contact   : int
    model_config = {"from_attributes": True}

class StudentUpdate(BaseModel):
    firstname  : str
    lastname   : str
    semester   : int
    dept       : str
    email      : EmailStr
    contact    : int
    start_date : datetime
    end_date   : datetime
    model_config = {"from_attributes": True}

class SelectCourse(BaseModel):
    courses : list[int]
    model_config = {"from_attributes": True}
