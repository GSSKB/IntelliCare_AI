import os
import pickle
import numpy as np
from typing import List, Dict, Tuple
import faiss
from pathlib import Path

# Try to import sentence transformers, fallback to basic if not available
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not available. Using basic embeddings.")

class RAGService:
    def __init__(self, data_file_path: str = None):
        """
        Initialize RAG Service with vector database
        
        Args:
            data_file_path: Path to the cleaned_rag.txt file
        """
        # Try multiple possible paths (including Render deployment paths)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            data_file_path,
            os.path.join(current_dir, "cleaned_rag.txt"),  # Same directory as this file
            "cleaned_rag.txt",  # Current working directory
            os.path.join(current_dir, "data", "medical_docs", "cleaned_rag.txt"),
            os.path.join(os.path.dirname(current_dir), "cleaned_rag.txt"),  # Parent directory
        ]
        
        self.data_file_path = None
        for path in possible_paths:
            if path and os.path.exists(path):
                self.data_file_path = path
                break
        
        if not self.data_file_path:
            print(f"Warning: cleaned_rag.txt not found in any of these locations:")
            for path in possible_paths:
                if path:
                    print(f"  - {path}")
            print("RAG service will use dummy context")
        
        self.documents: List[str] = []
        self.embeddings = None
        self.index = None
        self.embedding_model = None
        self.vectorizer = None  # Save TF-IDF vectorizer for reuse
        
        # Initialize embedding model
        self.use_sentence_transformers = SENTENCE_TRANSFORMERS_AVAILABLE
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                print("Loading sentence transformer model...")
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("Embedding model loaded successfully")
            except Exception as e:
                print(f"Error loading sentence transformer: {e}")
                self.use_sentence_transformers = False
        
        # Load and index documents
        self._load_documents()
        self._build_index()
    
    def _load_documents(self):
        """Load medical records from the cleaned_rag.txt file"""
        if not os.path.exists(self.data_file_path):
            print(f"Warning: Data file not found at {self.data_file_path}")
            print("Using dummy context")
            return
        
        try:
            print(f"Loading medical records from {self.data_file_path}...")
            with open(self.data_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Parse each line as a medical record
            self.documents = []
            for line in lines:
                line = line.strip()
                if line:  # Skip empty lines
                    self.documents.append(line)
            
            print(f"Loaded {len(self.documents)} medical records")
            
        except Exception as e:
            print(f"Error loading documents: {e}")
            self.documents = []
    
    def _create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for texts"""
        if self.use_sentence_transformers and self.embedding_model:
            print("Creating embeddings with sentence transformer...")
            embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
            return np.array(embeddings).astype('float32')
        else:
            # Fallback: Use simple TF-IDF-like approach or basic embeddings
            print("Using basic embeddings (sentence-transformers not available)")
            # Simple bag-of-words approach as fallback
            from sklearn.feature_extraction.text import TfidfVectorizer
            self.vectorizer = TfidfVectorizer(max_features=384)  # Save vectorizer for reuse
            embeddings = self.vectorizer.fit_transform(texts).toarray().astype('float32')
            return embeddings
    
    def _build_index(self):
        """Build FAISS index for vector search"""
        if len(self.documents) == 0:
            print("No documents to index")
            return
        
        try:
            # Create embeddings
            print("Creating embeddings for documents...")
            self.embeddings = self._create_embeddings(self.documents)
            
            # Get embedding dimension
            dimension = self.embeddings.shape[1]
            print(f"Embedding dimension: {dimension}")
            
            # Create FAISS index
            print("Building FAISS index...")
            self.index = faiss.IndexFlatL2(dimension)
            
            # Add embeddings to index
            self.index.add(self.embeddings)
            print(f"Index built with {self.index.ntotal} vectors")
            
        except Exception as e:
            print(f"Error building index: {e}")
            self.index = None
    
    def search(self, query: str, top_k: int = 5) -> str:
        """
        Search for relevant medical records using semantic search
        
        Args:
            query: User query
            top_k: Number of top results to return
            
        Returns:
            Context string with relevant medical information
        """
        if self.index is None or len(self.documents) == 0:
            # Return dummy context if no index
            return """
            Medical Information:
            - Fever is a common symptom of many infections
            - Cough can indicate respiratory issues
            - Fatigue is a general symptom with many possible causes
            - Always consult with a healthcare professional for medical advice
            """
        
        try:
            # Create query embedding
            if self.use_sentence_transformers and self.embedding_model:
                query_embedding = self.embedding_model.encode([query])
            else:
                # Use saved vectorizer to ensure same embedding space
                if self.vectorizer is None:
                    raise Exception("Vectorizer not initialized. Cannot create query embedding.")
                query_embedding = self.vectorizer.transform([query]).toarray()
            
            query_embedding = np.array(query_embedding).astype('float32')
            
            # Search in FAISS index
            distances, indices = self.index.search(query_embedding, min(top_k, len(self.documents)))
            
            # Retrieve relevant documents
            relevant_docs = []
            for idx in indices[0]:
                if idx < len(self.documents):
                    relevant_docs.append(self.documents[idx])
            
            # Format context
            context = "Relevant Medical Records:\n\n"
            for i, doc in enumerate(relevant_docs, 1):
                context += f"{i}. {doc}\n\n"
            
            return context
            
        except Exception as e:
            print(f"Error in search: {e}")
            # Return dummy context on error
            return """
            Medical Information:
            - Fever is a common symptom of many infections
            - Cough can indicate respiratory issues
            - Fatigue is a general symptom with many possible causes
            - Always consult with a healthcare professional for medical advice
            """
    
    def get_relevant_documents(self, query: str, top_k: int = 5) -> List[str]:
        """
        Get list of relevant documents (without formatting)
        
        Args:
            query: User query
            top_k: Number of top results to return
            
        Returns:
            List of relevant document strings
        """
        if self.index is None or len(self.documents) == 0:
            return []
        
        try:
            # Create query embedding
            if self.use_sentence_transformers and self.embedding_model:
                query_embedding = self.embedding_model.encode([query])
            else:
                # Use saved vectorizer to ensure same embedding space
                if self.vectorizer is None:
                    raise Exception("Vectorizer not initialized. Cannot create query embedding.")
                query_embedding = self.vectorizer.transform([query]).toarray()
            
            query_embedding = np.array(query_embedding).astype('float32')
            
            # Search in FAISS index
            distances, indices = self.index.search(query_embedding, min(top_k, len(self.documents)))
            
            # Retrieve relevant documents
            relevant_docs = []
            for idx in indices[0]:
                if idx < len(self.documents):
                    relevant_docs.append(self.documents[idx])
            
            return relevant_docs
            
        except Exception as e:
            print(f"Error getting relevant documents: {e}")
            return []
