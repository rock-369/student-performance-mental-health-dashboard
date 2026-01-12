import os
import sys

# Add the current directory to sys.path to allow importing from local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models.sql_models import User, UserRole, StudentAcademicData, StudentBehaviorData
from services.auth_service import AuthService
import datetime

# Create tables
Base.metadata.create_all(bind=engine)

def seed():
    db = SessionLocal()
    
    # Check if seed already exists
    if db.query(User).first():
        print("Database already seeded.")
        return

    # Create Users
    users = [
        {"name": "Admin Student", "email": "student@test.com", "password": "password123", "role": UserRole.STUDENT},
        {"name": "Teacher User", "email": "teacher@test.com", "password": "password123", "role": UserRole.TEACHER},
        {"name": "Counselor User", "email": "counselor@test.com", "password": "password123", "role": UserRole.COUNSELOR},
        {"name": "John Doe", "email": "john@test.com", "password": "password123", "role": UserRole.STUDENT},
    ]

    db_users = []
    for u in users:
        new_user = User(
            name=u["name"],
            email=u["email"],
            hashed_password=AuthService.get_password_hash(u["password"]),
            role=u["role"]
        )
        db.add(new_user)
        db_users.append(new_user)
    
    db.commit()
    
    # Add some initial data for students
    student_ids = [u.id for u in db_users if u.role == UserRole.STUDENT]
    
    for sid in student_ids:
        # Academic Data
        ac = StudentAcademicData(
            student_id=sid,
            marks=75.0,
            attendance=85.0,
            assignment_scores=80.0,
            predicted_performance=78.5,
            risk_level="Low"
        )
        db.add(ac)
        
        # Behavior Data
        bh = StudentBehaviorData(
            student_id=sid,
            mood_score=4,
            sleep_hours=7.5,
            study_hours=5.0,
            sentiment_result="Positive"
        )
        db.add(bh)
    
    db.commit()
    print("Database seeded successfully!")
    db.close()

if __name__ == "__main__":
    seed()
