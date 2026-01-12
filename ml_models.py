"""
Machine Learning Models Module
Contains models for academic performance prediction and risk classification
"""
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import pickle
from pathlib import Path
from typing import Dict, Any, Tuple

MODEL_DIR = Path(__file__).parent


class PerformancePredictor:
    """
    Regression model to predict student's final academic score
    Uses Random Forest Regressor for robust predictions
    """
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = [
            'avg_attendance', 'avg_assignment', 'avg_internal',
            'avg_mood', 'avg_study_hours', 'avg_sleep_hours'
        ]
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Train the regression model"""
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        
        metrics = {
            'mse': float(mean_squared_error(y_test, y_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
            'r2_score': float(r2_score(y_test, y_pred))
        }
        
        return metrics
    
    def predict(self, features: Dict[str, float]) -> float:
        """Predict final score for a student"""
        if not self.is_trained:
            raise ValueError("Model not trained yet!")
        
        # Prepare features in correct order
        X = np.array([[
            features.get('avg_attendance', 0),
            features.get('avg_assignment', 0),
            features.get('avg_internal', 0),
            features.get('avg_mood', 3),
            features.get('avg_study_hours', 5),
            features.get('avg_sleep_hours', 6)
        ]])
        
        X_scaled = self.scaler.transform(X)
        prediction = self.model.predict(X_scaled)[0]
        
        # Ensure prediction is within valid range
        return float(max(0, min(100, prediction)))
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from the model"""
        if not self.is_trained:
            return {}
        
        importances = self.model.feature_importances_
        return dict(zip(self.feature_names, importances.tolist()))
    
    def save(self, filepath: str = None):
        """Save model to disk"""
        if filepath is None:
            filepath = MODEL_DIR / "performance_predictor.pkl"
        
        with open(filepath, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'is_trained': self.is_trained
            }, f)
    
    def load(self, filepath: str = None):
        """Load model from disk"""
        if filepath is None:
            filepath = MODEL_DIR / "performance_predictor.pkl"
        
        if Path(filepath).exists():
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.scaler = data['scaler']
                self.is_trained = data['is_trained']


class RiskClassifier:
    """
    Classification model to categorize students into risk levels
    Low (0) / Medium (1) / High (2)
    """
    
    RISK_LABELS = {0: 'Low', 1: 'Medium', 2: 'High'}
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=8,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = [
            'avg_attendance', 'avg_assignment', 'avg_internal',
            'avg_mood', 'avg_study_hours', 'avg_sleep_hours'
        ]
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train the classification model"""
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        
        metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'classification_report': classification_report(
                y_test, y_pred, 
                target_names=['Low', 'Medium', 'High'],
                output_dict=True
            )
        }
        
        return metrics
    
    def predict(self, features: Dict[str, float]) -> Tuple[str, Dict[str, float]]:
        """
        Predict risk category for a student
        Returns: (risk_label, probability_dict)
        """
        if not self.is_trained:
            raise ValueError("Model not trained yet!")
        
        # Prepare features in correct order
        X = np.array([[
            features.get('avg_attendance', 0),
            features.get('avg_assignment', 0),
            features.get('avg_internal', 0),
            features.get('avg_mood', 3),
            features.get('avg_study_hours', 5),
            features.get('avg_sleep_hours', 6)
        ]])
        
        X_scaled = self.scaler.transform(X)
        
        # Get prediction and probabilities
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        
        risk_label = self.RISK_LABELS[prediction]
        prob_dict = {
            'Low': float(probabilities[0]),
            'Medium': float(probabilities[1]),
            'High': float(probabilities[2])
        }
        
        return risk_label, prob_dict
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from the model"""
        if not self.is_trained:
            return {}
        
        importances = self.model.feature_importances_
        return dict(zip(self.feature_names, importances.tolist()))
    
    def save(self, filepath: str = None):
        """Save model to disk"""
        if filepath is None:
            filepath = MODEL_DIR / "risk_classifier.pkl"
        
        with open(filepath, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'is_trained': self.is_trained
            }, f)
    
    def load(self, filepath: str = None):
        """Load model from disk"""
        if filepath is None:
            filepath = MODEL_DIR / "risk_classifier.pkl"
        
        if Path(filepath).exists():
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.scaler = data['scaler']
                self.is_trained = data['is_trained']
