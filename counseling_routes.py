from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.sql_models import User, CounselorRemark, CounselingRequest, UserRole, CounselingRequestStatus
from schemas import CounselorRemarkCreate, CounselorRemarkResponse, CounselingRequestCreate, CounselingRequestUpdate, CounselingRequestResponse
from routes.auth_routes import get_current_user, check_role
from typing import List

router = APIRouter(prefix="/counseling", tags=["Counseling"])

# --- Remarks ---
@router.post("/remarks", response_model=CounselorRemarkResponse)
def add_remark(
    remark: CounselorRemarkCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_role([UserRole.COUNSELOR, UserRole.TEACHER]))
):
    new_remark = CounselorRemark(
        student_id=remark.student_id,
        counselor_id=current_user.id,
        remarks=remark.remarks
    )
    db.add(new_remark)
    db.commit()
    db.refresh(new_remark)
    return new_remark

@router.get("/remarks/{student_id}", response_model=List[CounselorRemarkResponse])
def get_student_remarks(student_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Students can see their own remarks, teachers/counselors can see all
    if current_user.role == UserRole.STUDENT and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return db.query(CounselorRemark).filter(CounselorRemark.student_id == student_id).all()

# --- Requests ---
@router.post("/requests", response_model=CounselingRequestResponse)
def create_request(
    request: CounselingRequestCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_role([UserRole.STUDENT]))
):
    new_request = CounselingRequest(
        student_id=current_user.id,
        counselor_id=request.counselor_id,
        status=CounselingRequestStatus.PENDING
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request

@router.get("/requests", response_model=List[CounselingRequestResponse])
def get_requests(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.STUDENT:
        return db.query(CounselingRequest).filter(CounselingRequest.student_id == current_user.id).all()
    elif current_user.role == UserRole.COUNSELOR:
        return db.query(CounselingRequest).filter(
            (CounselingRequest.counselor_id == current_user.id) | (CounselingRequest.counselor_id == None)
        ).all()
    else:
        return db.query(CounselingRequest).all()

@router.patch("/requests/{request_id}", response_model=CounselingRequestResponse)
def update_request_status(
    request_id: int, 
    update: CounselingRequestUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_role([UserRole.COUNSELOR]))
):
    req = db.query(CounselingRequest).filter(CounselingRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    req.status = update.status
    if not req.counselor_id:
        req.counselor_id = current_user.id
        
    db.commit()
    db.refresh(req)
    return req

@router.post("/call/{student_id}")
def log_call(student_id: int, db: Session = Depends(get_db), current_user: User = Depends(check_role([UserRole.COUNSELOR, UserRole.TEACHER]))):
    # Simulated call logging
    return {"message": f"Call to student {student_id} logged by {current_user.name}"}
