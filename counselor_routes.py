"""
Counselor Routes
API endpoints for counselor remarks and notes on students
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import pandas as pd
from pathlib import Path

router = APIRouter(prefix="/counselor", tags=["Counselor"])

DATA_DIR = Path(__file__).parent.parent / "data"
REMARKS_FILE = DATA_DIR / "counselor_remarks.csv"


class RemarkCreate(BaseModel):
    student_id: str
    counselor_name: str
    remark: str
    category: str = "general"


class RemarkResponse(BaseModel):
    student_id: str
    counselor_name: str
    remark: str
    created_at: str
    category: str


def load_remarks():
    """Load remarks from CSV file"""
    if REMARKS_FILE.exists():
        return pd.read_csv(REMARKS_FILE)
    return pd.DataFrame(columns=['student_id', 'counselor_name', 'remark', 'created_at', 'category'])


def save_remarks(df):
    """Save remarks to CSV file"""
    df.to_csv(REMARKS_FILE, index=False)


@router.get("/remarks")
async def get_all_remarks():
    """Get all counselor remarks"""
    try:
        remarks = load_remarks()
        # Sort by created_at descending (newest first)
        if not remarks.empty:
            remarks = remarks.sort_values('created_at', ascending=False)
        return {
            "success": True,
            "data": remarks.to_dict('records'),
            "total": len(remarks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/remarks/{student_id}")
async def get_student_remarks(student_id: str):
    """Get all remarks for a specific student"""
    try:
        remarks = load_remarks()
        student_remarks = remarks[remarks['student_id'] == student_id]
        
        if not student_remarks.empty:
            student_remarks = student_remarks.sort_values('created_at', ascending=False)
        
        return {
            "success": True,
            "data": student_remarks.to_dict('records'),
            "total": len(student_remarks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/remarks")
async def create_remark(remark_data: RemarkCreate):
    """Create a new counselor remark for a student"""
    try:
        remarks = load_remarks()
        
        new_remark = {
            'student_id': remark_data.student_id,
            'counselor_name': remark_data.counselor_name,
            'remark': remark_data.remark,
            'created_at': datetime.now().isoformat(),
            'category': remark_data.category
        }
        
        # Create new DataFrame with the new remark
        new_df = pd.DataFrame([new_remark])
        remarks = pd.concat([remarks, new_df], ignore_index=True)
        
        save_remarks(remarks)
        
        return {
            "success": True,
            "message": "Remark added successfully",
            "data": new_remark
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/remarks/{student_id}/{created_at}")
async def delete_remark(student_id: str, created_at: str):
    """Delete a specific remark"""
    try:
        remarks = load_remarks()
        
        # Find and remove the remark
        mask = (remarks['student_id'] == student_id) & (remarks['created_at'] == created_at)
        
        if not mask.any():
            raise HTTPException(status_code=404, detail="Remark not found")
        
        remarks = remarks[~mask]
        save_remarks(remarks)
        
        return {
            "success": True,
            "message": "Remark deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
