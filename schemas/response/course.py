from pydantic import BaseModel
from typing import Optional

class CourseResponse(BaseModel):
    id: int
    name: str
    incharge_id: Optional[int] = None

    model_config = {"from_attributes": True}