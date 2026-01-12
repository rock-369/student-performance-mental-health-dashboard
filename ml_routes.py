"""
ML Routes
API endpoints for machine learning operations
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services import MLService

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

ml_service = MLService()


class SentimentRequest(BaseModel):
    text: str


class BatchPredictionRequest(BaseModel):
    student_ids: List[str]


@router.post("/train")
async def train_models():
    """Train all ML models"""
    try:
        metrics = ml_service.train_models()
        
        return {
            "success": True,
            "message": "Models trained successfully",
            "data": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_model_status():
    """Get status and info about trained models"""
    try:
        info = ml_service.get_model_info()
        
        return {
            "success": True,
            "data": info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sentiment")
async def analyze_sentiment(request: SentimentRequest):
    """Analyze sentiment of given text"""
    try:
        result = ml_service.analyze_sentiment(request.text)
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-predict")
async def batch_predictions(request: BatchPredictionRequest):
    """Get predictions for multiple students"""
    try:
        results = ml_service.get_batch_predictions(request.student_ids)
        
        return {
            "success": True,
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predict/{student_id}")
async def predict_performance(student_id: str):
    """Predict academic performance for a student"""
    try:
        prediction = ml_service.predict_performance(student_id)
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return {
            "success": True,
            "data": prediction
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk/{student_id}")
async def classify_risk(student_id: str):
    """Classify risk level for a student"""
    try:
        risk = ml_service.classify_risk(student_id)
        
        if not risk:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return {
            "success": True,
            "data": risk
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
