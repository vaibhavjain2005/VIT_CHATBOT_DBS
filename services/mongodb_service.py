from typing import List, Dict, Optional
from datetime import datetime
from pymongo import MongoClient, DESCENDING
from utils.similarity import cosine_similarity

class MongoDBService:
    def __init__(self, connection_url: str = "mongodb://localhost:27017/"):
        self.connection_url = connection_url
        self.client = None
        self.db = None
        self._initialize()
    
    def _initialize(self):
        try:
            print(f"Connecting to MongoDB at {self.connection_url}...")
            self.client = MongoClient(self.connection_url, serverSelectionTimeoutMS=5000)
            self.client.server_info()  # Test connection
            
            self.db = self.client.vit_chatbot
            self.faqs_collection = self.db.vit_faqs
            self.cutoffs_collection = self.db.vit_cutoffs
            self.logs_collection = self.db.query_logs
            
            # Create indexes for better query performance
            self._create_indexes()
            print("MongoDB initialized successfully!")
        except Exception as e:
            print(f"MongoDB initialization error: {e}")
            print("Note: Database features will be unavailable. App will run with limited functionality.")
            self.db = None

    def _create_indexes(self):
        """Create indexes for better query performance."""
        if not self.is_connected():
            return
        
        # FAQs collection indexes
        self.faqs_collection.create_index("category")
        
        # Cutoffs collection indexes
        self.cutoffs_collection.create_index([("year", DESCENDING)])
        self.cutoffs_collection.create_index("campus")
        self.cutoffs_collection.create_index("branch")
        self.cutoffs_collection.create_index("category")
        self.cutoffs_collection.create_index([("rank_range", 1)])
        
        # Compound index
        self.cutoffs_collection.create_index([
            ("branch", 1),
            ("campus", 1),
            ("category", 1),
            ("year", DESCENDING)
        ])
    
    def is_connected(self) -> bool:
        return self.db is not None
    
    def add_faq(self, faq_data: Dict) -> Optional[str]:
        if not self.is_connected():
            return None
        try:
            result = self.faqs_collection.insert_one(faq_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error adding FAQ: {e}")
            return None
    
    def add_cutoff(self, cutoff_data: Dict) -> Optional[str]:
        if not self.is_connected():
            return None
        try:
            required_fields = ['year', 'campus', 'branch', 'category', 'rank_range']
            if not all(field in cutoff_data for field in required_fields):
                print("Error: Missing required fields in cutoff data")
                return None
            
            cutoff_data['last_updated'] = datetime.utcnow()
            result = self.cutoffs_collection.insert_one(cutoff_data)
            
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error adding cutoff: {e}")
            return None
    
    def vector_search_faqs(self, query_embedding: List[float], top_k: int = 8) -> List[Dict]:
        """Search FAQs using vector similarity"""
        if not self.is_connected():
            return []
        try:
            docs = list(self.faqs_collection.find({}))
            
            if not docs:
                print("⚠️ No FAQ documents found in database")
                return []
            
            results = []
            for doc in docs:
                if 'embedding' in doc:
                    similarity = cosine_similarity(query_embedding, doc['embedding'])
                    results.append({
                        'id': str(doc['_id']),
                        'question': doc.get('question', ''),
                        'answer': doc.get('answer', ''),
                        'category': doc.get('category', ''),
                        'score': similarity
                    })
            
            results.sort(key=lambda x: x['score'], reverse=True)
            print(f"📊 Found {len(results)} FAQ matches, returning top {min(top_k, len(results))}")
            return results[:top_k]
        
        except Exception as e:
            print(f"Error in vector search FAQs: {e}")
            return []
    
    def vector_search_cutoffs(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        if not self.is_connected():
            return []
        try:
            docs = list(self.cutoffs_collection.find({}))
            
            results = []
            for doc in docs:
                if 'embedding' in doc:
                    similarity = cosine_similarity(query_embedding, doc['embedding'])
                    results.append({
                        'id': str(doc['_id']),
                        'campus': doc.get('campus', ''),
                        'branch': doc.get('branch', ''),
                        'category': doc.get('category', ''),
                        'rank_range': doc.get('rank_range', []),
                        'answer': doc.get('answer', ''),
                        'score': similarity
                    })
            
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:top_k]
        
        except Exception as e:
            print(f"Error in vector search cutoffs: {e}")
            return []
    
    def get_cutoffs_by_rank(self, rank: int, year: Optional[int] = None) -> List[Dict]:
        """Get branches for a rank with expanded buffer for more possibilities"""
        if not self.is_connected():
            return []
        
        try:
            # Expanded buffer to show more possibilities
            buffer = 5000
            query = {
                "$or": [
                    # Within range
                    {
                        "$and": [
                            {"rank_range.0": {"$lte": rank}},
                            {"rank_range.1": {"$gte": rank}}
                        ]
                    },
                    # Just above range
                    {
                        "$and": [
                            {"rank_range.0": {"$gt": rank}},
                            {"rank_range.0": {"$lte": rank + buffer}}
                        ]
                    },
                    # Just below range
                    {
                        "$and": [
                            {"rank_range.1": {"$lt": rank}},
                            {"rank_range.1": {"$gte": rank - buffer}}
                        ]
                    }
                ]
            }

            latest_year = None

            # Add year filter
            if year:
                query["year"] = year
                latest_year = year
            else:
                latest_year = self.get_latest_year()
                if latest_year:
                    query["year"] = latest_year
            
            docs = self.cutoffs_collection.find(query)
            
            results = []
            for doc in docs:
                results.append({
                    'id': str(doc['_id']),
                    'year': doc.get('year', latest_year),
                    'campus': doc.get('campus', ''),
                    'branch': doc.get('branch', ''),
                    'category': doc.get('category', ''),
                    'rank_range': doc.get('rank_range', []),
                    'notes': doc.get('notes', '')
                })
            
            print(f"📊 Found {len(results)} branches for rank {rank} (year: {year or latest_year})")
            return results
            
        except Exception as e:
            print(f"Error getting cutoffs by rank: {e}")
            return []
    
    def get_all_cutoffs_for_rank(self, rank: int) -> List[Dict]:
        """Get ALL historical cutoffs for a rank (all years) - for predictions"""
        if not self.is_connected():
            return []
        
        try:
            buffer = 5000
            query = {
                "$or": [
                    {
                        "$and": [
                            {"rank_range.0": {"$lte": rank}},
                            {"rank_range.1": {"$gte": rank}}
                        ]
                    },
                    {
                        "$and": [
                            {"rank_range.0": {"$gt": rank}},
                            {"rank_range.0": {"$lte": rank + buffer}}
                        ]
                    },
                    {
                        "$and": [
                            {"rank_range.1": {"$lt": rank}},
                            {"rank_range.1": {"$gte": rank - buffer}}
                        ]
                    }
                ]
            }
            
            # No year filter - get ALL years
            docs = self.cutoffs_collection.find(query).sort("year", DESCENDING)
            
            results = []
            for doc in docs:
                results.append({
                    'id': str(doc['_id']),
                    'year': doc.get('year'),
                    'campus': doc.get('campus', ''),
                    'branch': doc.get('branch', ''),
                    'category': doc.get('category', ''),
                    'rank_range': doc.get('rank_range', []),
                    'notes': doc.get('notes', '')
                })
            
            print(f"📊 Found {len(results)} historical cutoffs for rank {rank} (all years)")
            return results
            
        except Exception as e:
            print(f"Error getting all cutoffs by rank: {e}")
            return []
            
    def get_latest_year(self) -> Optional[int]:
        """Get the most recent year in the database."""
        if not self.is_connected():
            return None
        
        try:
            result = self.cutoffs_collection.find_one(sort=[("year", DESCENDING)])
            return result["year"] if result else None
        except Exception as e:
            print(f"Error getting latest year: {e}")
            return None
    
    def log_query(self, log_data: Dict):
        """Log a query with detailed information."""
        if not self.is_connected():
            return
        try:
            structured_log = {
                'timestamp': datetime.utcnow(),
                'query': log_data.get('query', ''),
                'type': log_data.get('type', 'general'),
                'rank': log_data.get('rank'),
                'year': log_data.get('year'),
                'filters': log_data.get('filters', {}),
                'results_count': log_data.get('results_count', 0),
                'execution_time_ms': log_data.get('execution_time_ms'),
                'error': log_data.get('error'),
                'user_metadata': log_data.get('user_metadata', {})
            }
            
            # Add any additional custom fields
            for key, value in log_data.items():
                if key not in structured_log:
                    structured_log[key] = value
            
            self.logs_collection.insert_one(structured_log)
        except Exception as e:
            print(f"Error logging query: {e}")