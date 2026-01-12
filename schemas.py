from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from models.sql_models import UserRole, CounselingRequestStatus

# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int
    name: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

# Academic Data Schemas
class StudentAcademicDataBase(BaseModel):
    marks: float
    attendance: float
    assignment_scores: float

class StudentAcademicDataCreate(StudentAcademicDataBase):
    pass

class StudentAcademicDataResponse(StudentAcademicDataBase):
    id: int
    student_id: int
    predicted_performance: Optional[float]
    risk_level: Optional[str]
    timestamp: datetime
    class Config:
        from_attributes = True

# Behavior Data Schemas (Questionnaire)
class QuestionnaireInput(BaseModel):
    concentration_level: int # 1-5 mapping
    confidence_level: int # 1-5 mapping
    mental_fatigue: int # 1-5 mapping (will be inverted for mood)
    sleep_hours: float
    study_hours: float
    assignment_scores: float # Often asked in both
    marks: float
    attendance: float

class StudentBehaviorDataResponse(BaseModel):
    id: int
    student_id: int
    mood_score: int
    sleep_hours: float
    study_hours: float
    sentiment_result: Optional[str]
    timestamp: datetime
    class Config:
        from_attributes = True

# Counselor Schemas
class CounselorRemarkCreate(BaseModel):
    student_id: int
    remarks: str

class CounselorRemarkResponse(BaseModel):
    id: int
    student_id: int
    counselor_id: int
    remarks: str
    timestamp: datetime
    class Config:
        from_attributes = True

# Counseling Request Schemas
class CounselingRequestCreate(BaseModel):
    counselor_id: Optional[int] = None

class CounselingRequestUpdate(BaseModel):
    status: CounselingRequestStatus

class CounselingRequestResponse(BaseModel):
    id: int
    student_id: int
    counselor_id: Optional[int]
    status: str
    request_time: datetime
    class Config:
        from_attributes = True

# Chat Schemas
class ChatMessageCreate(BaseModel):
    receiver_id: int
    message: str

class ChatMessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    message: str
    timestamp: datetime
    class Config:
        from_attributes = True
