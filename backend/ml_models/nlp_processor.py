"""
Medical NLP Processor
Uses natural language processing to extract and analyze medical information from text
"""

import re
from typing import Dict, List, Tuple, Any
import os

# Optional NLP dependencies - handle gracefully if not available
try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("Warning: NLTK not available. Using basic text processing.")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("Warning: TextBlob not available. Sentiment analysis will be limited.")

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("Warning: spaCy not available. Using basic NLP processing.")

class NLPProcessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer() if NLTK_AVAILABLE else None
        
        # Download required NLTK data
        if NLTK_AVAILABLE:
            self._download_nltk_data()
        
        # Load spaCy model (use small model for efficiency)
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("spaCy model not found. Using basic NLP processing.")
        
        # Medical symptom keywords
        self.medical_keywords = self._create_medical_keywords()
        
        # Symptom patterns
        self.symptom_patterns = self._create_symptom_patterns()
        
        # Severity indicators
        self.severity_words = {
            'mild': ['mild', 'slight', 'minor', 'light', 'low'],
            'moderate': ['moderate', 'medium', 'some', 'fair'],
            'severe': ['severe', 'intense', 'extreme', 'bad', 'terrible', 'awful'],
            'very_severe': ['very severe', 'extremely', 'unbearable', 'worst']
        }
        
        # Duration indicators
        self.duration_patterns = {
            'hours': r'\b(hour|hr|hours)\b',
            'days': r'\b(day|days|daily)\b',
            'weeks': r'\b(week|weeks|weekly)\b',
            'months': r'\b(month|months|monthly)\b',
            'years': r'\b(year|years|yearly|annual)\b'
        }
    
    def _download_nltk_data(self):
        """Download required NLTK data"""
        if not NLTK_AVAILABLE:
            return
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
        
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger')
    
    def _create_medical_keywords(self) -> Dict[str, List[str]]:
        """Create medical keyword mappings"""
        return {
            'pain': ['pain', 'ache', 'hurt', 'sore', 'discomfort', 'tender'],
            'fever': ['fever', 'temperature', 'hot', 'feverish', 'pyrexia'],
            'cough': ['cough', 'coughing', 'chesty', 'dry cough', 'wet cough'],
            'breathing': ['breath', 'breathing', 'shortness', 'dyspnea', 'wheezing'],
            'nausea': ['nausea', 'queasy', 'sick', 'vomit', 'vomiting', 'throw up'],
            'headache': ['headache', 'head', 'migraine', 'cephalgia'],
            'fatigue': ['fatigue', 'tired', 'exhausted', 'weak', 'lethargic', 'drained'],
            'joint': ['joint', 'arthritis', 'stiffness', 'swelling', 'inflammation'],
            'chest': ['chest', 'thorax', 'sternum', 'rib'],
            'stomach': ['stomach', 'abdomen', 'belly', 'tummy', 'gastric'],
            'dizziness': ['dizzy', 'dizziness', 'vertigo', 'lightheaded', 'faint'],
            'rash': ['rash', 'skin', 'itchy', 'redness', 'hives', 'dermatitis']
        }
    
    def _create_symptom_patterns(self) -> Dict[str, str]:
        """Create regex patterns for symptom extraction"""
        return {
            'chest_pain': r'\b(chest\s*pain|chest\s*discomfort|chest\s*pressure|chest\s*tightness)\b',
            'breathing_difficulty': r'\b(shortness\s*of\s*breath|difficulty\s*breathing|can\'t\s*breathe|breathless)\b',
            'stomach_pain': r'\b(stomach\s*pain|abdominal\s*pain|belly\s*ache|stomach\s*ache)\b',
            'headache': r'\b(headache|migraine|head\s*ache|cephalgia)\b',
            'fever': r'\b(fever|temperature|feverish|pyrexia)\b',
            'cough': r'\b(cough|coughing|chesty|dry\s*cough|wet\s*cough)\b',
            'nausea': r'\b(nausea|queasy|sick|vomit|vomiting|throw\s*up)\b',
            'fatigue': r'\b(fatigue|tired|exhausted|weak|lethargic|drained)\b',
            'joint_pain': r'\b(joint\s*pain|arthritis|stiffness|swelling|inflammation)\b',
            'dizziness': r'\b(dizzy|dizziness|vertigo|lightheaded|faint)\b',
            'rash': r'\b(rash|skin|itchy|redness|hives|dermatitis)\b'
        }
    
    def extract_symptoms(self, text: str) -> Dict[str, Any]:
        """Extract symptoms from medical text"""
        
        # Preprocess text
        cleaned_text = self._preprocess_text(text)
        
        # Extract symptoms using patterns
        extracted_symptoms = {}
        for symptom_name, pattern in self.symptom_patterns.items():
            matches = re.findall(pattern, cleaned_text, re.IGNORECASE)
            extracted_symptoms[symptom_name] = len(matches) > 0
        
        # Extract severity
        severity = self._extract_severity(cleaned_text)
        
        # Extract duration
        duration = self._extract_duration(cleaned_text)
        
        # Extract sentiment
        sentiment = self._analyze_sentiment(text)
        
        # Extract medical entities if spaCy is available
        medical_entities = []
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['DISEASE', 'SYMPTOM', 'CONDITION']:
                    medical_entities.append({
                        'text': ent.text,
                        'label': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char
                    })
        
        return {
            'extracted_symptoms': extracted_symptoms,
            'severity': severity,
            'duration': duration,
            'sentiment': sentiment,
            'medical_entities': medical_entities,
            'processed_text': cleaned_text,
            'symptom_count': sum(extracted_symptoms.values())
        }
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep medical punctuation
        text = re.sub(r'[^\w\s\-\.\']', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _extract_severity(self, text: str) -> str:
        """Extract symptom severity from text"""
        
        for severity_level, words in self.severity_words.items():
            for word in words:
                if word in text:
                    return severity_level
        
        return 'moderate'  # Default severity
    
    def _extract_duration(self, text: str) -> str:
        """Extract symptom duration from text"""
        
        for duration_level, pattern in self.duration_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return duration_level
        
        return 'days'  # Default duration
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of medical text"""
        
        if TEXTBLOB_AVAILABLE:
            try:
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                subjectivity = blob.sentiment.subjectivity
                
                # Classify sentiment
                if polarity > 0.1:
                    sentiment_label = 'positive'
                elif polarity < -0.1:
                    sentiment_label = 'negative'
                else:
                    sentiment_label = 'neutral'
                
                return {
                    'polarity': polarity,
                    'subjectivity': subjectivity,
                    'label': sentiment_label
                }
            except:
                pass
        
        return {
            'polarity': 0.0,
            'subjectivity': 0.0,
            'label': 'neutral'
        }
    
    def analyze_medical_query(self, query: str) -> Dict[str, Any]:
        """Comprehensive analysis of medical query"""
        
        # Extract symptoms
        symptom_analysis = self.extract_symptoms(query)
        
        # Tokenize and extract keywords
        if NLTK_AVAILABLE:
            tokens = word_tokenize(query.lower())
            tokens = [token for token in tokens if token.isalpha() and token not in stopwords.words('english')]
            # Lemmatize tokens
            lemmas = [self.lemmatizer.lemmatize(token) for token in tokens] if self.lemmatizer else tokens
        else:
            # Basic tokenization without NLTK
            tokens = query.lower().split()
            tokens = [token for token in tokens if token.isalpha()]
            lemmas = tokens
        
        # Find medical keywords
        medical_terms_found = []
        for category, keywords in self.medical_keywords.items():
            for keyword in keywords:
                if keyword in lemmas:
                    medical_terms_found.append((category, keyword))
        
        # Determine query type
        query_type = self._classify_query_type(query, symptom_analysis)
        
        # Extract key phrases
        key_phrases = self._extract_key_phrases(query)
        
        return {
            'symptom_analysis': symptom_analysis,
            'tokens': tokens,
            'lemmas': lemmas,
            'medical_terms': medical_terms_found,
            'query_type': query_type,
            'key_phrases': key_phrases,
            'urgency_indicators': self._detect_urgency_indicators(query)
        }
    
    def _classify_query_type(self, query: str, symptom_analysis: Dict) -> str:
        """Classify the type of medical query"""
        
        query_lower = query.lower()
        
        # Risk assessment queries
        if any(word in query_lower for word in ['risk', 'assess', 'evaluate', 'analyze']):
            return 'risk_assessment'
        
        # Symptom information queries
        elif any(word in query_lower for word in ['what is', 'information', 'tell me about', 'explain']):
            return 'information'
        
        # Treatment queries
        elif any(word in query_lower for word in ['treatment', 'cure', 'medicine', 'medication']):
            return 'treatment'
        
        # General symptom description
        elif symptom_analysis['symptom_count'] > 0:
            return 'symptom_description'
        
        # General medical question
        else:
            return 'general_question'
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key medical phrases from text"""
        
        # Use spaCy for phrase extraction if available
        if self.nlp:
            doc = self.nlp(text)
            phrases = []
            
            # Extract noun phrases
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) <= 3:  # Keep phrases short
                    phrases.append(chunk.text)
            
            return phrases
        else:
            # Fallback: extract phrases using simple patterns
            phrases = []
            # Look for adjective-noun combinations
            words = text.split()
            for i in range(len(words) - 1):
                phrase = f"{words[i]} {words[i+1]}"
                if any(keyword in phrase.lower() for keywords in self.medical_keywords.values() for keyword in keywords):
                    phrases.append(phrase)
            
            return phrases
    
    def _detect_urgency_indicators(self, text: str) -> List[str]:
        """Detect urgency indicators in medical text"""
        
        urgency_words = [
            'emergency', 'urgent', 'immediate', 'severe', 'extreme',
            'unbearable', 'worst', 'can\'t breathe', 'chest pain',
            'call 911', 'hospital', 'emergency room'
        ]
        
        text_lower = text.lower()
        found_indicators = []
        
        for word in urgency_words:
            if word in text_lower:
                found_indicators.append(word)
        
        return found_indicators
    
    def generate_summary(self, text: str) -> str:
        """Generate a summary of medical text"""
        
        # Simple extractive summarization
        if NLTK_AVAILABLE:
            sentences = sent_tokenize(text)
        else:
            # Basic sentence splitting
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 2:
            return text
        
        # Score sentences based on medical keywords
        sentence_scores = []
        for sentence in sentences:
            score = 0
            sentence_lower = sentence.lower()
            
            # Check for medical keywords
            for keywords in self.medical_keywords.values():
                for keyword in keywords:
                    if keyword in sentence_lower:
                        score += 1
            
            # Check for urgency indicators
            urgency_indicators = self._detect_urgency_indicators(sentence)
            score += len(urgency_indicators) * 2
            
            sentence_scores.append((sentence, score))
        
        # Sort by score and take top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top 2-3 sentences as summary
        summary_sentences = [sent[0] for sent in sentence_scores[:2]]
        
        return ' '.join(summary_sentences)
    
    def normalize_symptoms(self, symptoms: Dict[str, bool]) -> Dict[str, bool]:
        """Normalize symptom names to standard format"""
        
        normalization_map = {
            'chest_pain': 'chestPain',
            'breathing_difficulty': 'breathingDifficulty',
            'joint_pain': 'jointPain',
            'stomach_pain': 'nausea'  # Map stomach pain to nausea for simplicity
        }
        
        normalized = {}
        for symptom, present in symptoms.items():
            normalized_symptom = normalization_map.get(symptom, symptom)
            normalized[normalized_symptom] = present
        
        return normalized
