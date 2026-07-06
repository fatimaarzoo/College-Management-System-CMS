from pydantic import BaseModel

class CourseAdd(BaseModel):
    name: str

    model_config = {"from_attributes": True}


class CourseUpdate(BaseModel):
    name: str
    incharge_id: int

    model_config = {"from_attributes": True}