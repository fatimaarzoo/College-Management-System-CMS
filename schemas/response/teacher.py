from pydantic import BaseModel
from typing import Optional
from schemas.response.course import CourseResponse
from datetime import datetime

class TeacherResponse(BaseModel):
    id      : int
    name    : str
    subject : str
    email   : str
    contact : int
    dept    : Optional[str] = None
    dept_id : Optional[int] = None
    courses : list[CourseResponse] = []
    joined_date : Optional[datetime] = None
    model_config = {"from_attributes": True}
