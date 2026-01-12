"""
ML Service
Handles model training and predictions
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from preprocessing import prepare_training_data, prepare_features_for_prediction
from models.ml_models import PerformancePredictor, RiskClassifier
from models.sentiment_analyzer import SentimentAnalyzer
from typing import Dict, Any, Optional


class MLService:
    """
    Service class for ML model operations
    """
    
    def __init__(self):
        self.performance_predictor = PerformancePredictor()
        self.risk_classifier = RiskClassifier()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.training_metrics = {}
    
    def train_models(self) -> Dict[str, Any]:
        """Train all ML models and return metrics"""
        X, y_reg, y_clf = prepare_training_data()
        
        # Train performance predictor
        reg_metrics = self.performance_predictor.train(X, y_reg)
        
        # Train risk classifier
        clf_metrics = self.risk_classifier.train(X, y_clf)
        
        # Save models
        self.performance_predictor.save()
        self.risk_classifier.save()
        
        self.training_metrics = {
            'performance_predictor': reg_metrics,
            'risk_classifier': clf_metrics,
            'status': 'trained'
        }
        
        return self.training_metrics
    
    def load_models(self) -> bool:
        """Load pre-trained models from disk"""
        try:
            self.performance_predictor.load()
            self.risk_classifier.load()
            return True
        except:
            return False
    
    def predict_performance(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Predict academic performance for a student"""
        if not self.performance_predictor.is_trained:
            self.train_models()
        
        features = prepare_features_for_prediction(student_id)
        if not features:
            return None
        
        predicted_score = self.performance_predictor.predict(features)
        feature_importance = self.performance_predictor.get_feature_importance()
        
        return {
            'student_id': student_id,
            'predicted_final_score': round(predicted_score, 2),
            'current_features': features,
            'feature_importance': feature_importance,
            'interpretation': self._interpret_prediction(predicted_score)
        }
    
    def classify_risk(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Classify risk level for a student"""
        if not self.risk_classifier.is_trained:
            self.train_models()
        
        features = prepare_features_for_prediction(student_id)
        if not features:
            return None
        
        risk_label, probabilities = self.risk_classifier.predict(features)
        feature_importance = self.risk_classifier.get_feature_importance()
        
        return {
            'student_id': student_id,
            'risk_level': risk_label,
            'probabilities': probabilities,
            'current_features': features,
            'feature_importance': feature_importance,
            'interpretation': self._interpret_risk(risk_label, probabilities)
        }
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of given text"""
        result = self.sentiment_analyzer.analyze(text)
        mental_health_score = self.sentiment_analyzer.get_mental_health_score(result)
        
        return {
            **result,
            'mental_health_score': mental_health_score,
            'mental_health_label': self._get_mental_health_label(mental_health_score)
        }
    
    def get_batch_predictions(self, student_ids: list) -> Dict[str, Any]:
        """Get predictions for multiple students"""
        if not self.performance_predictor.is_trained:
            self.train_models()
        
        results = []
        for sid in student_ids:
            perf = self.predict_performance(sid)
            risk = self.classify_risk(sid)
            if perf and risk:
                results.append({
                    'student_id': sid,
                    'predicted_score': perf['predicted_final_score'],
                    'risk_level': risk['risk_level'],
                    'risk_probabilities': risk['probabilities']
                })
        
        return {
            'predictions': results,
            'total_processed': len(results)
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about trained models"""
        return {
            'performance_predictor': {
                'is_trained': self.performance_predictor.is_trained,
                'model_type': 'RandomForestRegressor',
                'feature_importance': self.performance_predictor.get_feature_importance()
            },
            'risk_classifier': {
                'is_trained': self.risk_classifier.is_trained,
                'model_type': 'RandomForestClassifier',
                'feature_importance': self.risk_classifier.get_feature_importance()
            },
            'training_metrics': self.training_metrics
        }
    
    def _interpret_prediction(self, score: float) -> str:
        """Interpret predicted score"""
        if score >= 80:
            return 'Excellent performance expected. Keep up the great work!'
        elif score >= 60:
            return 'Good performance expected. Consider focusing on weaker areas.'
        elif score >= 40:
            return 'Average performance expected. Additional effort and support recommended.'
        else:
            return 'Below average performance predicted. Immediate intervention recommended.'
    
    def _interpret_risk(self, label: str, probs: Dict[str, float]) -> str:
        """Interpret risk classification"""
        confidence = max(probs.values())
        
        if label == 'High':
            return f'High risk detected with {confidence:.1%} confidence. Immediate attention required.'
        elif label == 'Medium':
            return f'Medium risk detected with {confidence:.1%} confidence. Monitor progress closely.'
        else:
            return f'Low risk with {confidence:.1%} confidence. Student is performing well.'
    
    def _get_mental_health_label(self, score: int) -> str:
        """Convert mental health score to label"""
        if score <= 3:
            return 'Concerning - Seek support'
        elif score <= 5:
            return 'Fair - Monitor closely'
        elif score <= 7:
            return 'Good - Maintain balance'
        else:
            return 'Excellent - Keep it up'
