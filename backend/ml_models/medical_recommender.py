"""
Medical Recommendation System
Uses machine learning to provide personalized medical recommendations
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
import joblib
import os
from typing import Dict, List, Tuple, Any
import json

class MedicalRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        self.knn_model = NearestNeighbors(n_neighbors=5, metric='cosine')
        self.is_trained = False
        self.model_path = 'backend/ml_models/saved_models/medical_recommender.pkl'
        
        # Medical knowledge base
        self.medical_database = self._create_medical_database()
        
        # Load pre-trained model if exists
        self.load_model()
    
    def _create_medical_database(self) -> List[Dict[str, Any]]:
        """Create a comprehensive medical knowledge base"""
        
        database = [
            {
                'condition': 'Gastroenteritis',
                'symptoms': 'stomach pain nausea vomiting diarrhea abdominal cramps fever',
                'category': 'gastrointestinal',
                'severity': 'moderate',
                'recommendations': [
                    'Stay hydrated with clear fluids',
                    'Rest your stomach for several hours',
                    'Gradually reintroduce bland foods',
                    'Avoid dairy products and caffeine',
                    'Seek medical care if symptoms persist > 2 days'
                ],
                'medications': ['oral rehydration solution', 'anti-diarrheal medications', 'anti-nausea medications'],
                'lifestyle': ['hand washing', 'food safety', 'avoid contaminated water'],
                'urgency': 'medium'
            },
            {
                'condition': 'Gastroesophageal Reflux Disease (GERD)',
                'symptoms': 'heartburn chest pain acid reflux regurgitation difficulty swallowing',
                'category': 'gastrointestinal',
                'severity': 'mild_to_moderate',
                'recommendations': [
                    'Avoid trigger foods (spicy, fatty, acidic)',
                    'Eat smaller, more frequent meals',
                    'Don\'t lie down after eating',
                    'Elevate head of bed',
                    'Maintain healthy weight'
                ],
                'medications': ['antacids', 'H2 blockers', 'proton pump inhibitors'],
                'lifestyle': ['weight management', 'dietary modifications', 'stress reduction'],
                'urgency': 'low'
            },
            {
                'condition': 'Acute Bronchitis',
                'symptoms': 'cough chest congestion shortness of breath wheezing fatigue',
                'category': 'respiratory',
                'severity': 'moderate',
                'recommendations': [
                    'Get plenty of rest',
                    'Stay hydrated',
                    'Use humidifier',
                    'Avoid irritants (smoke, dust)',
                    'Try honey or lozenges for cough'
                ],
                'medications': ['cough suppressants', 'expectorants', 'pain relievers'],
                'lifestyle': ['smoking cessation', 'avoid pollutants', 'immune support'],
                'urgency': 'medium'
            },
            {
                'condition': 'Community-Acquired Pneumonia',
                'symptoms': 'cough fever chest pain shortness of breath fatigue confusion',
                'category': 'respiratory',
                'severity': 'moderate_to_severe',
                'recommendations': [
                    'Seek immediate medical attention',
                    'Complete prescribed antibiotics',
                    'Get adequate rest',
                    'Stay hydrated',
                    'Monitor fever and breathing'
                ],
                'medications': ['antibiotics', 'fever reducers', 'cough medicine'],
                'lifestyle': ['vaccination', 'hand hygiene', 'healthy lifestyle'],
                'urgency': 'high'
            },
            {
                'condition': 'Angina',
                'symptoms': 'chest pain pressure tightness shortness of breath fatigue',
                'category': 'cardiovascular',
                'severity': 'moderate_to_severe',
                'recommendations': [
                    'Seek immediate medical attention for chest pain',
                    'Take prescribed medications as directed',
                    'Avoid physical exertion during episodes',
                    'Learn to recognize warning signs',
                    'Call emergency services if pain is severe'
                ],
                'medications': ['nitroglycerin', 'beta blockers', 'calcium channel blockers', 'aspirin'],
                'lifestyle': ['heart-healthy diet', 'regular exercise', 'stress management', 'no smoking'],
                'urgency': 'high'
            },
            {
                'condition': 'Migraine',
                'symptoms': 'headache nausea sensitivity to light sensitivity to sound aura',
                'category': 'neurological',
                'severity': 'moderate_to_severe',
                'recommendations': [
                    'Rest in quiet, dark room',
                    'Apply cold compress to head',
                    'Stay hydrated',
                    'Try to identify and avoid triggers',
                    'Consider preventive medications'
                ],
                'medications': ['triptans', 'NSAIDs', 'anti-nausea medications', 'preventive medications'],
                'lifestyle': ['regular sleep schedule', 'stress management', 'trigger avoidance', 'exercise'],
                'urgency': 'medium'
            },
            {
                'condition': 'Tension Headache',
                'symptoms': 'headache neck pain shoulder tension stress fatigue',
                'category': 'neurological',
                'severity': 'mild_to_moderate',
                'recommendations': [
                    'Apply warm compress to neck/shoulders',
                    'Practice relaxation techniques',
                    'Improve posture',
                    'Get regular exercise',
                    'Ensure adequate sleep'
                ],
                'medications': ['over-the-counter pain relievers', 'muscle relaxants'],
                'lifestyle': ['stress management', 'ergonomic workspace', 'regular breaks'],
                'urgency': 'low'
            },
            {
                'condition': 'Osteoarthritis',
                'symptoms': 'joint pain stiffness swelling reduced range of motion',
                'category': 'musculoskeletal',
                'severity': 'mild_to_moderate',
                'recommendations': [
                    'Low-impact exercise (swimming, walking)',
                    'Maintain healthy weight',
                    'Physical therapy',
                    'Heat and cold therapy',
                    'Assistive devices if needed'
                ],
                'medications': ['NSAIDs', 'acetaminophen', 'topical analgesics'],
                'lifestyle': ['weight management', 'regular exercise', 'joint protection'],
                'urgency': 'low'
            },
            {
                'condition': 'Rheumatoid Arthritis',
                'symptoms': 'joint pain swelling stiffness fatigue fever weight loss',
                'category': 'musculoskeletal',
                'severity': 'moderate_to_severe',
                'recommendations': [
                    'Seek rheumatologist care',
                    'Take prescribed medications consistently',
                    'Balance rest and activity',
                    'Protect joints during daily activities',
                    'Consider assistive devices'
                ],
                'medications': ['DMARDs', 'NSAIDs', 'steroids', 'biologics'],
                'lifestyle': ['gentle exercise', 'stress management', 'joint protection'],
                'urgency': 'medium'
            },
            {
                'condition': 'Contact Dermatitis',
                'symptoms': 'skin rash itching redness swelling blisters',
                'category': 'dermatological',
                'severity': 'mild_to_moderate',
                'recommendations': [
                    'Identify and avoid irritants/allergens',
                    'Apply cool compresses',
                    'Use moisturizer frequently',
                    'Avoid scratching',
                    'Wear protective clothing'
                ],
                'medications': ['topical corticosteroids', 'antihistamines', 'moisturizers'],
                'lifestyle': ['avoid triggers', 'gentle skin care', 'protective measures'],
                'urgency': 'low'
            },
            {
                'condition': 'Influenza (Flu)',
                'symptoms': 'fever cough body aches headache fatigue sore throat',
                'category': 'general',
                'severity': 'moderate',
                'recommendations': [
                    'Get plenty of rest',
                    'Stay hydrated',
                    'Take fever reducers',
                    'Isolate to prevent spread',
                    'Seek care if symptoms worsen'
                ],
                'medications': ['antiviral medications', 'fever reducers', 'pain relievers'],
                'lifestyle': ['annual vaccination', 'hand hygiene', 'healthy lifestyle'],
                'urgency': 'medium'
            },
            {
                'condition': 'Hypertension',
                'symptoms': 'headache dizziness vision changes chest pain difficulty breathing',
                'category': 'cardiovascular',
                'severity': 'moderate',
                'recommendations': [
                    'Monitor blood pressure regularly',
                    'Take medications as prescribed',
                    'Reduce sodium intake',
                    'Exercise regularly',
                    'Manage stress'
                ],
                'medications': ['ACE inhibitors', 'beta blockers', 'diuretics', 'calcium channel blockers'],
                'lifestyle': ['low-sodium diet', 'regular exercise', 'weight management', 'stress reduction'],
                'urgency': 'medium'
            }
        ]
        
        return database
    
    def train(self):
        """Train the recommendation system"""
        print("Training Medical Recommender...")
        
        # Extract symptom descriptions
        symptom_texts = [item['symptoms'] for item in self.medical_database]
        
        # Vectorize symptoms
        self.symptom_vectors = self.vectorizer.fit_transform(symptom_texts)
        
        # Train KNN model
        self.knn_model.fit(self.symptom_vectors)
        
        self.is_trained = True
        self.save_model()
        
        print(f"Trained on {len(self.medical_database)} medical conditions")
        return True
    
    def get_recommendations(self, symptoms: Dict[str, bool], 
                          patient_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get personalized medical recommendations based on symptoms"""
        
        if not self.is_trained:
            self.train()
        
        # Create symptom text from input
        symptom_text = self._create_symptom_text(symptoms)
        
        # Vectorize input symptoms
        input_vector = self.vectorizer.transform([symptom_text])
        
        # Find similar conditions
        distances, indices = self.knn_model.kneighbors(input_vector)
        
        # Get top recommendations
        recommendations = []
        for i, idx in enumerate(indices[0]):
            if distances[0][i] < 0.8:  # Similarity threshold
                condition = self.medical_database[idx]
                recommendations.append({
                    'condition': condition['condition'],
                    'category': condition['category'],
                    'severity': condition['severity'],
                    'similarity': float(1 - distances[0][i]),
                    'recommendations': condition['recommendations'],
                    'medications': condition['medications'],
                    'lifestyle': condition['lifestyle'],
                    'urgency': condition['urgency']
                })
        
        # Sort by similarity
        recommendations.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Generate personalized advice
        personalized_advice = self._generate_personalized_advice(
            symptoms, recommendations[:3], patient_info
        )
        
        return {
            'primary_recommendations': recommendations[:3],
            'all_matches': recommendations,
            'personalized_advice': personalized_advice,
            'symptom_analysis': self._analyze_symptoms(symptoms),
            'next_steps': self._get_next_steps(recommendations[:3])
        }
    
    def _create_symptom_text(self, symptoms: Dict[str, bool]) -> str:
        """Convert symptom dictionary to text"""
        symptom_mapping = {
            'fever': 'fever',
            'cough': 'cough',
            'fatigue': 'fatigue',
            'headache': 'headache',
            'nausea': 'nausea',
            'chestPain': 'chest pain',
            'breathingDifficulty': 'breathing difficulty shortness of breath',
            'jointPain': 'joint pain'
        }
        
        symptoms_text = []
        for symptom, present in symptoms.items():
            if present and symptom in symptom_mapping:
                symptoms_text.append(symptom_mapping[symptom])
        
        return ' '.join(symptoms_text)
    
    def _generate_personalized_advice(self, symptoms: Dict[str, bool], 
                                   recommendations: List[Dict], 
                                   patient_info: Dict[str, Any] = None) -> List[str]:
        """Generate personalized medical advice"""
        
        advice = []
        
        # Age-specific advice
        if patient_info and 'age' in patient_info:
            age = patient_info['age']
            if age > 65:
                advice.append("Given your age, be extra vigilant about symptom changes")
            elif age < 18:
                advice.append("For younger patients, parental guidance is recommended")
        
        # Symptom-specific advice
        if symptoms.get('chestPain', False):
            advice.append("Chest pain always requires immediate medical evaluation")
        
        if symptoms.get('breathingDifficulty', False):
            advice.append("Breathing difficulties warrant urgent medical attention")
        
        # Multiple symptoms advice
        active_symptoms = sum(symptoms.values())
        if active_symptoms >= 3:
            advice.append("Multiple symptoms suggest a more complex condition - seek medical evaluation")
        elif active_symptoms == 0:
            advice.append("No active symptoms reported - continue monitoring your health")
        
        # Based on top recommendation
        if recommendations:
            top_condition = recommendations[0]['condition']
            urgency = recommendations[0]['urgency']
            
            if urgency == 'high':
                advice.append(f"Based on similarity to {top_condition}, seek immediate medical care")
            elif urgency == 'medium':
                advice.append(f"Consider consulting a healthcare provider about possible {top_condition}")
            else:
                advice.append(f"Symptoms suggest mild condition similar to {top_condition}")
        
        return advice
    
    def _analyze_symptoms(self, symptoms: Dict[str, bool]) -> Dict[str, Any]:
        """Analyze the provided symptoms"""
        
        active_symptoms = [symptom for symptom, present in symptoms.items() if present]
        symptom_count = len(active_symptoms)
        
        # Categorize symptoms
        categories = {
            'gastrointestinal': ['nausea'],
            'respiratory': ['cough', 'breathingDifficulty'],
            'cardiovascular': ['chestPain'],
            'neurological': ['headache'],
            'musculoskeletal': ['jointPain'],
            'general': ['fever', 'fatigue']
        }
        
        affected_categories = []
        for category, symptom_list in categories.items():
            if any(symptom in active_symptoms for symptom in symptom_list):
                affected_categories.append(category)
        
        # Determine severity indicators
        severe_symptoms = ['chestPain', 'breathingDifficulty']
        has_severe = any(symptom in active_symptoms for symptom in severe_symptoms)
        
        return {
            'active_symptoms': active_symptoms,
            'symptom_count': symptom_count,
            'affected_categories': affected_categories,
            'has_severe_symptoms': has_severe,
            'severity_level': 'high' if has_severe else 'moderate' if symptom_count >= 2 else 'low'
        }
    
    def _get_next_steps(self, recommendations: List[Dict]) -> List[str]:
        """Get recommended next steps"""
        
        if not recommendations:
            return ["Monitor symptoms and seek care if they develop or worsen"]
        
        # Get highest urgency level
        urgency_levels = [rec['urgency'] for rec in recommendations]
        highest_urgency = 'high' if 'high' in urgency_levels else 'medium' if 'medium' in urgency_levels else 'low'
        
        next_steps = {
            'high': [
                "Seek immediate medical attention",
                "Call emergency services if symptoms are severe",
                "Do not wait - get evaluated urgently"
            ],
            'medium': [
                "Schedule appointment with healthcare provider",
                "Monitor symptoms for changes",
                "Consider urgent care if symptoms worsen"
            ],
            'low': [
                "Continue home monitoring",
                "Try over-the-counter remedies if appropriate",
                "Seek care if symptoms persist > 3-5 days"
            ]
        }
        
        return next_steps.get(highest_urgency, [])
    
    def save_model(self):
        """Save the trained model"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        model_data = {
            'vectorizer': self.vectorizer,
            'knn_model': self.knn_model,
            'medical_database': self.medical_database,
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
                self.knn_model = model_data['knn_model']
                self.medical_database = model_data['medical_database']
                self.is_trained = model_data['is_trained']
                print("Loaded pre-trained medical recommender")
                return True
            except Exception as e:
                print(f"Error loading model: {e}")
                return False
        return False
