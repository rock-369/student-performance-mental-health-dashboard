"""
Analytics Service
Provides comprehensive analytics for dashboards
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from preprocessing import (
    load_students, load_academics, load_mental_health,
    clean_academic_data, clean_mental_health_data,
    get_aggregated_student_data, get_department_analytics,
    get_subject_analytics
)
from models.sentiment_analyzer import SentimentAnalyzer
from typing import Dict, Any, List
import pandas as pd
import numpy as np


class AnalyticsService:
    """
    Service class that handles all analytics operations
    """
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self._cache = {}
    
    def get_student_performance_trends(self, student_id: int) -> Dict[str, Any]:
        """Get performance trends for a specific student"""
        academics = clean_academic_data(load_academics())
        mental_health = clean_mental_health_data(load_mental_health())
        
        # Ensure student_id is int for comparison if needed, or string matching DB
        # Assuming DB returns ints
        try:
            student_id = int(student_id)
        except ValueError:
            pass # Keep as string if conversion fails
            
        student_academics = academics[academics['student_id'] == student_id]
        student_mental = mental_health[mental_health['student_id'] == student_id]
        
        if student_academics.empty and student_mental.empty:
             # Fallback to return empty structure instead of None to prevent frontend crash
             return None
        
        # Subject-wise performance
        subjects = []
        if not student_academics.empty:
             subjects = student_academics[['subject', 'subject_marks', 'attendance_percentage']].to_dict('records')
        
        # Time-based mental health trends
        mental_trends = []
        if not student_mental.empty:
            for _, row in student_mental.iterrows():
                sentiment = self.sentiment_analyzer.analyze(row['text_feedback'])
                mental_trends.append({
                    'date': row['recorded_date'].strftime('%Y-%m-%d'),
                    'mood_score': int(row['mood_score']),
                    'study_hours': float(row['study_hours']),
                    'sleep_hours': float(row['sleep_hours']),
                    'sentiment': sentiment['sentiment'],
                    'polarity': sentiment['polarity']
                })
        
        # Calculate summary stats
        # Calculate summary stats
        summary = {
            'avg_marks': float(student_academics['subject_marks'].mean()) if not student_academics.empty else 0.0,
            'avg_attendance': float(student_academics['attendance_percentage'].mean()) if not student_academics.empty else 0.0,
            'highest_subject': student_academics.loc[student_academics['subject_marks'].idxmax(), 'subject'] if not student_academics.empty else 'N/A',
            'lowest_subject': student_academics.loc[student_academics['subject_marks'].idxmin(), 'subject'] if not student_academics.empty else 'N/A',
            'avg_mood': float(student_mental['mood_score'].mean()) if not student_mental.empty else 3.0,
            'avg_study_hours': float(student_mental['study_hours'].mean()) if not student_mental.empty else 5.0,
            'avg_sleep_hours': float(student_mental['sleep_hours'].mean()) if not student_mental.empty else 6.0
        }
        
        return {
            'subjects': subjects,
            'mental_trends': mental_trends,
            'summary': summary
        }
    
    def get_class_analytics(self, department: str = None) -> Dict[str, Any]:
        """Get class-level analytics, optionally filtered by department"""
        data = get_aggregated_student_data()
        
        if department:
            data = data[data['department'] == department]
        
        if data.empty:
            return None
        
        # Performance distribution
        def categorize_performance(marks):
            if marks >= 80:
                return 'Excellent'
            elif marks >= 60:
                return 'Good'
            elif marks >= 40:
                return 'Average'
            else:
                return 'Poor'
        
        data['performance_category'] = data['avg_marks'].apply(categorize_performance)
        perf_distribution = data['performance_category'].value_counts().to_dict()
        
        # Risk distribution (based on preprocessing logic)
        def calculate_risk(row):
            if row['avg_marks'] >= 70 and row['avg_mood'] >= 4:
                return 'Low'
            elif row['avg_marks'] < 50 or row['avg_mood'] <= 2:
                return 'High'
            else:
                return 'Medium'
        
        data['risk_level'] = data.apply(calculate_risk, axis=1)
        risk_distribution = data['risk_level'].value_counts().to_dict()
        
        # At-risk students
        at_risk = data[data['risk_level'] == 'High'][
            ['student_id', 'name', 'department', 'avg_marks', 'avg_mood']
        ].to_dict('records')
        
        # Statistics
        stats = {
            'total_students': len(data),
            'avg_marks': float(data['avg_marks'].mean()),
            'avg_attendance': float(data['avg_attendance'].mean()),
            'avg_mood': float(data['avg_mood'].mean()),
            'marks_std': float(data['avg_marks'].std())
        }
        
        return {
            'performance_distribution': perf_distribution,
            'risk_distribution': risk_distribution,
            'at_risk_students': at_risk,
            'statistics': stats
        }
    
    def get_attendance_marks_correlation(self) -> Dict[str, Any]:
        """Analyze correlation between attendance and marks"""
        academics = clean_academic_data(load_academics())
        
        correlation = academics['attendance_percentage'].corr(academics['subject_marks'])
        
        # Create scatter plot data
        scatter_data = academics[['attendance_percentage', 'subject_marks']].to_dict('records')
        
        # Group by attendance ranges
        def attendance_range(att):
            if att >= 90:
                return '90-100%'
            elif att >= 75:
                return '75-89%'
            elif att >= 60:
                return '60-74%'
            else:
                return '<60%'
        
        academics['att_range'] = academics['attendance_percentage'].apply(attendance_range)
        range_stats = academics.groupby('att_range')['subject_marks'].mean().to_dict()
        
        return {
            'correlation_coefficient': round(correlation, 3),
            'interpretation': self._interpret_correlation(correlation),
            'range_wise_average': range_stats,
            'data_points': scatter_data[:100]  # Limit for frontend
        }
    
    def get_mental_health_trends(self, department: str = None) -> Dict[str, Any]:
        """Get mental health trends across students"""
        mental_health = clean_mental_health_data(load_mental_health())
        students = load_students()
        
        # Merge with student info
        data = mental_health.merge(students[['student_id', 'department']], on='student_id')
        
        if department:
            data = data[data['department'] == department]
        
        if data.empty:
            return None
        
        # Analyze all feedback
        all_feedback = data['text_feedback'].tolist()
        batch_analysis = self.sentiment_analyzer.analyze_batch(all_feedback)
        
        # Mood distribution
        mood_dist = data['mood_score'].value_counts().sort_index().to_dict()
        
        # Time-based trends (average by date)
        time_trends = data.groupby('recorded_date').agg({
            'mood_score': 'mean',
            'study_hours': 'mean',
            'sleep_hours': 'mean'
        }).reset_index()
        
        time_trends['recorded_date'] = time_trends['recorded_date'].dt.strftime('%Y-%m-%d')
        time_trends = time_trends.to_dict('records')
        
        # Identify concerning cases
        concerning = data[data['mood_score'] <= 2][
            ['student_id', 'mood_score', 'recorded_date', 'text_feedback']
        ].to_dict('records')
        
        for case in concerning:
            case['recorded_date'] = case['recorded_date'].strftime('%Y-%m-%d')
            sentiment = self.sentiment_analyzer.analyze(case['text_feedback'])
            case['sentiment'] = sentiment['sentiment']
            case['stress_indicators'] = sentiment['stress_indicators']
        
        return {
            'sentiment_distribution': batch_analysis['sentiment_distribution'],
            'mood_distribution': mood_dist,
            'time_trends': time_trends,
            'concerning_cases': concerning,
            'common_stress_indicators': batch_analysis['common_stress_indicators'],
            'average_polarity': batch_analysis['average_polarity']
        }
    
    def get_stress_marks_correlation(self) -> Dict[str, Any]:
        """Analyze correlation between mental health indicators and academic performance"""
        data = get_aggregated_student_data()
        
        correlations = {
            'mood_vs_marks': round(data['avg_mood'].corr(data['avg_marks']), 3),
            'sleep_vs_marks': round(data['avg_sleep_hours'].corr(data['avg_marks']), 3),
            'study_vs_marks': round(data['avg_study_hours'].corr(data['avg_marks']), 3),
            'mood_vs_attendance': round(data['avg_mood'].corr(data['avg_attendance']), 3)
        }
        
        # Interpretation
        interpretations = {
            key: self._interpret_correlation(val) 
            for key, val in correlations.items()
        }
        
        return {
            'correlations': correlations,
            'interpretations': interpretations,
            'insights': self._generate_insights(correlations)
        }
    
    def get_department_summary(self) -> List[Dict[str, Any]]:
        """Get summary statistics by department"""
        return get_department_analytics()
    
    def get_subject_summary(self) -> List[Dict[str, Any]]:
        """Get summary statistics by subject"""
        return get_subject_analytics()
    
    def generate_recommendations(self, student_id: str) -> List[Dict[str, Any]]:
        """Generate AI-powered recommendations for a student"""
        trends = self.get_student_performance_trends(student_id)
        
        if not trends:
            return []
        
        recommendations = []
        summary = trends['summary']
        
        # Academic recommendations
        if summary['avg_marks'] < 60:
            recommendations.append({
                'type': 'academic',
                'priority': 'high',
                'title': 'Improve Academic Performance',
                'description': f"Your average marks ({summary['avg_marks']:.1f}%) need improvement. Consider forming study groups and utilizing tutoring services.",
                'action_items': [
                    'Schedule regular tutoring sessions',
                    'Join or form a study group',
                    'Create a structured study schedule',
                    'Seek help from professors during office hours'
                ]
            })
        
        if summary['avg_attendance'] < 75:
            recommendations.append({
                'type': 'attendance',
                'priority': 'high',
                'title': 'Improve Attendance',
                'description': f"Your attendance ({summary['avg_attendance']:.1f}%) is below the recommended threshold. Regular attendance is correlated with better academic performance.",
                'action_items': [
                    'Set multiple alarms for morning classes',
                    'Partner with a classmate for accountability',
                    'Address any underlying issues affecting attendance'
                ]
            })
        
        # Mental health recommendations
        if summary['avg_mood'] <= 2:
            recommendations.append({
                'type': 'mental_health',
                'priority': 'urgent',
                'title': 'Seek Mental Health Support',
                'description': 'Your recent mood indicators suggest you may be experiencing significant stress. Please consider reaching out to campus counseling services.',
                'action_items': [
                    'Schedule an appointment with a campus counselor',
                    'Talk to a trusted friend, family member, or mentor',
                    'Practice stress-reduction techniques like meditation',
                    'Helpline: Campus Wellness Center'
                ]
            })
        elif summary['avg_mood'] <= 3:
            recommendations.append({
                'type': 'wellness',
                'priority': 'medium',
                'title': 'Focus on Well-being',
                'description': 'Consider incorporating wellness activities into your routine to maintain a healthy balance.',
                'action_items': [
                    'Take regular breaks during study sessions',
                    'Engage in physical activity',
                    'Maintain social connections'
                ]
            })
        
        if summary['avg_sleep_hours'] < 6:
            recommendations.append({
                'type': 'health',
                'priority': 'medium',
                'title': 'Improve Sleep Habits',
                'description': f"You're averaging {summary['avg_sleep_hours']:.1f} hours of sleep. Adults need 7-9 hours for optimal cognitive function.",
                'action_items': [
                    'Set a consistent bedtime',
                    'Limit screen time before bed',
                    'Create a relaxing pre-sleep routine',
                    'Avoid caffeine in the evening'
                ]
            })
        
        if summary['avg_study_hours'] < 4:
            recommendations.append({
                'type': 'study_habits',
                'priority': 'medium',
                'title': 'Increase Study Time',
                'description': f"Consider increasing your study hours from {summary['avg_study_hours']:.1f} hours to at least 4-6 hours daily.",
                'action_items': [
                    'Use the Pomodoro technique for focused study',
                    'Identify and minimize distractions',
                    'Create a dedicated study space'
                ]
            })
        
        # Positive reinforcement
        if summary['avg_marks'] >= 80 and summary['avg_mood'] >= 4:
            recommendations.append({
                'type': 'positive',
                'priority': 'low',
                'title': 'Keep Up the Great Work!',
                'description': 'Your academic performance and well-being indicators are excellent. Continue maintaining your healthy habits.',
                'action_items': [
                    'Consider mentoring other students',
                    'Explore advanced opportunities like research',
                    'Maintain your work-life balance'
                ]
            })
        
        return recommendations
    
    def _interpret_correlation(self, corr: float) -> str:
        """Interpret correlation coefficient"""
        if corr >= 0.7:
            return 'Strong positive correlation'
        elif corr >= 0.4:
            return 'Moderate positive correlation'
        elif corr >= 0.2:
            return 'Weak positive correlation'
        elif corr > -0.2:
            return 'No significant correlation'
        elif corr > -0.4:
            return 'Weak negative correlation'
        elif corr > -0.7:
            return 'Moderate negative correlation'
        else:
            return 'Strong negative correlation'
    
    def _generate_insights(self, correlations: Dict[str, float]) -> List[str]:
        """Generate human-readable insights from correlation data"""
        insights = []
        
        if correlations['mood_vs_marks'] > 0.3:
            insights.append("Students with higher mood scores tend to perform better academically. Mental health support could improve academic outcomes.")
        
        if correlations['sleep_vs_marks'] > 0.3:
            insights.append("Better sleep habits are associated with higher academic performance. Sleep hygiene should be promoted.")
        
        if correlations['study_vs_marks'] > 0.5:
            insights.append("Study hours show strong correlation with marks. Encouraging productive study habits is beneficial.")
        
        if correlations['mood_vs_attendance'] > 0.4:
            insights.append("Students with better mental health show higher attendance. Early mental health intervention could reduce absenteeism.")
        
        if not insights:
            insights.append("Continue monitoring patterns as more data becomes available for deeper insights.")
        
        return insights
