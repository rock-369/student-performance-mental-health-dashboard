from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.sql_models import User, UserRole, StudentAcademicData, StudentBehaviorData
from schemas import QuestionnaireInput, UserResponse
from routes.auth_routes import get_current_user, check_role
from services.student_service import StudentService
from typing import List

router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/questionnaire")
def submit_questionnaire(
    data: QuestionnaireInput, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_role([UserRole.STUDENT]))
):
    student_service = StudentService(db)
    result = student_service.process_questionnaire(current_user.id, data)
    return {"success": True, "data": result}

@router.get("/dashboard", response_model=dict)
def get_my_dashboard(
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_role([UserRole.STUDENT]))
):
    student_service = StudentService(db)
    data = student_service.get_student_dashboard_data(current_user.id)
    if not data:
        raise HTTPException(status_code=404, detail="Student data not found")
    return {"success": True, "data": data}

@router.get("/all", response_model=List[UserResponse])
def get_students_list(
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_role([UserRole.TEACHER, UserRole.COUNSELOR]))
):
    return db.query(User).filter(User.role == UserRole.STUDENT).all()

@router.get("/{student_id}/dashboard", response_model=dict)
def get_any_student_dashboard(
    student_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_role([UserRole.TEACHER, UserRole.COUNSELOR]))
):
    student_service = StudentService(db)
    data = student_service.get_student_dashboard_data(student_id)
    if not data:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"success": True, "data": data}
