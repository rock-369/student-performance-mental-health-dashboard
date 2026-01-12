from sqlalchemy.orm import Session
from models.sql_models import User, StudentAcademicData, StudentBehaviorData, UserRole
from schemas import QuestionnaireInput
from services.ml_service import MLService
from typing import Dict, Any

class StudentService:
    def __init__(self, db: Session):
        self.db = db
        self.ml_service = MLService()

    def process_questionnaire(self, student_id: int, data: QuestionnaireInput):
        # 1. Map indirect questions to mood score (1-5)
        # Concentration (1-5), Confidence (1-5), Fatigue (1-5, inverted)
        # Invert fatigue: 1 -> 5, 2 -> 4, 3 -> 3, 4 -> 2, 5 -> 1
        inverted_fatigue = 6 - data.mental_fatigue
        
        avg_mood_score = (data.concentration_level + data.confidence_level + inverted_fatigue) / 3
        final_mood_score = round(avg_mood_score)
        
        # 2. Store Behavior Data
        sentiment_result = self.ml_service.analyze_sentiment(f"Concentration: {data.concentration_level}, Confidence: {data.confidence_level}, Fatigue: {data.mental_fatigue}")
        
        behavior_entry = StudentBehaviorData(
            student_id=student_id,
            mood_score=final_mood_score,
            sleep_hours=data.sleep_hours,
            study_hours=data.study_hours,
            sentiment_result=sentiment_result['label']
        )
        self.db.add(behavior_entry)
        
        # 3. Store Academic Data
        # For prediction, we need to calculate it now or let a background task do it
        # For now, let's just use the current marks as a proxy or trigger prediction
        
        academic_entry = StudentAcademicData(
            student_id=student_id,
            marks=data.marks,
            attendance=data.attendance,
            assignment_scores=data.assignment_scores
        )
        self.db.add(academic_entry)
        self.db.commit()
        self.db.refresh(academic_entry)
        
        # 4. Trigger ML Prediction and update the academic entry
        # In a real app, you'd fetch all historical data for this student
        prediction = self.ml_service.predict_performance(str(student_id))
        risk = self.ml_service.classify_risk(str(student_id))
        
        if prediction:
            academic_entry.predicted_performance = prediction['predicted_final_score']
        if risk:
            academic_entry.risk_level = risk['risk_level']
            
        self.db.commit()
        
        return {
            "mood_score": final_mood_score,
            "prediction": prediction,
            "risk": risk
        }

    def get_student_dashboard_data(self, student_id: int):
        from services.analytics_service import AnalyticsService
        
        user = self.db.query(User).filter(User.id == student_id).first()
        if not user:
            return None
            
        academic = self.db.query(StudentAcademicData).filter(StudentAcademicData.student_id == student_id).order_by(StudentAcademicData.timestamp.desc()).first()
        behavior = self.db.query(StudentBehaviorData).filter(StudentBehaviorData.student_id == student_id).order_by(StudentBehaviorData.timestamp.desc()).first()
        
        # Use AnalyticsService for rich data
        analytics_service = AnalyticsService()
        performance_trends = analytics_service.get_student_performance_trends(student_id)
        recommendations = analytics_service.generate_recommendations(student_id)
        
        # Construct response
        response = {
            "student_info": {
                "student_id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "department": "Computer Science", # Placeholder
                "year": 3 # Placeholder
            },
            "performance": performance_trends if performance_trends else {
                "summary": {
                    "avg_marks": academic.marks if academic else 0,
                    "avg_attendance": academic.attendance if academic else 0,
                    "avg_mood": behavior.mood_score if behavior else 3,
                    "avg_sleep_hours": behavior.sleep_hours if behavior else 7,
                    "avg_study_hours": behavior.study_hours if behavior else 4
                },
                "subjects": [], # Would need subject-wise data
                "mental_trends": [] # Would need historical data
            },
            "prediction": {
                "predicted_final_score": academic.predicted_performance if academic else None,
                "interpretation": "Based on your current trends."
            },
            "risk": {
                "risk_level": academic.risk_level if academic else "Low",
                "probabilities": {"Low": 0.8, "Medium": 0.15, "High": 0.05} # Placeholder
            },
            "recommendations": recommendations if recommendations else []
        }
        
        return response
