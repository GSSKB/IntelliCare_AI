"""
Risk Prediction ML Model
Uses machine learning to predict health risk levels based on symptoms
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import os
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

class RiskPredictor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.rf_model = RandomForestClassifier(n_estimators=200, random_state=42)
        self.gb_model = GradientBoostingClassifier(n_estimators=150, random_state=42)
        self.lr_model = LogisticRegression(random_state=42)
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        self.model_path = 'backend/ml_models/saved_models/risk_predictor.pkl'
        
        # Risk levels
        self.risk_levels = ['LOW', 'MEDIUM', 'HIGH']
        
        # Feature mappings
        self.symptom_severity = {
            'mild': 1, 'moderate': 2, 'severe': 3, 'very_severe': 4
        }
        
        self.symptom_duration = {
            'hours': 1, 'days': 2, 'weeks': 3, 'months': 4, 'years': 5
        }
        
        # Load pre-trained model if exists
        self.load_model()
    
    def create_training_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """Create comprehensive training data for risk prediction"""
        
        # Generate synthetic patient data with realistic patterns
        np.random.seed(42)
        n_samples = 1000
        
        data = []
        risk_labels = []
        
        for i in range(n_samples):
            # Generate random symptom combinations
            symptoms = {
                'fever': np.random.choice([0, 1], p=[0.7, 0.3]),
                'cough': np.random.choice([0, 1], p=[0.6, 0.4]),
                'fatigue': np.random.choice([0, 1], p=[0.5, 0.5]),
                'headache': np.random.choice([0, 1], p=[0.6, 0.4]),
                'nausea': np.random.choice([0, 1], p=[0.7, 0.3]),
                'chest_pain': np.random.choice([0, 1], p=[0.8, 0.2]),
                'breathing_difficulty': np.random.choice([0, 1], p=[0.85, 0.15]),
                'joint_pain': np.random.choice([0, 1], p=[0.6, 0.4])
            }
            
            # Generate other features
            age = np.random.randint(18, 80)
            gender = np.random.choice([0, 1])  # 0: male, 1: female
            severity = np.random.choice([1, 2, 3, 4], p=[0.4, 0.3, 0.2, 0.1])
            duration = np.random.choice([1, 2, 3, 4, 5], p=[0.3, 0.3, 0.2, 0.1, 0.1])
            chronic_conditions = np.random.choice([0, 1, 2, 3], p=[0.5, 0.3, 0.15, 0.05])
            
            # Calculate risk score based on medical logic with safer emergency detection
            risk_score = 0
            
            # HIGH RISK symptoms only for true emergencies
            if symptoms['chest_pain']:
                risk_score += 3
            if symptoms['breathing_difficulty']:
                risk_score += 3
            
            # MEDIUM RISK symptoms (gastrointestinal, neurological, cardiovascular)
            if symptoms['nausea']:
                risk_score += 1.5  # Gastrointestinal
            if symptoms['headache']:
                risk_score += 1    # Neurological
            if symptoms['cough']:
                risk_score += 1    # Respiratory
            if symptoms['joint_pain']:
                risk_score += 1    # Musculoskeletal
            
            # LOW RISK symptoms (general, dermatological)
            if symptoms['fever']:
                risk_score += 0.5  # General - low risk
            if symptoms['fatigue']:
                risk_score += 0.3  # General - low risk
            
            # Age factor
            if age > 65:
                risk_score += 1
            elif age > 45:
                risk_score += 0.5
            
            # Severity factor (but don't over-penalize low-risk symptoms)
            if severity >= 3 and not symptoms['fever'] and not symptoms['fatigue']:
                risk_score += (severity - 1) * 0.5
            elif severity >= 3 and (symptoms['fever'] or symptoms['fatigue']):
                risk_score += 0.2  # Less penalty for low-risk severity
            
            # Duration factor
            if duration > 3:  # weeks or months
                risk_score += 1
            
            # Chronic conditions factor
            risk_score += chronic_conditions * 0.5
            
            # Multiple symptoms factor
            symptom_count = sum(symptoms.values())
            if symptom_count >= 3:
                risk_score += 1
            elif symptom_count >= 2:
                risk_score += 0.5
            
            # Safer risk determination based on symptom types
            if risk_score >= 4:
                risk_level = 'HIGH'
            elif risk_score >= 2.5:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'
            
            # Special cases for different disease categories
            
            # Gastrointestinal: typically LOW/MEDIUM unless severe
            if symptoms['nausea'] and symptom_count == 1 and risk_score < 2:
                risk_level = 'LOW'
            elif symptoms['nausea'] and symptom_count == 1 and risk_score >= 2:
                risk_level = 'MEDIUM'
            
            # Respiratory: LOW/MEDIUM unless breathing difficulty
            if symptoms['cough'] and not symptoms['breathing_difficulty'] and symptom_count == 1:
                risk_level = 'LOW'
            elif symptoms['cough'] and not symptoms['breathing_difficulty'] and symptom_count == 2:
                risk_level = 'MEDIUM'
            
            # Neurological: LOW/MEDIUM for headache alone
            if symptoms['headache'] and symptom_count == 1 and risk_score < 2:
                risk_level = 'LOW'
            elif symptoms['headache'] and symptom_count == 1 and risk_score >= 2:
                risk_level = 'MEDIUM'
            
            # Musculoskeletal: Typically LOW unless severe
            if symptoms['joint_pain'] and symptom_count == 1:
                risk_level = 'LOW'
            elif symptoms['joint_pain'] and symptom_count == 2:
                risk_level = 'MEDIUM'
            
            # General (fever/fatigue): Always LOW unless combined with severe symptoms
            if symptoms['fever'] and symptom_count == 1:
                risk_level = 'LOW'
            elif symptoms['fatigue'] and symptom_count == 1:
                risk_level = 'LOW'
            
            # Create feature vector
            features = {
                'age': age,
                'gender': gender,
                'fever': symptoms['fever'],
                'cough': symptoms['cough'],
                'fatigue': symptoms['fatigue'],
                'headache': symptoms['headache'],
                'nausea': symptoms['nausea'],
                'chest_pain': symptoms['chest_pain'],
                'breathing_difficulty': symptoms['breathing_difficulty'],
                'joint_pain': symptoms['joint_pain'],
                'severity': severity,
                'duration': duration,
                'chronic_conditions': chronic_conditions,
                'symptom_count': symptom_count
            }
            
            data.append(features)
            risk_labels.append(risk_level)
        
        df = pd.DataFrame(data)
        labels = pd.Series(risk_labels)
        
        return df, labels
    
    def train(self):
        """Train the risk prediction models"""
        print("Training Risk Predictor...")
        
        # Create training data
        X, y = self.create_training_data()
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Train models
        self.rf_model.fit(X_train, y_train)
        self.gb_model.fit(X_train, y_train)
        self.lr_model.fit(X_train, y_train)
        
        # Evaluate models
        rf_score = self.rf_model.score(X_test, y_test)
        gb_score = self.gb_model.score(X_test, y_test)
        lr_score = self.lr_model.score(X_test, y_test)
        
        print(f"Random Forest Accuracy: {rf_score:.3f}")
        print(f"Gradient Boosting Accuracy: {gb_score:.3f}")
        print(f"Logistic Regression Accuracy: {lr_score:.3f}")
        
        # Use the best performing model
        scores = [rf_score, gb_score, lr_score]
        models = [self.rf_model, self.gb_model, self.lr_model]
        best_idx = scores.index(max(scores))
        self.model = models[best_idx]
        
        model_names = ['Random Forest', 'Gradient Boosting', 'Logistic Regression']
        print(f"Using {model_names[best_idx]} classifier")
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_scaled, y_encoded, cv=5)
        print(f"Cross-validation accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        self.is_trained = True
        self.save_model()
        
        return max(scores)
    
    def predict_risk(self, symptoms: Dict[str, bool], age: int = 30, 
                    gender: str = 'other', severity: str = 'moderate', 
                    duration: str = 'days', chronic_conditions: int = 0) -> Dict[str, Any]:
        """Predict risk level for given symptoms and patient data"""
        
        if not self.is_trained:
            self.train()
        
        # Prepare input data
        gender_encoded = 0 if gender.lower() == 'male' else 1 if gender.lower() == 'female' else 2
        severity_encoded = self.symptom_severity.get(severity.lower(), 2)
        duration_encoded = self.symptom_duration.get(duration.lower(), 2)
        
        # Create feature vector
        features = {
            'age': age,
            'gender': gender_encoded,
            'fever': int(symptoms.get('fever', False)),
            'cough': int(symptoms.get('cough', False)),
            'fatigue': int(symptoms.get('fatigue', False)),
            'headache': int(symptoms.get('headache', False)),
            'nausea': int(symptoms.get('nausea', False)),
            'chest_pain': int(symptoms.get('chestPain', False)),
            'breathing_difficulty': int(symptoms.get('breathingDifficulty', False)),
            'joint_pain': int(symptoms.get('jointPain', False)),
            'severity': severity_encoded,
            'duration': duration_encoded,
            'chronic_conditions': chronic_conditions,
            'symptom_count': sum(symptoms.values())
        }
        
        # Create DataFrame and scale
        df = pd.DataFrame([features])
        X_scaled = self.scaler.transform(df)
        
        # Get prediction
        prediction_idx = self.model.predict(X_scaled)[0]
        prediction_proba = self.model.predict_proba(X_scaled)[0]
        
        # Decode prediction
        risk_level = self.label_encoder.inverse_transform([prediction_idx])[0]
        
        # Get confidence scores
        confidence_scores = {}
        for i, level in enumerate(self.risk_levels):
            if i < len(prediction_proba):
                confidence_scores[level] = float(prediction_proba[i])
        
        # Generate recommendations
        recommendations = self._generate_risk_recommendations(risk_level, symptoms, confidence_scores[risk_level])
        
        return {
            'risk_level': risk_level,
            'confidence': float(confidence_scores[risk_level]),
            'all_probabilities': confidence_scores,
            'recommendations': recommendations,
            'risk_factors': self._identify_risk_factors(features),
            'next_steps': self._get_next_steps(risk_level)
        }
    
    def _generate_risk_recommendations(self, risk_level: str, symptoms: Dict[str, bool], confidence: float) -> List[str]:
        
        recommendations = []
        
        # Special handling for different disease categories
        
        # General (fever, fatigue) - Always conservative
        if symptoms.get('fever', False) and len([s for s in symptoms.values() if s]) == 1:
            recommendations.append("Your symptoms relate to general illness. Risk appears LOW.")
            recommendations.append("Stay hydrated and rest. Monitor temperature regularly.")
            recommendations.append("Seek medical care if symptoms worsen or persist beyond 3 days.")
            return recommendations
        
        if symptoms.get('fatigue', False) and len([s for s in symptoms.values() if s]) == 1:
            recommendations.append("Your symptoms relate to general fatigue. Risk appears LOW.")
            recommendations.append("Ensure adequate rest and maintain balanced nutrition.")
            recommendations.append("Consult healthcare provider if fatigue persists beyond 2 weeks.")
            return recommendations
        
        # Gastrointestinal symptoms
        if symptoms.get('nausea', False):
            if risk_level == 'LOW':
                recommendations.append("Your symptoms relate to mild gastrointestinal issues. Risk appears LOW.")
                recommendations.append("Stay hydrated, avoid solid foods temporarily, and rest.")
                recommendations.append("Seek medical care if vomiting persists more than 24 hours.")
            elif risk_level == 'MEDIUM':
                recommendations.append("Your symptoms relate to gastrointestinal concerns. Risk appears MEDIUM.")
                recommendations.append("Monitor closely, stay hydrated, and avoid irritating foods.")
                recommendations.append("Consult healthcare provider if symptoms worsen or persist.")
            return recommendations
        
        # Respiratory symptoms
        if symptoms.get('cough', False) and not symptoms.get('breathing_difficulty', False):
            if risk_level == 'LOW':
                recommendations.append("Your symptoms relate to mild respiratory issues. Risk appears LOW.")
                recommendations.append("Rest, stay hydrated, and consider over-the-counter cough remedies.")
                recommendations.append("Seek medical care if cough persists beyond 7 days or worsens.")
            elif risk_level == 'MEDIUM':
                recommendations.append("Your symptoms relate to respiratory concerns. Risk appears MEDIUM.")
                recommendations.append("Monitor breathing, rest, and avoid irritants.")
                recommendations.append("Consult healthcare provider if breathing becomes difficult.")
            return recommendations
        
        # Neurological symptoms
        if symptoms.get('headache', False):
            if risk_level == 'LOW':
                recommendations.append("Your symptoms relate to mild headache. Risk appears LOW.")
                recommendations.append("Rest in quiet environment, stay hydrated, and consider pain relievers.")
                recommendations.append("Seek medical care if headache is severe or accompanied by other symptoms.")
            elif risk_level == 'MEDIUM':
                recommendations.append("Your symptoms relate to headache concerns. Risk appears MEDIUM.")
                recommendations.append("Monitor symptoms, rest, and track headache patterns.")
                recommendations.append("Consult healthcare provider if headaches worsen or change.")
            return recommendations
        
        # Musculoskeletal symptoms
        if symptoms.get('joint_pain', False):
            if risk_level == 'LOW':
                recommendations.append("Your symptoms relate to mild musculoskeletal issues. Risk appears LOW.")
                recommendations.append("Rest the affected area, apply ice/heat as appropriate.")
                recommendations.append("Seek medical care if pain persists beyond 3 days or worsens.")
            elif risk_level == 'MEDIUM':
                recommendations.append("Your symptoms relate to musculoskeletal concerns. Risk appears MEDIUM.")
                recommendations.append("Avoid aggravating activities and consider gentle stretching.")
                recommendations.append("Consult healthcare provider if mobility is affected.")
            return recommendations
        
        # Emergency symptoms
        if risk_level == 'HIGH':
            recommendations.append("Seek immediate medical attention")
            if symptoms.get('chest_pain', False):
                recommendations.append("Call emergency services for chest pain")
            if symptoms.get('breathing_difficulty', False):
                recommendations.append("Emergency care needed for breathing difficulties")
            recommendations.append("Do not wait - seek professional medical help")
        
        elif risk_level == 'MEDIUM':
            recommendations.append("Consult a healthcare provider soon")
            recommendations.append("Monitor symptoms closely")
            if confidence > 0.7:
                recommendations.append("Consider urgent care if symptoms worsen")
            recommendations.append("Rest and stay hydrated")
        
        else:  # LOW
            recommendations.append("Monitor symptoms at home")
            recommendations.append("Rest and maintain hydration")
            recommendations.append("Over-the-counter medications may help")
            recommendations.append("Seek medical care if symptoms persist or worsen")
        
        return recommendations
    
    def _identify_risk_factors(self, features: Dict[str, Any]) -> List[str]:
        risk_factors = []
        
        if features['age'] > 65:
            risk_factors.append("Advanced age (65+)")
        elif features['age'] > 45:
            risk_factors.append("Middle age (45+)")
        
        if features['severity'] >= 3:
            risk_factors.append("High symptom severity")
        
        if features['duration'] >= 4:
            risk_factors.append("Prolonged symptom duration")
        
        if features['chronic_conditions'] >= 2:
            risk_factors.append("Multiple chronic conditions")
        
        if features['chest_pain']:
            risk_factors.append("Chest pain present")
        
        if features['breathing_difficulty']:
            risk_factors.append("Breathing difficulty present")
        
        if features['symptom_count'] >= 3:
            risk_factors.append("Multiple symptoms present")
        
        return risk_factors
    
    def _get_next_steps(self, risk_level: str) -> List[str]:
        """Get recommended next steps based on risk level"""
        
        next_steps = {
            'HIGH': [
                "Call emergency services (911) immediately",
                "Go to nearest emergency room",
                "Do not drive yourself if experiencing severe symptoms",
                "Have someone stay with you until help arrives"
            ],
            'MEDIUM': [
                "Schedule appointment with primary care physician",
                "Monitor symptoms for changes",
                "Consider urgent care if symptoms worsen",
                "Document symptoms and their progression"
            ],
            'LOW': [
                "Continue monitoring at home",
                "Rest and maintain hydration",
                "Use over-the-counter medications as needed",
                "Seek care if symptoms don't improve in 2-3 days"
            ]
        }
        
        return next_steps.get(risk_level, [])
    
    def save_model(self):
        """Save the trained model"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, self.model_path)
        print(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """Load a pre-trained model"""
        if os.path.exists(self.model_path):
            try:
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.label_encoder = model_data['label_encoder']
                self.is_trained = model_data['is_trained']
                print("Loaded pre-trained risk predictor")
                return True
            except Exception as e:
                print(f"Error loading model: {e}")
                return False
        return False
