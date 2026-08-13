from pydantic import BaseModel, EmailStr
from datetime import datetime

class TeacherAdd(BaseModel):
    name        : str
    subject     : str
    email       : EmailStr
    contact     : int
    joined_date : Optional[datetime] = None
    model_config = {"from_attributes": True}
