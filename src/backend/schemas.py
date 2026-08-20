from pydantic import BaseModel, Field
from typing import Optional


class DetectionInput(BaseModel):
    camera_id: str
    zone: str
    people_count: int = Field(ge=0)
    crowd_level: str = "NORMAL"
    blocked: bool = False
    threat: Optional[str] = None