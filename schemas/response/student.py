from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from schemas.response.course import CourseResponse

class StudentResponse(BaseModel):
    id         : int
    firstname  : str
    lastname   : str
    semester   : int
    dept       : Optional[str] = None
    email      : str
    contact    : int
    start_date : Optional[datetime] = None
    end_date   : Optional[datetime] = None
    courses    : list[CourseResponse] = []
    model_config = {"from_attributes": True}
