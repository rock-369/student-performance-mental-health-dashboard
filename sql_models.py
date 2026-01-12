from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from database import Base
import datetime
import enum

class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    COUNSELOR = "counselor"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default=UserRole.STUDENT)

    academic_data = relationship("StudentAcademicData", back_populates="student", cascade="all, delete-orphan")
    behavior_data = relationship("StudentBehaviorData", back_populates="student", cascade="all, delete-orphan")
    counseling_requests = relationship("CounselingRequest", back_populates="student", foreign_keys="CounselingRequest.student_id")
    received_requests = relationship("CounselingRequest", back_populates="counselor", foreign_keys="CounselingRequest.counselor_id")

class StudentAcademicData(Base):
    __tablename__ = "student_academic_data"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    marks = Column(Float)
    attendance = Column(Float)
    assignment_scores = Column(Float)
    predicted_performance = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("User", back_populates="academic_data")

class StudentBehaviorData(Base):
    __tablename__ = "student_behavior_data"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    mood_score = Column(Integer) # 1-5
    sleep_hours = Column(Float)
    study_hours = Column(Float)
    sentiment_result = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("User", back_populates="behavior_data")

class CounselorRemark(Base):
    __tablename__ = "counselor_remarks"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    counselor_id = Column(Integer, ForeignKey("users.id"))
    remarks = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class CounselingRequestStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class CounselingRequest(Base):
    __tablename__ = "counseling_requests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    counselor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, default=CounselingRequestStatus.PENDING)
    request_time = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("User", back_populates="counseling_requests", foreign_keys=[student_id])
    counselor = relationship("User", back_populates="received_requests", foreign_keys=[counselor_id])
