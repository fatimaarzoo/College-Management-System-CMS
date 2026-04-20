from pydantic import BaseModel, EmailStr
from datetime import datetime

class TeacherAdd(BaseModel):
    name        : str
    subject     : str
    email       : EmailStr
    contact     : int
    joined_date : datetime
    model_config = {"from_attributes": True}
