from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date, time
from .models import RoleEnum, AttendanceStatusEnum

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: RoleEnum
    institution_id: Optional[int] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class MonitoringTokenRequest(BaseModel):
    key: str

class BatchCreate(BaseModel):
    name: str
    institution_id: int

class JoinBatchRequest(BaseModel):
    token: str

class SessionCreate(BaseModel):
    title: str
    date: date
    start_time: time
    end_time: time
    batch_id: int

class AttendanceMark(BaseModel):
    session_id: int
    status: AttendanceStatusEnum

class BatchResponse(BaseModel):
    id: int
    name: str
    institution_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class SessionResponse(BaseModel):
    id: int
    batch_id: int
    trainer_id: int
    title: str
    date: date
    start_time: time
    end_time: time

    class Config:
        orm_mode = True
