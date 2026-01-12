from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.sql_models import User, ChatMessage, UserRole
from schemas import ChatMessageCreate, ChatMessageResponse
from routes.auth_routes import get_current_user
from typing import List
from sqlalchemy import or_, and_

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/send", response_model=ChatMessageResponse)
def send_message(
    msg: ChatMessageCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    new_msg = ChatMessage(
        sender_id=current_user.id,
        receiver_id=msg.receiver_id,
        message=msg.message
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg

@router.get("/history/{other_user_id}", response_model=List[ChatMessageResponse])
def get_chat_history(
    other_user_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    history = db.query(ChatMessage).filter(
        or_(
            and_(ChatMessage.sender_id == current_user.id, ChatMessage.receiver_id == other_user_id),
            and_(ChatMessage.sender_id == other_user_id, ChatMessage.receiver_id == current_user.id)
        )
    ).order_by(ChatMessage.timestamp.asc()).all()
    return history

@router.get("/contacts", response_model=List[dict])
def get_chat_contacts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Students can see counselors and maybe teachers
    # Counselors/Teachers can see all students
    if current_user.role == UserRole.STUDENT:
        contacts = db.query(User).filter(User.role != UserRole.STUDENT).all()
    else:
        contacts = db.query(User).filter(User.role == UserRole.STUDENT).all()
    
    return [{"id": c.id, "name": c.name, "role": c.role} for c in contacts]
