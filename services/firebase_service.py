from typing import List, Dict, Optional
import firebase_admin
from firebase_admin import credentials, firestore
from utils.similarity import cosine_similarity


class FirebaseService:
    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.db = None
        self._initialize()
    
    def _initialize(self):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(self.credentials_path)
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            self.faqs_collection = self.db.collection('vit_faqs')
            self.cutoffs_collection = self.db.collection('vit_cutoffs')
            self.logs_collection = self.db.collection('query_logs')
            print("Firebase initialized successfully!")
        except Exception as e:
            print(f"Firebase initialization error: {e}")
            print("Note: Firebase features will be unavailable. App will run with limited functionality.")
            self.db = None
    
    def is_connected(self) -> bool:
        return self.db is not None
    
    def add_faq(self, faq_data: Dict) -> Optional[str]:
        if not self.is_connected():
            return None
        try:
            doc_ref = self.faqs_collection.add(faq_data)
            return doc_ref[1].id
        except Exception as e:
            print(f"Error adding FAQ: {e}")
            return None
    
    def add_cutoff(self, cutoff_data: Dict) -> Optional[str]:
        if not self.is_connected():
            return None
        try:
            doc_ref = self.cutoffs_collection.add(cutoff_data)
            return doc_ref[1].id
        except Exception as e:
            print(f"Error adding cutoff: {e}")
            return None
    
    def vector_search_faqs(self, query_embedding: List[float], top_k: int = 3) -> List[Dict]:
        if not self.is_connected():
            return []
        try:
            docs = self.faqs_collection.stream()
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                if 'embedding' in data:
                    similarity = cosine_similarity(query_embedding, data['embedding'])
                    results.append({
                        'id': doc.id,
                        'question': data.get('question', ''),
                        'answer': data.get('answer', ''),
                        'category': data.get('category', ''),
                        'score': similarity
                    })
            
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:top_k]
        
        except Exception as e:
            print(f"Error in vector search FAQs: {e}")
            return []
    
    def vector_search_cutoffs(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        if not self.is_connected():
            return []
        try:
            docs = self.cutoffs_collection.stream()
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                if 'embedding' in data:
                    similarity = cosine_similarity(query_embedding, data['embedding'])
                    results.append({
                        'id': doc.id,
                        'campus': data.get('campus', ''),
                        'branch': data.get('branch', ''),
                        'category': data.get('category', ''),
                        'rank_range': data.get('rank_range', []),
                        'answer': data.get('answer', ''),
                        'score': similarity
                    })
            
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:top_k]
        
        except Exception as e:
            print(f"Error in vector search cutoffs: {e}")
            return []
    
    def get_cutoffs_by_rank(self, rank: int) -> List[Dict]:
        if not self.is_connected():
            return []
        try:
            docs = self.cutoffs_collection.stream()
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                rank_range = data.get('rank_range', [])
                
                if len(rank_range) == 2:
                    if rank_range[0] <= rank <= rank_range[1]:
                        results.append({
                            'id': doc.id,
                            'campus': data.get('campus', ''),
                            'branch': data.get('branch', ''),
                            'category': data.get('category', ''),
                            'rank_range': rank_range,
                            'answer': data.get('answer', '')
                        })
            
            return results
        
        except Exception as e:
            print(f"Error getting cutoffs by rank: {e}")
            return []
    
    def log_query(self, log_data: Dict):
        if not self.is_connected():
            return
        try:
            log_data['timestamp'] = firestore.SERVER_TIMESTAMP
            self.logs_collection.add(log_data)
        except Exception as e:
            print(f"Error logging query: {e}")
