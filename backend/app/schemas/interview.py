from pydantic import BaseModel
from datetime import datetime


class InterviewBase(BaseModel):
    title: str
    transcript: str


class InterviewCreate(InterviewBase):
    pass


class InterviewRead(InterviewBase):
    id: int
    analysis: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True 