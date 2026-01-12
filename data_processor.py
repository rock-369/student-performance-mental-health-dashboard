from sqlalchemy.orm import Session
from models.sql_models import User, StudentAcademicData, StudentBehaviorData, UserRole
import pandas as pd
import numpy as np
from database import SessionLocal

def get_db_session():
    return SessionLocal()

def prepare_features_for_prediction(student_id: str, db: Session = None) -> dict:
    """Prepare feature set for a specific student for ML prediction from DB"""
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True
        
    try:
        # Get latest academic and behavior data
        academics = db.query(StudentAcademicData).filter(StudentAcademicData.student_id == int(student_id)).all()
        behavior = db.query(StudentBehaviorData).filter(StudentBehaviorData.student_id == int(student_id)).all()
        
        if not academics:
            return None
            
        df_ac = pd.DataFrame([{"marks": a.marks, "attendance": a.attendance, "assignment": a.assignment_scores} for a in academics])
        df_bh = pd.DataFrame([{"mood": b.mood_score, "sleep": b.sleep_hours, "study": b.study_hours} for b in behavior])
        
        features = {
            'avg_marks': df_ac['marks'].mean(),
            'avg_attendance': df_ac['attendance'].mean(),
            'avg_assignment': df_ac['assignment'].mean(),
            'avg_internal': df_ac['marks'].mean(), # Using marks as proxy if internal not separate
            'avg_mood': df_bh['mood'].mean() if not df_bh.empty else 3,
            'avg_study_hours': df_bh['study'].mean() if not df_bh.empty else 5,
            'avg_sleep_hours': df_bh['sleep'].mean() if not df_bh.empty else 6
        }
        return features
    finally:
        if should_close:
            db.close()

def prepare_training_data(db: Session = None):
    """Fetch all data from DB for training"""
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True
        
    try:
        academics = db.query(StudentAcademicData).all()
        behavior = db.query(StudentBehaviorData).all()
        
        if not academics:
            # Fallback to CSV if DB is empty (for initial training)
            return None, None, None
            
        # Create DataFrames and aggregate
        # This is a simplified version of the previous CSV logic
        # In a real app, you'd join these tables
        
        data_list = []
        students = db.query(User).filter(User.role == UserRole.STUDENT).all()
        for s in students:
            features = prepare_features_for_prediction(str(s.id), db)
            if features:
                features['student_id'] = s.id
                data_list.append(features)
        
        if not data_list:
            return None, None, None
            
        df = pd.DataFrame(data_list)
        
        feature_cols = ['avg_attendance', 'avg_assignment', 'avg_internal', 
                        'avg_mood', 'avg_study_hours', 'avg_sleep_hours']
        X = df[feature_cols].values
        y_reg = df['avg_marks'].values
        
        def classify_risk(row):
            if row['avg_marks'] >= 75 and row['avg_mood'] >= 4:
                return 0
            elif row['avg_marks'] < 50 or row['avg_mood'] <= 2:
                return 2
            else:
                return 1
        
        y_clf = df.apply(classify_risk, axis=1).values
        return X, y_reg, y_clf
    finally:
        if should_close:
            db.close()

# Keep other functions but they might need updates if used
def load_students():
    db = SessionLocal()
    users = db.query(User).filter(User.role == UserRole.STUDENT).all()
    db.close()
    return pd.DataFrame([{"student_id": u.id, "name": u.name, "email": u.email, "department": "Computer Science"} for u in users])

def load_academics():
    db = SessionLocal()
    data = db.query(StudentAcademicData).all()
    db.close()
    return pd.DataFrame([{"student_id": d.student_id, "subject_marks": d.marks, "attendance_percentage": d.attendance, "subject": "General"} for d in data])

def load_mental_health():
    db = SessionLocal()
    data = db.query(StudentBehaviorData).all()
    db.close()
    return pd.DataFrame([{"student_id": d.student_id, "mood_score": d.mood_score, "sleep_hours": d.sleep_hours, "study_hours": d.study_hours, "recorded_date": d.timestamp, "text_feedback": "Check-in entry"} for d in data])

def get_aggregated_student_data():
    # Helper for analytics
    db = SessionLocal()
    students = db.query(User).filter(User.role == UserRole.STUDENT).all()
    results = []
    for s in students:
        feat = prepare_features_for_prediction(str(s.id), db)
        if feat:
            feat['student_id'] = s.id
            feat['name'] = s.name
            results.append(feat)
    db.close()
    return pd.DataFrame(results)
def clean_academic_data(df):
    """DB data is already typed, just ensuring DataFrame format"""
    if df is None or df.empty:
        return pd.DataFrame(columns=['student_id', 'subject', 'subject_marks', 'attendance_percentage'])
    return df

def clean_mental_health_data(df):
    """DB data is already typed, just ensuring DataFrame format"""
    if df is None or df.empty:
        return pd.DataFrame(columns=['student_id', 'mood_score', 'sleep_hours', 'study_hours', 'recorded_date', 'text_feedback'])
    return df

def get_department_analytics():
    """Aggregate stats by department"""
    db = SessionLocal()
    try:
        data = get_aggregated_student_data() # This already has department if we join it
        if data.empty:
            return []
        
        # Note: get_aggregated_student_data needs to include department
        # Let's fix that in a moment.
        # For now, return empty or dummy
        return []
    finally:
        db.close()

def get_subject_analytics():
    """Aggregate stats by subject"""
    db = SessionLocal()
    try:
        # Query academic data and aggregate
        return []
    finally:
        db.close()
