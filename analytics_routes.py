"""
Analytics Routes
API endpoints for analytics and insights
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services import AnalyticsService, MLService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

analytics_service = AnalyticsService()
ml_service = MLService()


@router.get("/class")
async def get_class_analytics(department: Optional[str] = Query(None, description="Filter by department")):
    """Get class-level analytics"""
    try:
        analytics = analytics_service.get_class_analytics(department)
        
        if not analytics:
            raise HTTPException(status_code=404, detail="No data found")
        
        return {
            "success": True,
            "data": analytics,
            "filters": {"department": department}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/departments")
async def get_department_analytics():
    """Get department-wise analytics"""
    try:
        summary = analytics_service.get_department_summary()
        
        return {
            "success": True,
            "data": summary,
            "count": len(summary)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subjects")
async def get_subject_analytics():
    """Get subject-wise analytics"""
    try:
        summary = analytics_service.get_subject_summary()
        
        return {
            "success": True,
            "data": summary,
            "count": len(summary)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/correlation/attendance-marks")
async def get_attendance_marks_correlation():
    """Get correlation between attendance and marks"""
    try:
        correlation = analytics_service.get_attendance_marks_correlation()
        
        return {
            "success": True,
            "data": correlation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/correlation/stress-marks")
async def get_stress_marks_correlation():
    """Get correlation between stress indicators and marks"""
    try:
        correlation = analytics_service.get_stress_marks_correlation()
        
        return {
            "success": True,
            "data": correlation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mental-health")
async def get_mental_health_trends(department: Optional[str] = Query(None, description="Filter by department")):
    """Get mental health trends"""
    try:
        trends = analytics_service.get_mental_health_trends(department)
        
        if not trends:
            raise HTTPException(status_code=404, detail="No data found")
        
        return {
            "success": True,
            "data": trends,
            "filters": {"department": department}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/at-risk")
async def get_at_risk_students(department: Optional[str] = Query(None, description="Filter by department")):
    """Get list of at-risk students"""
    try:
        analytics = analytics_service.get_class_analytics(department)
        
        if not analytics:
            raise HTTPException(status_code=404, detail="No data found")
        
        return {
            "success": True,
            "data": analytics['at_risk_students'],
            "count": len(analytics['at_risk_students']),
            "risk_distribution": analytics['risk_distribution']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teacher-dashboard")
async def get_teacher_dashboard(department: Optional[str] = Query(None, description="Filter by department")):
    """Get complete teacher dashboard data"""
    try:
        class_analytics = analytics_service.get_class_analytics(department)
        subject_analytics = analytics_service.get_subject_summary()
        attendance_correlation = analytics_service.get_attendance_marks_correlation()
        
        return {
            "success": True,
            "data": {
                "class_analytics": class_analytics,
                "subject_analytics": subject_analytics,
                "attendance_correlation": attendance_correlation
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/counselor-dashboard")
async def get_counselor_dashboard(department: Optional[str] = Query(None, description="Filter by department")):
    """Get complete counselor/admin dashboard data"""
    try:
        mental_health = analytics_service.get_mental_health_trends(department)
        stress_correlation = analytics_service.get_stress_marks_correlation()
        class_analytics = analytics_service.get_class_analytics(department)
        department_summary = analytics_service.get_department_summary()
        
        return {
            "success": True,
            "data": {
                "mental_health": mental_health,
                "stress_correlation": stress_correlation,
                "at_risk_students": class_analytics.get('at_risk_students', []) if class_analytics else [],
                "department_summary": department_summary
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
