import os
import requests
import json
import re
from typing import List
from rag_service import RAGService
from ml_models.symptom_classifier import SymptomClassifier
from ml_models.risk_predictor import RiskPredictor
from ml_models.medical_recommender import MedicalRecommender
from ml_models.nlp_processor import NLPProcessor

class ChatService:
    def __init__(self):
        self.rag_service = RAGService()
        
        # Initialize ML models
        self.symptom_classifier = SymptomClassifier()
        self.risk_predictor = RiskPredictor()
        self.medical_recommender = MedicalRecommender()
        self.nlp_processor = NLPProcessor()
        
        print("ML models initialized")
        
    def get_response(self, message: str) -> str:
        message_lower = message.lower()
        
        # Handle natural conversation (always allow)
        if message_lower in ['hi', 'hello', 'hey', 'greetings', 'how are you', 'how are you doing', 
                            'thanks', 'thank you', 'thank', 'bye', 'goodbye', 'see you', 
                            'what can you do', 'help me']:
            return self._get_contextual_response(message)
        
        # ALWAYS check RAG first for all medical queries
        # Check if data exists in RAG file (symptoms OR disease names)
        if not self._check_rag_data_available(message):
            return "No data found"
        
        # Get RAG context - this will retrieve relevant medical records
        context = self.rag_service.search(message)
        print(f"RAG retrieved context: {len(context)} characters")
        
        # Check if Google API key is available and valid
        api_key = os.getenv("GOOGLE_API_KEY")
        print(f"Google API key check: {api_key[:10]}..." if api_key and len(api_key) > 10 else "No Google API key found")
        
        # ALWAYS prefer LLM with RAG for all queries if API key is available
        if api_key and api_key.startswith("AIza"):
            try:
                print("Using Google AI with RAG context...")
                return self._get_google_ai_response(message, context)
            except Exception as e:
                print(f"Google AI API error: {e}")
                # Fallback: return "No data found" if LLM fails and no RAG data
                return "No data found"
        else:
            # If no API key, use ML models with RAG context
            try:
                print("Using ML models with RAG context...")
                return self._get_contextual_response(message, context)
            except Exception as e:
                print(f"ML models error: {e}")
                return "No data found"
    
    def _get_google_ai_response(self, message: str, context: str) -> str:
        # Check if data exists in RAG file (symptoms OR disease names)
        if not self._check_rag_data_available(message):
            return "No data found"
        
        api_key = os.getenv("GOOGLE_API_KEY")
        
        # Test the API key validity first
        test_url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
        
        try:
            # Test if API key works
            response = requests.get(test_url)
            if response.status_code != 200:
                raise Exception(f"API key validation failed: {response.status_code}")
            
            # Using Google Generative AI API (Gemini) - use working model
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        except Exception as e:
            print(f"API validation error: {e}")
            raise Exception("Google AI API key or endpoint issue")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        # Get relevant documents from RAG
        relevant_docs = self.rag_service.get_relevant_documents(message, top_k=5)
        rag_context = "\n".join([f"- {doc}" for doc in relevant_docs]) if relevant_docs else context
        
        # Extract similar cases for the response
        similar_cases = self._extract_similar_cases(relevant_docs)
        
        # Determine the type of response needed based on question type
        message_lower = message.lower()
        
        # Risk Assessment Questions
        if any(phrase in message_lower for phrase in ["analyze these symptoms", "risk assessment", "how severe", "low, medium, or high risk", "should i seek medical attention", "is difficulty breathing always high risk", "should i go to the er", "is chest pain dangerous", "when is fever considered an emergency"]):
            prompt = f"""You are a medical AI assistant with access to a database of medical records. Analyze the symptoms and provide a risk assessment.

User Query: {message}

Relevant Medical Records from Database:
{rag_context}

Based on the medical records above, provide a risk assessment in this EXACT format:

[RISK LEVEL] RISK - [brief explanation based on similar cases]

Then format your response using bullet points:

• [Key point 1]
• [Key point 2]
• [Key point 3]

Similar Cases
{similar_cases}

Disclaimer
• AI-generated result based on similar cases
• Consult a healthcare professional for diagnosis

IMPORTANT: Use ONLY information from the medical records provided. If no relevant cases match, state that clearly."""
        
        # Disease Information Questions
        elif any(phrase in message_lower for phrase in ["what is", "explain symptoms of", "what happens when someone has", "what are common signs of", "difference between", "how is", "what does", "explain"]):
            prompt = f"""You are a medical AI assistant with access to a database of medical records. Answer the question using information from the database.

User Query: {message}

Relevant Medical Records from Database:
{rag_context}

Format your response using bullet points:

• [Key information point 1]
• [Key information point 2]
• [Key information point 3]

Similar Cases
{similar_cases}

Disclaimer
• AI-generated result based on similar cases
• Consult a healthcare professional for diagnosis

IMPORTANT: Use ONLY information from the medical records provided. Reference specific diseases and symptoms from the database when relevant."""
        
        # Similar Case Lookup Questions
        elif any(phrase in message_lower for phrase in ["show me similar", "similar cases", "what cases resemble", "have there been patients", "show similar medical cases"]):
            prompt = f"""You are a medical AI assistant with access to a database of medical records. Show similar cases based on the query.

User Query: {message}

Relevant Medical Records from Database:
{rag_context}

Format your response using bullet points:

Similar Cases
{similar_cases}

Analysis
• [Analysis point 1 based on similar cases]
• [Analysis point 2]
• [Analysis point 3]

Disclaimer
• AI-generated result based on similar cases
• Consult a healthcare professional for diagnosis

IMPORTANT: Use ONLY information from the medical records provided."""
        
        # Recommendation / Home Care Questions
        elif any(phrase in message_lower for phrase in ["what should i do", "how do i manage", "what are the first steps", "should i take medication", "how can i prevent", "what foods help", "how to reduce"]):
            prompt = f"""You are a medical AI assistant with access to a database of medical records. Provide recommendations based on the query.

User Query: {message}

Relevant Medical Records from Database:
{rag_context}

Format your response using bullet points:

Recommendations
• [Recommendation 1]
• [Recommendation 2]
• [Recommendation 3]

Similar Cases
{similar_cases}

Disclaimer
• AI-generated result based on similar cases
• Consult a healthcare professional for diagnosis

IMPORTANT: Use ONLY information from the medical records provided. Base recommendations on similar cases in the database."""
        
        # Outcome-based Questions
        elif any(phrase in message_lower for phrase in ["what happens if", "are these symptoms usually", "do patients with", "often recover", "outcome"]):
            prompt = f"""You are a medical AI assistant with access to a database of medical records. Answer based on outcomes in the database.

User Query: {message}

Relevant Medical Records from Database:
{rag_context}

Format your response using bullet points:

• [Outcome information point 1]
• [Outcome information point 2]
• [Outcome information point 3]

Similar Cases
{similar_cases}

Disclaimer
• AI-generated result based on similar cases
• Consult a healthcare professional for diagnosis

IMPORTANT: Use ONLY information from the medical records provided. Reference specific outcomes (Positive/Negative) from the database."""
        
        # Age & Gender Specific Questions
        elif any(phrase in message_lower for phrase in ["i'm", "i am", "for kids", "affect females", "affect males", "age", "gender"]):
            prompt = f"""You are a medical AI assistant with access to a database of medical records. Provide personalized information based on age and gender.

User Query: {message}

Relevant Medical Records from Database:
{rag_context}

Format your response using bullet points:

• [Personalized information point 1]
• [Personalized information point 2]
• [Personalized information point 3]

Similar Cases
{similar_cases}

Disclaimer
• AI-generated result based on similar cases
• Consult a healthcare professional for diagnosis

IMPORTANT: Use ONLY information from the medical records provided. Reference age and gender patterns from the database when relevant."""
        
        # General Medical Questions (default)
        else:
            prompt = f"""You are a medical AI assistant with access to a database of medical records. Answer the question using information from the database.

User Query: {message}

Relevant Medical Records from Database:
{rag_context}

Format your response using bullet points:

• [Key information point 1]
• [Key information point 2]
• [Key information point 3]

Similar Cases
{similar_cases}

Disclaimer
• AI-generated result based on similar cases
• Consult a healthcare professional for diagnosis

IMPORTANT: Use ONLY information from the medical records provided. If the database doesn't contain relevant information, state "No data found" clearly."""
        
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1500,
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        if 'candidates' in result and len(result['candidates']) > 0:
            llm_response = result['candidates'][0]['content']['parts'][0]['text']
            # Ensure response includes similar cases and disclaimer if not already present
            if "Similar Cases" not in llm_response:
                llm_response += f"\n\nSimilar Cases\n{similar_cases}\n\nDisclaimer\n• AI-generated result based on similar cases\n• Consult a healthcare professional for diagnosis"
            return llm_response
        else:
            raise Exception("No response from Google AI")
    
    def _extract_similar_cases(self, relevant_docs: List[str]) -> str:
        """Extract and format similar cases from RAG documents"""
        if not relevant_docs or len(relevant_docs) == 0:
            return "• No similar cases found in database"
        
        cases_info = []
        for doc in relevant_docs[:3]:  # Top 3 cases
            if "Disease:" in doc:
                try:
                    disease_part = doc.split("Disease:")[1].split(".")[0].strip()
                    symptoms_part = ""
                    if "Symptoms:" in doc:
                        symptoms_part = doc.split("Symptoms:")[1].split("Age:")[0].strip()
                    
                    if disease_part:
                        cases_info.append({
                            'disease': disease_part,
                            'symptoms': symptoms_part
                        })
                except Exception as e:
                    pass
        
        if not cases_info:
            return "• No similar cases found in database"
        
        formatted_cases = ""
        for case in cases_info:
            symptoms_list = []
            if case['symptoms']:
                symptoms_text = case['symptoms']
                symptom_pattern = r'(\w+(?:\s+\w+)?)\s*\(Yes\)'
                matches = re.findall(symptom_pattern, symptoms_text)
                for match in matches:
                    symptom_name = match.strip()
                    if symptom_name not in ['Yes', 'No']:
                        symptoms_list.append(symptom_name)
                
                if not symptoms_list:
                    if "Fever (Yes)" in symptoms_text: symptoms_list.append("Fever")
                    if "Cough (Yes)" in symptoms_text: symptoms_list.append("Cough")
                    if "Fatigue (Yes)" in symptoms_text: symptoms_list.append("Fatigue")
                    if "Difficulty Breathing (Yes)" in symptoms_text or "Breathing (Yes)" in symptoms_text:
                        symptoms_list.append("Breathing Issues")
            
            symptoms_str = ", ".join(symptoms_list) if symptoms_list else "N/A"
            formatted_cases += f"• {case['disease']} — {symptoms_str}\n"
        
        return formatted_cases.strip()
    
    def _extract_symptom_names(self, message: str, nlp_result: dict) -> List[str]:
        """Extract symptom names from message"""
        message_lower = message.lower()
        symptoms_found = []
        
        symptom_keywords = {
            'fever': ['fever', 'feverish', 'temperature'],
            'cough': ['cough', 'coughing'],
            'headache': ['headache', 'head pain', 'head ache'],
            'nausea': ['nausea', 'nauseous', 'queasy'],
            'chest pain': ['chest pain', 'chest discomfort'],
            'breathing difficulty': ['breathing difficulty', 'shortness of breath', 'can\'t breathe', 'breathless'],
            'joint pain': ['joint pain', 'joint ache'],
            'muscle pain': ['muscle pain', 'muscle ache', 'muscle soreness', 'muscular pain'],
            'fatigue': ['fatigue', 'tired', 'exhausted', 'weak']
        }
        
        for symptom_name, keywords in symptom_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                symptoms_found.append(symptom_name.title())
        
        # Also check extracted symptoms from NLP
        if nlp_result.get('symptom_analysis', {}).get('extracted_symptoms'):
            extracted = nlp_result['symptom_analysis']['extracted_symptoms']
            for symptom_key, present in extracted.items():
                if present and symptom_key.replace('_', ' ').title() not in symptoms_found:
                    symptoms_found.append(symptom_key.replace('_', ' ').title())
        
        return symptoms_found if symptoms_found else ["General symptoms"]
    
    def _format_symptom_response(self, symptoms: List[str], category: str, risk_level: str, 
                                 confidence: float, recommendations: List[str]) -> str:
        """Format symptom analysis response in consistent structure"""
        symptoms_str = ", ".join(symptoms) if symptoms else "General symptoms"
        category_display = category.replace('_', ' ').title()
        
        response = f"""Symptom Analysis
• Symptoms: {symptoms_str}
• Category: {category_display}
• Risk Level: {risk_level.upper()}

Recommendations"""
        
        for rec in recommendations:
            response += f"\n• {rec}"
        
        return response
    
    def _enhance_with_rag_context(self, base_response: str, relevant_docs: List[str]) -> str:
        """Enhance ML response with relevant medical records from RAG - ALWAYS includes disclaimer"""
        # Always build enhancement section, even if no relevant docs found
        enhancement = "\n\nSimilar Cases\n"
        
        if relevant_docs and len(relevant_docs) > 0:
            # Extract disease names, symptoms, and outcomes from relevant documents
            cases_info = []
            
            for doc in relevant_docs[:5]:  # Use top 5 most relevant
                if "Disease:" in doc:
                    try:
                        # Parse disease name
                        disease_part = doc.split("Disease:")[1].split(".")[0].strip()
                        
                        # Parse symptoms
                        symptoms_part = ""
                        if "Symptoms:" in doc:
                            symptoms_part = doc.split("Symptoms:")[1].split("Age:")[0].strip()
                        
                        if disease_part:
                            cases_info.append({
                                'disease': disease_part,
                                'symptoms': symptoms_part
                            })
                    except Exception as e:
                        pass
            
            if cases_info:
                for i, case in enumerate(cases_info[:3], 1):
                    # Parse symptoms from the symptoms_part string - extract all symptoms
                    symptoms_list = []
                    if case['symptoms']:
                        symptoms_text = case['symptoms']
                        # Extract all symptoms in format "Symptom (Yes/No)"
                        symptom_pattern = r'(\w+(?:\s+\w+)?)\s*\(Yes\)'
                        matches = re.findall(symptom_pattern, symptoms_text)
                        for match in matches:
                            symptom_name = match.strip()
                            if symptom_name not in ['Yes', 'No']:
                                symptoms_list.append(symptom_name)
                        
                        # If no matches found, try alternative parsing
                        if not symptoms_list:
                            # Fallback: extract common symptoms
                            if "Fever (Yes)" in symptoms_text:
                                symptoms_list.append("Fever")
                            if "Cough (Yes)" in symptoms_text:
                                symptoms_list.append("Cough")
                            if "Fatigue (Yes)" in symptoms_text:
                                symptoms_list.append("Fatigue")
                            if "Difficulty Breathing (Yes)" in symptoms_text or "Breathing (Yes)" in symptoms_text:
                                symptoms_list.append("Breathing Issues")
                            if "Headache (Yes)" in symptoms_text:
                                symptoms_list.append("Headache")
                            if "Nausea (Yes)" in symptoms_text:
                                symptoms_list.append("Nausea")
                            if "Joint Pain (Yes)" in symptoms_text:
                                symptoms_list.append("Joint Pain")
                            if "Stomach Pain (Yes)" in symptoms_text or "Stomach (Yes)" in symptoms_text:
                                symptoms_list.append("Stomach Pain")
                            if "Back Pain (Yes)" in symptoms_text or "Back (Yes)" in symptoms_text:
                                symptoms_list.append("Back Pain")
                    
                    # Format as bullet point: "• Disease — Symptom1, Symptom2"
                    symptoms_str = ", ".join(symptoms_list) if symptoms_list else "N/A"
                    enhancement += f"• {case['disease']} — {symptoms_str}\n"
            else:
                enhancement += "• No similar cases found in database\n"
        else:
            enhancement += "• No similar cases found in database\n"
        
        # ALWAYS include disclaimer
        enhancement += "\nDisclaimer\n"
        enhancement += "• AI-generated result based on similar cases\n"
        enhancement += "• Consult a healthcare professional for diagnosis"
        
        return enhancement
    
    def _check_rag_symptoms_available(self, message: str) -> bool:
        """Check if the symptoms mentioned in the query are in the RAG file"""
        message_lower = message.lower()
        
        # RAG file only contains these 4 symptoms
        rag_symptoms = ['fever', 'cough', 'fatigue', 'difficulty breathing', 'breathing difficulty', 
                       'breathing', 'shortness of breath', 'can\'t breathe', 'breathless']
        
        # Check if message contains any RAG-supported symptoms
        for symptom in rag_symptoms:
            if symptom in message_lower:
                return True
        
        return False
    
    def _check_rag_data_available(self, message: str) -> bool:
        """Check if relevant data exists in RAG file for the query (symptoms OR disease names)"""
        message_lower = message.lower()
        
        # First check if query contains RAG-supported symptoms
        rag_symptoms = ['fever', 'cough', 'fatigue', 'difficulty breathing', 'breathing difficulty', 
                       'breathing', 'shortness of breath', 'can\'t breathe', 'breathless']
        has_rag_symptom = any(symptom in message_lower for symptom in rag_symptoms)
        
        # If query mentions a symptom that's NOT RAG-supported, reject it immediately
        non_rag_symptoms = ['headache', 'head pain', 'head ache', 'nausea', 'nauseous', 'muscle pain', 
                           'muscle ache', 'joint pain', 'chest pain', 'stomach pain', 'back pain',
                           'dizziness', 'vomiting', 'diarrhea', 'constipation', 'rash', 'itchy']
        mentions_non_rag_symptom = any(symptom in message_lower for symptom in non_rag_symptoms)
        
        if mentions_non_rag_symptom and not has_rag_symptom:
            # Query mentions a symptom that's NOT in RAG file
            return False
        
        # Get relevant documents from RAG
        relevant_docs = self.rag_service.get_relevant_documents(message, top_k=5)
        
        # Check if we have any relevant documents with disease information
        if not relevant_docs or len(relevant_docs) == 0:
            return False
        
        # Check if any document contains disease information
        has_disease_data = False
        for doc in relevant_docs:
            if "Disease:" in doc:
                has_disease_data = True
                # If query contains RAG-supported symptoms, allow it
                if has_rag_symptom:
                    return True
                # Otherwise, check if it's a disease name query
                # Extract potential disease name from query (words longer than 3 chars)
                query_words = [w for w in message_lower.split() if len(w) > 3]
                doc_lower = doc.lower()
                # Check if any query word appears in the disease name
                disease_match = re.search(r'disease:\s*([^.]+)', doc_lower, re.IGNORECASE)
                if disease_match:
                    disease_name = disease_match.group(1).strip().lower()
                    # Check if any significant query word matches the disease name
                    for word in query_words:
                        if word in disease_name or disease_name in word:
                            return True
        
        # Only return True if we have disease data AND either RAG symptoms or matched disease name
        return has_disease_data
    
    def _get_contextual_response(self, message: str, rag_context: str = None) -> str:
        """Generate ML-powered contextual responses with RAG context"""
        message_lower = message.lower()
        
        # Handle natural conversation (always allow)
        if message_lower in ['hi', 'hello', 'hey', 'greetings']:
            return "Hello! I'm here to help with your health and medical questions using advanced AI and machine learning. How can I assist you today?"
        elif message_lower in ['how are you', 'how are you doing']:
            return "I'm functioning optimally with my machine learning models ready to provide accurate medical insights. How can I help you?"
        elif message_lower in ['thanks', 'thank you', 'thank']:
            return "You're welcome! Is there anything else I can help you with regarding your health?"
        elif message_lower in ['bye', 'goodbye', 'see you']:
            return "Goodbye! Remember to take care of your health and don't hesitate to reach out if you have any medical questions."
        elif 'what can you do' in message_lower or 'help me' in message_lower:
            return "I can provide ML-powered symptom analysis, risk assessment, medical recommendations, and personalized health insights. All my predictions are based on trained machine learning models."
        
        # Check if data exists in RAG file (symptoms OR disease names)
        if not self._check_rag_data_available(message):
            return "No data found. I don't find the data related to your query in my database. Please try asking about symptoms (Fever, Cough, Fatigue, Difficulty Breathing) or diseases that are available in my knowledge base."
        
        # Get RAG context if not provided
        if rag_context is None:
            rag_context = self.rag_service.search(message)
        
        # Get relevant documents for enhanced responses
        relevant_docs = self.rag_service.get_relevant_documents(message, top_k=5)
        
        # Handle risk assessment prompts using ML models
        if "analyze these symptoms:" in message_lower or "risk assessment" in message_lower:
            response = self._ml_risk_assessment(message)
            # ALWAYS enhance with RAG context (includes disclaimer)
            response += self._enhance_with_rag_context(response, relevant_docs or [])
            return response
        
        # Handle symptom queries using ML (for RAG-supported symptoms)
        elif any(symptom in message_lower for symptom in ['fever', 'cough', 'breathing difficulty', 'breathing', 'fatigue']):
            response = self._ml_symptom_analysis(message, relevant_docs)
            return response
        
        # Handle search queries using ML recommender
        elif "what is" in message_lower or "provide" in message_lower and "information" in message_lower:
            return self._ml_medical_information(message)
        else:
            # Use ML for general medical queries
            return self._ml_general_query(message)
    
    def _ml_risk_assessment(self, message: str) -> str:
        """Use ML models for risk assessment"""
        try:
            # Extract symptoms using NLP
            nlp_result = self.nlp_processor.analyze_medical_query(message)
            symptoms = nlp_result['symptom_analysis']['extracted_symptoms']
            
            # Normalize symptoms
            normalized_symptoms = self.nlp_processor.normalize_symptoms(symptoms)
            
            # Use ML risk predictor
            risk_result = self.risk_predictor.predict_risk(normalized_symptoms)
            
            # Format response
            risk_level = risk_result['risk_level']
            confidence = risk_result['confidence']
            
            response = f"{risk_level} RISK - "
            
            # Add ML-generated recommendations
            if risk_result['recommendations']:
                response += risk_result['recommendations'][0]
            
            return response
            
        except Exception as e:
            print(f"ML risk assessment error: {e}")
            return "MEDIUM RISK - ML model temporarily unavailable. Monitor symptoms and consult healthcare provider if concerned."
    
    def _ml_symptom_analysis(self, message: str, relevant_docs: List[str] = None) -> str:
        """Use ML for symptom analysis with RAG context"""
        # Check if relevant docs exist
        if not relevant_docs or len(relevant_docs) == 0:
            return "No data found. I don't find the data related to your query in my database. Please try asking about symptoms (Fever, Cough, Fatigue, Difficulty Breathing) or diseases that are available in my knowledge base."
        
        # Check if any document contains disease information
        has_disease_data = any("Disease:" in doc for doc in relevant_docs)
        if not has_disease_data:
            return "No data found. I don't find the data related to your query in my database. Please try asking about symptoms (Fever, Cough, Fatigue, Difficulty Breathing) or diseases that are available in my knowledge base."
        
        try:
            # Classify symptoms
            classification = self.symptom_classifier.classify_symptom(message)
            
            # Get recommendations
            nlp_result = self.nlp_processor.analyze_medical_query(message)
            symptoms = nlp_result['symptom_analysis']['extracted_symptoms']
            normalized_symptoms = self.nlp_processor.normalize_symptoms(symptoms)
            
            # Format response
            category = classification['category']
            confidence = classification['confidence']
            urgency = classification['urgency']
            
            # Special handling for different disease categories
            message_lower = message.lower()
            
            # Handle fever + cough combination (common respiratory illness)
            if 'fever' in message_lower and 'cough' in message_lower:
                risk_result = self.risk_predictor.predict_risk(normalized_symptoms)
                risk_level = risk_result['risk_level']
                base_response = f"""Symptom Analysis
• Symptoms: Fever, Cough
• Category: Respiratory Illness
• Risk Level: {risk_level.upper()}

Recommendations
• Rest and stay hydrated
• Monitor symptoms
• Seek care if symptoms worsen or last more than 7 days
• Seek urgent help if you develop difficulty breathing"""
                # ALWAYS enhance with RAG context (includes disclaimer)
                base_response += self._enhance_with_rag_context(base_response, relevant_docs or [])
                return base_response
            
            # General category (fever, fatigue)
            if category == 'general' and ('fever' in message_lower or 'fatigue' in message_lower):
                risk_result = self.risk_predictor.predict_risk(normalized_symptoms)
                risk_level = risk_result['risk_level']
                symptoms_list = self._extract_symptom_names(message, nlp_result)
                
                if 'fever' in message_lower:
                    recommendations = [
                        "Stay hydrated and rest",
                        "Monitor symptoms",
                        "Seek care if symptoms worsen or persist beyond 3 days"
                    ]
                else:  # fatigue
                    recommendations = [
                        "Ensure adequate rest and maintain balanced nutrition",
                        "Monitor energy levels",
                        "Consult healthcare provider if fatigue persists beyond 2 weeks"
                    ]
                
                base_response = self._format_symptom_response(
                    symptoms_list, category, risk_level, confidence, recommendations
                )
                # ALWAYS enhance with RAG context (includes disclaimer)
                base_response += self._enhance_with_rag_context(base_response, relevant_docs or [])
                return base_response
            
            # Gastrointestinal
            elif category == 'gastrointestinal' and ('nausea' in message_lower or 'stomach' in message_lower):
                risk_result = self.risk_predictor.predict_risk(normalized_symptoms)
                risk_level = risk_result['risk_level']
                symptoms_list = self._extract_symptom_names(message, nlp_result)
                
                if risk_level == 'LOW':
                    recommendations = [
                        "Stay hydrated, avoid solid foods temporarily",
                        "Rest and monitor symptoms",
                        "Seek medical care if vomiting persists more than 24 hours"
                    ]
                else:
                    recommendations = [
                        "Monitor closely and stay hydrated",
                        "Avoid irritating foods",
                        "Consult healthcare provider if symptoms worsen or persist"
                    ]
                
                base_response = self._format_symptom_response(
                    symptoms_list, category, risk_level, confidence, recommendations
                )
                # ALWAYS enhance with RAG context (includes disclaimer)
                base_response += self._enhance_with_rag_context(base_response, relevant_docs or [])
                return base_response
            
            # Respiratory
            elif category == 'respiratory' and 'cough' in message_lower and 'breathing' not in message_lower:
                risk_result = self.risk_predictor.predict_risk(normalized_symptoms)
                risk_level = risk_result['risk_level']
                symptoms_list = self._extract_symptom_names(message, nlp_result)
                
                if risk_level == 'LOW':
                    recommendations = [
                        "Rest and stay hydrated",
                        "Consider over-the-counter cough remedies",
                        "Seek medical care if cough persists beyond 7 days or worsens"
                    ]
                else:
                    recommendations = [
                        "Monitor breathing and rest",
                        "Avoid irritants",
                        "Consult healthcare provider if breathing becomes difficult"
                    ]
                
                base_response = self._format_symptom_response(
                    symptoms_list, category, risk_level, confidence, recommendations
                )
                # ALWAYS enhance with RAG context (includes disclaimer)
                base_response += self._enhance_with_rag_context(base_response, relevant_docs or [])
                return base_response
            
            # Neurological
            elif category == 'neurological' and 'headache' in message_lower:
                risk_result = self.risk_predictor.predict_risk(normalized_symptoms)
                risk_level = risk_result['risk_level']
                symptoms_list = self._extract_symptom_names(message, nlp_result)
                
                if risk_level == 'LOW':
                    recommendations = [
                        "Rest in quiet environment and stay hydrated",
                        "Consider pain relievers if appropriate",
                        "Seek medical care if headache is severe or accompanied by other symptoms"
                    ]
                else:
                    recommendations = [
                        "Monitor symptoms and rest",
                        "Track headache patterns",
                        "Consult healthcare provider if headaches worsen or change"
                    ]
                
                base_response = self._format_symptom_response(
                    symptoms_list, category, risk_level, confidence, recommendations
                )
                # ALWAYS enhance with RAG context (includes disclaimer)
                base_response += self._enhance_with_rag_context(base_response, relevant_docs or [])
                return base_response
            
            # Musculoskeletal
            elif category == 'musculoskeletal' and ('joint' in message_lower or 'muscle' in message_lower or 'back' in message_lower):
                risk_result = self.risk_predictor.predict_risk(normalized_symptoms)
                risk_level = risk_result['risk_level']
                symptoms_list = self._extract_symptom_names(message, nlp_result)
                
                if 'muscle' in message_lower:
                    if risk_level == 'LOW':
                        recommendations = [
                            "Rest the affected muscle and avoid strenuous activity",
                            "Apply ice/heat as appropriate",
                            "Gentle stretching may help after initial rest",
                            "Seek medical care if pain persists beyond 3 days or worsens"
                        ]
                    else:
                        recommendations = [
                            "Rest and avoid aggravating activities",
                            "Apply ice/heat and consider gentle stretching",
                            "Consult healthcare provider if mobility is affected or pain is severe"
                        ]
                else:
                    if risk_level == 'LOW':
                        recommendations = [
                            "Rest the affected area",
                            "Apply ice/heat as appropriate",
                            "Seek medical care if pain persists beyond 3 days or worsens"
                        ]
                    else:
                        recommendations = [
                            "Avoid aggravating activities",
                            "Consider gentle stretching",
                            "Consult healthcare provider if mobility is affected"
                        ]
                
                base_response = self._format_symptom_response(
                    symptoms_list, category, risk_level, confidence, recommendations
                )
                # ALWAYS enhance with RAG context (includes disclaimer)
                base_response += self._enhance_with_rag_context(base_response, relevant_docs or [])
                return base_response
            
            # Emergency symptoms
            elif category == 'emergency' or ('chest pain' in message_lower or 'breathing difficulty' in message_lower):
                symptoms_list = self._extract_symptom_names(message, nlp_result)
                recommendations = [
                    "Seek immediate medical attention",
                    "Call emergency services",
                    "Do not wait - seek professional medical help"
                ]
                base_response = self._format_symptom_response(
                    symptoms_list, category, "HIGH", confidence, recommendations
                )
                # ALWAYS enhance with RAG context (includes disclaimer)
                base_response += self._enhance_with_rag_context(base_response, relevant_docs or [])
                return base_response
            
            # Use risk predictor for other symptoms (fallback for any unhandled cases)
            risk_result = self.risk_predictor.predict_risk(normalized_symptoms)
            risk_level = risk_result['risk_level']
            symptoms_list = self._extract_symptom_names(message, nlp_result)
            
            # Get recommendations
            recommendations = []
            if risk_result.get('recommendations'):
                recommendations = risk_result['recommendations']
            else:
                recommendations = [
                    "Monitor symptoms closely",
                    "Rest and stay hydrated",
                    "Consult healthcare provider if symptoms persist or worsen"
                ]
            
            base_response = self._format_symptom_response(
                symptoms_list, category, risk_level, confidence, recommendations
            )
            
            # ALWAYS enhance with RAG context (includes disclaimer)
            base_response += self._enhance_with_rag_context(base_response, relevant_docs or [])
            
            return base_response
            
        except Exception as e:
            print(f"ML symptom analysis error: {e}")
            return "I'm experiencing difficulty with my ML analysis. Please consult a healthcare provider for accurate medical advice."
    
    def _ml_medical_information(self, message: str) -> str:
        """Use ML recommender for medical information"""
        # Get RAG context for medical information queries
        relevant_docs = self.rag_service.get_relevant_documents(message, top_k=5)
        
        # Check if relevant docs exist
        if not relevant_docs or len(relevant_docs) == 0:
            return "No data found. I don't find the data related to your query in my database. Please try asking about symptoms (Fever, Cough, Fatigue, Difficulty Breathing) or diseases that are available in my knowledge base."
        
        # Check if any document contains disease information
        has_disease_data = any("Disease:" in doc for doc in relevant_docs)
        if not has_disease_data:
            return "No data found. I don't find the data related to your query in my database. Please try asking about symptoms (Fever, Cough, Fatigue, Difficulty Breathing) or diseases that are available in my knowledge base."
        
        try:
            # Analyze with NLP
            nlp_result = self.nlp_processor.analyze_medical_query(message)
            
            # Classify symptoms
            classification = self.symptom_classifier.classify_symptom(message)
            category = classification['category']
            confidence = classification['confidence']
            
            # Extract symptoms from message
            symptoms_list = self._extract_symptom_names(message, nlp_result)
            
            # Get risk assessment
            symptoms = nlp_result['symptom_analysis']['extracted_symptoms']
            normalized_symptoms = self.nlp_processor.normalize_symptoms(symptoms)
            risk_result = self.risk_predictor.predict_risk(normalized_symptoms)
            risk_level = risk_result['risk_level']
            
            # Generate recommendations
            recommendations = [
                "Consult healthcare provider for proper diagnosis",
                "Monitor symptoms closely",
                "Seek immediate medical attention if symptoms worsen"
            ]
            
            if risk_result.get('recommendations'):
                recommendations = risk_result['recommendations'][:3]
            
            # Format response
            base_response = self._format_symptom_response(
                symptoms_list, category, risk_level, confidence, recommendations
            )
            
            # ALWAYS add RAG context and disclaimer
            base_response += self._enhance_with_rag_context(base_response, relevant_docs or [])
            return base_response
            
        except Exception as e:
            print(f"ML medical information error: {e}")
            return "I'm having trouble accessing my ML knowledge base. Please consult a healthcare professional for accurate medical information."
    
    def _ml_general_query(self, message: str) -> str:
        """Use ML for general medical queries"""
        # Get RAG context for general queries
        relevant_docs = self.rag_service.get_relevant_documents(message, top_k=5)
        
        # Check if relevant docs exist
        if not relevant_docs or len(relevant_docs) == 0:
            return "No data found. I don't find the data related to your query in my database. Please try asking about symptoms (Fever, Cough, Fatigue, Difficulty Breathing) or diseases that are available in my knowledge base."
        
        # Check if any document contains disease information
        has_disease_data = any("Disease:" in doc for doc in relevant_docs)
        if not has_disease_data:
            return "No data found. I don't find the data related to your query in my database. Please try asking about symptoms (Fever, Cough, Fatigue, Difficulty Breathing) or diseases that are available in my knowledge base."
        
        try:
            # Analyze with NLP
            nlp_result = self.nlp_processor.analyze_medical_query(message)
            
            # Generate response based on analysis
            if nlp_result['symptom_analysis']['symptom_count'] > 0:
                return self._ml_symptom_analysis(message, relevant_docs)
            elif nlp_result['urgency_indicators']:
                # Classify symptoms for formatting
                classification = self.symptom_classifier.classify_symptom(message)
                category = classification['category']
                confidence = classification['confidence']
                symptoms_list = self._extract_symptom_names(message, nlp_result)
                
                symptoms = nlp_result['symptom_analysis']['extracted_symptoms']
                normalized_symptoms = self.nlp_processor.normalize_symptoms(symptoms)
                risk_result = self.risk_predictor.predict_risk(normalized_symptoms)
                risk_level = risk_result['risk_level']
                
                recommendations = [
                    "Seek immediate medical attention",
                    "Do not delay - contact healthcare provider",
                    "Monitor symptoms closely"
                ]
                
                response = self._format_symptom_response(
                    symptoms_list, category, risk_level, confidence, recommendations
                )
                # ALWAYS add RAG context and disclaimer
                response += self._enhance_with_rag_context(response, relevant_docs or [])
                return response
            else:
                # Format response for disease queries (like "hiv")
                classification = self.symptom_classifier.classify_symptom(message)
                category = classification['category']
                confidence = classification['confidence']
                symptoms_list = self._extract_symptom_names(message, nlp_result)
                
                symptoms = nlp_result['symptom_analysis']['extracted_symptoms']
                normalized_symptoms = self.nlp_processor.normalize_symptoms(symptoms)
                risk_result = self.risk_predictor.predict_risk(normalized_symptoms)
                risk_level = risk_result['risk_level']
                
                recommendations = [
                    "Consult healthcare provider for proper diagnosis",
                    "Monitor symptoms closely",
                    "Seek medical attention if symptoms worsen"
                ]
                
                if risk_result.get('recommendations'):
                    recommendations = risk_result['recommendations'][:3]
                
                response = self._format_symptom_response(
                    symptoms_list, category, risk_level, confidence, recommendations
                )
                # ALWAYS add RAG context and disclaimer
                response += self._enhance_with_rag_context(response, relevant_docs or [])
                return response
                
        except Exception as e:
            print(f"ML general query error: {e}")
            return "I'm experiencing technical difficulties with my ML models. Please try again or consult a healthcare professional for medical advice."