"""
Symptom Classification ML Model
Uses machine learning to classify and analyze medical symptoms
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
from typing import Dict, List, Tuple, Any

class SymptomClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.nb_classifier = MultinomialNB()
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        self.model_path = 'backend/ml_models/saved_models/symptom_classifier.pkl'
        
        # Medical symptom categories
        self.categories = [
            'gastrointestinal', 'respiratory', 'cardiovascular', 
            'neurological', 'musculoskeletal', 'dermatological',
            'general', 'emergency'
        ]
        
        # Load pre-trained model if exists
        self.load_model()
    
    def create_training_data(self) -> Tuple[List[str], List[str]]:
        """Create comprehensive training data for symptom classification"""
        
        symptoms_data = [
            # Gastrointestinal - More samples with appropriate risk levels
            "stomach pain abdominal cramps nausea vomiting diarrhea constipation bloating",
            "abdominal pain stomach upset indigestion heartburn acid reflux",
            "nausea vomiting stomach pain food poisoning stomach flu",
            "diarrhea stomach cramps abdominal pain loose stools",
            "stomach discomfort gastric pain belly ache tummy pain",
            "gastrointestinal issues digestive problems stomach issues",
            "acid reflux heartburn burning sensation chest pain",
            "bloating gas abdominal distension stomach fullness",
            "constipation difficulty bowel movements stomach pain",
            "stomach ulcer gastric pain bleeding ulcer",
            "mild stomach ache indigestion gas bloating",
            "food poisoning nausea vomiting stomach cramps",
            "irritable bowel syndrome abdominal pain diarrhea",
            
            # Respiratory - More samples with appropriate risk levels
            "cough chest pain shortness of breath wheezing difficulty breathing",
            "sore throat cough congestion runny nose sinus pressure",
            "chest tightness cough breathing difficulty asthma bronchitis",
            "wheezing shortness of breath chest pain respiratory distress",
            "lung infection pneumonia cough fever chest pain",
            "bronchitis cough mucus chest congestion breathing issues",
            "asthma attack wheezing shortness of breath inhaler",
            "sinus infection sinus pressure headache congestion",
            "allergy cough sneezing itchy eyes congestion",
            "respiratory infection breathing problems lung issues",
            "mild cough sore throat congestion runny nose",
            "common cold cough sneezing stuffy nose",
            
            # Cardiovascular - More samples with appropriate risk levels
            "chest pain heart attack shortness of breath palpitations dizziness",
            "heart palpitations chest tightness irregular heartbeat arrhythmia",
            "high blood pressure chest pain heart disease cardiovascular",
            "dizziness fainting chest pain heart problems circulation",
            "heart failure shortness of breath swelling legs fatigue",
            "angina chest pain heart condition artery blockage",
            "cardiac arrest heart stop emergency chest pain",
            "irregular heartbeat arrhythmia palpitations chest discomfort",
            "heart disease cardiovascular problems chest symptoms",
            "blood pressure hypertension heart condition dizziness",
            "mild chest discomfort heart palpitations",
            "high blood pressure hypertension dizziness",
            
            # Neurological - More samples with appropriate risk levels
            "headache migraine dizziness confusion memory loss seizures",
            "severe headache migraine aura nausea sensitivity to light",
            "dizziness vertigo balance problems coordination issues",
            "memory loss confusion cognitive impairment neurological symptoms",
            "seizure convulsion epilepsy neurological brain activity",
            "stroke symptoms paralysis weakness speech difficulty",
            "neuropathy nerve pain tingling numbness neurological",
            "brain injury head trauma confusion headache",
            "migraine headache severe pain nausea sensitivity",
            "cognitive impairment memory loss confusion neurological",
            "mild headache tension headache dizziness",
            "memory issues confusion forgetfulness",
            
            # Musculoskeletal - More samples with appropriate risk levels
            "joint pain arthritis muscle pain back pain stiffness swelling",
            "back pain muscle strain joint injury arthritis rheumatism",
            "muscle pain joint stiffness swelling inflammation orthopedic",
            "bone pain fracture sprain strain musculoskeletal injury",
            "arthritis joint pain swelling stiffness inflammation",
            "back injury spinal pain muscle strain disc problems",
            "joint swelling arthritis rheumatism inflammation pain",
            "muscle strain injury pain swelling orthopedic issues",
            "bone fracture broken bone pain swelling injury",
            "musculoskeletal pain joint muscle bone issues",
            "mild muscle ache joint stiffness back pain",
            "arthritis joint pain swelling limited movement",
            
            # Dermatological - More samples with appropriate risk levels
            "skin rash itching redness swelling allergic reaction hives",
            "rash skin irritation dermatitis eczema psoriasis",
            "itching burning skin redness inflammation dermatological",
            "hives allergic reaction skin welts itching",
            "eczema dry skin rash itching inflammation",
            "psoriasis scaly skin patches redness dermatology",
            "skin infection redness swelling pus dermatological",
            "allergic reaction skin rash itching hives",
            "dermatitis skin inflammation redness itching",
            "skin condition rash irritation dermatology",
            "mild skin rash itching redness",
            "acne pimples skin irritation",
            
            # General - More samples with fever terms
            "fever fatigue weakness general malaise tiredness exhaustion",
            "fatigue tiredness weakness low energy general illness",
            "fever chills body aches general symptoms flu-like",
            "general malaise feeling unwell tired weak sick",
            "flu symptoms fever body aches fatigue headache",
            "viral infection fever fatigue general illness",
            "weakness tiredness exhaustion low energy",
            "general feeling sick unwell malaise",
            "body aches fatigue fever general symptoms",
            "tiredness weakness fatigue general illness",
            "high temperature chills fever general viral infection",
            "fever body ache chills general illness",
            "temperature fever chills body pain general",
            "fever sickness general viral symptoms",
            "fever headache body ache general illness",
            "mild fever tiredness general illness",
            
            # Emergency - More samples with appropriate risk levels
            "severe chest pain difficulty breathing emergency medical attention",
            "unconsciousness seizure stroke emergency life threatening",
            "severe bleeding trauma injury emergency room urgent care",
            "emergency medical crisis severe symptoms life threatening",
            "critical condition emergency room severe pain",
            "medical emergency urgent care severe symptoms",
            "life threatening conditions emergency medical help",
            "severe trauma injury bleeding emergency",
            "emergency situation medical crisis severe",
            "urgent medical attention emergency severe pain",
            "loss of consciousness fainting emergency",
            "stroke symptoms paralysis speech difficulty emergency"
        ]
        
        labels = [
            'gastrointestinal', 'gastrointestinal', 'gastrointestinal', 'gastrointestinal',
            'gastrointestinal', 'gastrointestinal', 'gastrointestinal', 'gastrointestinal',
            'gastrointestinal', 'gastrointestinal', 'gastrointestinal', 'gastrointestinal',
            'gastrointestinal',
            'respiratory', 'respiratory', 'respiratory', 'respiratory',
            'respiratory', 'respiratory', 'respiratory', 'respiratory',
            'respiratory', 'respiratory', 'respiratory', 'respiratory',
            'cardiovascular', 'cardiovascular', 'cardiovascular', 'cardiovascular',
            'cardiovascular', 'cardiovascular', 'cardiovascular', 'cardiovascular',
            'cardiovascular', 'cardiovascular', 'cardiovascular', 'cardiovascular',
            'neurological', 'neurological', 'neurological', 'neurological',
            'neurological', 'neurological', 'neurological', 'neurological',
            'neurological', 'neurological', 'neurological', 'neurological',
            'musculoskeletal', 'musculoskeletal', 'musculoskeletal', 'musculoskeletal',
            'musculoskeletal', 'musculoskeletal', 'musculoskeletal', 'musculoskeletal',
            'musculoskeletal', 'musculoskeletal', 'musculoskeletal', 'musculoskeletal',
            'dermatological', 'dermatological', 'dermatological', 'dermatological',
            'dermatological', 'dermatological', 'dermatological', 'dermatological',
            'dermatological', 'dermatological', 'dermatological', 'dermatological',
            'general', 'general', 'general', 'general',
            'general', 'general', 'general', 'general',
            'general', 'general', 'general', 'general',
            'general', 'general', 'general', 'general',
            'emergency', 'emergency', 'emergency', 'emergency',
            'emergency', 'emergency', 'emergency', 'emergency',
            'emergency', 'emergency', 'emergency', 'emergency'
        ]
        
        return symptoms_data, labels
    
    def train(self):
        """Train the symptom classification models"""
        print("Training Symptom Classifier...")
        
        # Create training data
        texts, labels = self.create_training_data()
        
        # Encode labels
        encoded_labels = self.label_encoder.fit_transform(labels)
        
        # Vectorize text
        X = self.vectorizer.fit_transform(texts)
        y = encoded_labels
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train Random Forest
        self.rf_classifier.fit(X_train, y_train)
        rf_pred = self.rf_classifier.predict(X_test)
        rf_accuracy = accuracy_score(y_test, rf_pred)
        
        # Train Naive Bayes
        self.nb_classifier.fit(X_train, y_train)
        nb_pred = self.nb_classifier.predict(X_test)
        nb_accuracy = accuracy_score(y_test, nb_pred)
        
        print(f"Random Forest Accuracy: {rf_accuracy:.3f}")
        print(f"Naive Bayes Accuracy: {nb_accuracy:.3f}")
        
        # Use the better performing model
        if rf_accuracy > nb_accuracy:
            self.classifier = self.rf_classifier
            print("Using Random Forest classifier")
        else:
            self.classifier = self.nb_classifier
            print("Using Naive Bayes classifier")
        
        self.is_trained = True
        self.save_model()
        
        return rf_accuracy, nb_accuracy
    
    def classify_symptom(self, symptom_text: str) -> Dict[str, Any]:
        """Classify a symptom and return detailed analysis"""
        if not self.is_trained:
            self.train()
        
        # Vectorize input
        X = self.vectorizer.transform([symptom_text])
        
        # Get prediction
        prediction_idx = self.classifier.predict(X)[0]
        prediction_proba = self.classifier.predict_proba(X)[0]
        
        # Decode label
        category = self.label_encoder.inverse_transform([prediction_idx])[0]
        
        # Get confidence scores for all categories
        confidence_scores = {}
        for i, cat in enumerate(self.categories):
            if i < len(prediction_proba):
                confidence_scores[cat] = float(prediction_proba[i])
        
        # Apply confidence threshold: if < 40%, default to 'general'
        confidence = float(confidence_scores[category])
        if confidence < 0.4:
            category = 'general'
            confidence = max(confidence_scores.get('general', 0), 0.5)  # Give general a minimum confidence
        
        # Determine urgency
        urgency = self._determine_urgency(category, confidence)
        
        return {
            'category': category,
            'confidence': confidence,
            'all_scores': confidence_scores,
            'urgency': urgency,
            'recommendations': self._get_recommendations(category)
        }
    
    def _determine_urgency(self, category: str, confidence: float) -> str:
        """Determine urgency level based on category and confidence"""
        # Only emergency category triggers high urgency
        if category == 'emergency':
            return 'high'
        # Cardiovascular and respiratory only high with high confidence
        elif category in ['cardiovascular', 'respiratory'] and confidence > 0.7:
            return 'high'
        # Medium urgency for specific categories with moderate confidence
        elif category in ['gastrointestinal', 'neurological'] and confidence > 0.5:
            return 'medium'
        # General category is low urgency
        elif category == 'general':
            return 'low'
        else:
            return 'low'
    
    def _get_recommendations(self, category: str) -> List[str]:
        """Get medical recommendations based on symptom category"""
        recommendations = {
            'gastrointestinal': [
                "Stay hydrated and avoid solid foods for a few hours",
                "Consider over-the-counter antacids for mild symptoms",
                "Seek medical attention if symptoms persist more than 2 days"
            ],
            'respiratory': [
                "Rest and stay hydrated",
                "Use a humidifier to ease breathing",
                "Seek immediate care if breathing becomes difficult"
            ],
            'cardiovascular': [
                "Seek immediate medical attention for chest pain",
                "Call emergency services if pain is severe or persistent",
                "Monitor blood pressure if you have a history of heart issues"
            ],
            'neurological': [
                "Rest in a quiet, dark room for headaches",
                "Seek immediate care for sudden severe headaches",
                "Monitor for changes in consciousness or coordination"
            ],
            'musculoskeletal': [
                "Rest the affected area",
                "Apply ice to reduce swelling",
                "Seek medical care for severe pain or inability to move"
            ],
            'dermatological': [
                "Avoid scratching affected areas",
                "Apply cool compresses to reduce itching",
                "Seek medical care for widespread or worsening rashes"
            ],
            'general': [
                "Rest and stay hydrated",
                "Monitor symptoms closely",
                "Seek medical care if symptoms worsen or persist"
            ],
            'emergency': [
                "Call emergency services immediately",
                "Do not wait - seek immediate medical attention",
                "Follow emergency dispatcher instructions"
            ]
        }
        
        return recommendations.get(category, ["Consult a healthcare provider"])
    
    def save_model(self):
        """Save the trained model"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        model_data = {
            'vectorizer': self.vectorizer,
            'classifier': self.classifier,
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
                self.vectorizer = model_data['vectorizer']
                self.classifier = model_data['classifier']
                self.label_encoder = model_data['label_encoder']
                self.is_trained = model_data['is_trained']
                print("Loaded pre-trained symptom classifier")
                return True
            except Exception as e:
                print(f"Error loading model: {e}")
                return False
        return False
