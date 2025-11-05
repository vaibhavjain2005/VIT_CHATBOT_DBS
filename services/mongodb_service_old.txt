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
            self.trends_collection = self.db.trends
            
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
        
        # Compound index for trend analysis
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
            # Ensure required fields are present
            required_fields = ['year', 'campus', 'branch', 'category', 'rank_range']
            if not all(field in cutoff_data for field in required_fields):
                print("Error: Missing required fields in cutoff data")
                return None
            
            # Add timestamp
            cutoff_data['last_updated'] = datetime.utcnow()
            
            # Insert the cutoff data
            result = self.cutoffs_collection.insert_one(cutoff_data)
            
            # Update trends
            self._update_trends(cutoff_data)
            
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error adding cutoff: {e}")
            return None
            
    def _update_trends(self, cutoff_data: Dict):
        """Update trends data after adding new cutoff."""
        try:
            key = {
                'branch': cutoff_data['branch'],
                'campus': cutoff_data['campus'],
                'category': cutoff_data['category'],
                'year': cutoff_data['year']
            }
            
            # Calculate average rank for the cutoff
            avg_rank = sum(cutoff_data['rank_range']) / 2
            
            # Update trends collection
            self.trends_collection.update_one(
                key,
                {
                    '$min': {'min_rank': cutoff_data['rank_range'][0]},
                    '$max': {'max_rank': cutoff_data['rank_range'][1]},
                    '$push': {'rank_points': avg_rank},
                    '$set': {
                        'last_updated': datetime.utcnow(),
                        'seats': cutoff_data.get('seats'),
                        'filled': cutoff_data.get('filled')
                    }
                },
                upsert=True
            )
        except Exception as e:
            print(f"Error updating trends: {e}")
    
    def vector_search_faqs(self, query_embedding: List[float], top_k: int = 3) -> List[Dict]:
        if not self.is_connected():
            return []
        try:
            docs = list(self.faqs_collection.find({}))
            
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
        """Get cutoffs for a given rank and optionally for a specific year."""
        if not self.is_connected():
            return []
        
        try:
            # Build query to get branches within and near the rank
            buffer = 2000  # Allow some flexibility in rank ranges
            query = {
                "$or": [
                    # Direct matches (High chance)
                    {
                        "$and": [
                            {"rank_range.0": {"$lte": rank}},
                            {"rank_range.1": {"$gte": rank}}
                        ]
                    },
                    # Just above range (Moderate chance)
                    {
                        "$and": [
                            {"rank_range.0": {"$gt": rank}},
                            {"rank_range.0": {"$lte": rank + buffer}}
                        ]
                    },
                    # Just below range (Low chance)
                    {
                        "$and": [
                            {"rank_range.1": {"$lt": rank}},
                            {"rank_range.1": {"$gte": rank - buffer}}
                        ]
                    }
                ]
            }

            # Prepare latest_year variable
            latest_year = None

            # Add year filter if specified
            if year:
                query["year"] = year
                latest_year = year
            else:
                # Get latest year if not specified
                latest_year = self.get_latest_year()
                if latest_year:
                    query["year"] = latest_year
            
            # Find matching cutoffs
            docs = self.cutoffs_collection.find(query)
            
            results = []
            for doc in docs:
                # Get trend information
                trend_info = self.get_trend_info(
                    doc['branch'],
                    doc['campus'],
                    doc['category'],
                    doc.get('year', latest_year)
                )

                results.append({
                    'id': str(doc['_id']),
                    'year': doc.get('year', latest_year),
                    'campus': doc.get('campus', ''),
                    'branch': doc.get('branch', ''),
                    'category': doc.get('category', ''),
                    'rank_range': doc.get('rank_range', []),
                    'seats': doc.get('seats'),
                    'filled': doc.get('filled'),
                    'answer': doc.get('answer', ''),
                    'trend': trend_info
                })
            
            return results
            
        except Exception as e:
            print(f"Error getting cutoffs by rank: {e}")
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
            
    def get_trend_info(self, branch: str, campus: str, category: str, current_year: int) -> Dict:
        """Get trend information for a specific branch/campus/category combination."""
        try:
            # Get historical data
            pipeline = [
                {
                    "$match": {
                        "branch": branch,
                        "campus": campus,
                        "category": category,
                        "year": {"$lte": current_year}
                    }
                },
                {
                    "$sort": {"year": 1}
                },
                {
                    "$project": {
                        "year": 1,
                        "min_rank": {"$arrayElemAt": ["$rank_range", 0]},
                        "max_rank": {"$arrayElemAt": ["$rank_range", 1]},
                        "seats": 1,
                        "filled": 1
                    }
                },
                {
                    "$group": {
                        "_id": "$year",
                        "min_rank": {"$first": "$min_rank"},
                        "max_rank": {"$first": "$max_rank"},
                        "avg_rank": {
                            "$avg": {
                                "$divide": [
                                    {"$add": ["$min_rank", "$max_rank"]},
                                    2
                                ]
                            }
                        },
                        "seats": {"$first": "$seats"},
                        "filled": {"$first": "$filled"}
                    }
                }
            ]
            
            yearly_data = list(self.cutoffs_collection.aggregate(pipeline))
            
            if not yearly_data:
                return {}
            
            # Calculate trends
            trends = []
            for i in range(len(yearly_data)):
                year_data = yearly_data[i]
                trend = {
                    "year": year_data["_id"],
                    "min_rank": year_data["min_rank"],
                    "max_rank": year_data["max_rank"],
                    "avg_rank": year_data["avg_rank"],
                    "seats": year_data.get("seats"),
                    "filled": year_data.get("filled")
                }
                
                if i > 0:
                    prev_year = yearly_data[i-1]
                    yoy_change = ((year_data["avg_rank"] - prev_year["avg_rank"]) 
                                / prev_year["avg_rank"] * 100)
                    trend["yoy_change"] = round(yoy_change, 2)
                
                trends.append(trend)
            
            # Calculate prediction for next year
            prediction = self._predict_next_year(trends)
            
            return {
                "historical": trends,
                "prediction": prediction
            }
            
        except Exception as e:
            print(f"Error getting trend info: {e}")
            return {}
            
    def _predict_next_year(self, trends: List[Dict]) -> Dict:
        """Predict next year's ranks based on historical trends."""
        if len(trends) < 2:
            return {}
        
        try:
            # Calculate average year-over-year change
            yoy_changes = [t.get("yoy_change", 0) for t in trends[1:]]
            avg_change = sum(yoy_changes) / len(yoy_changes)
            
            # Get latest year's data
            latest = trends[-1]
            next_year = latest["year"] + 1
            
            # Predict ranks
            predicted_avg = latest["avg_rank"] * (1 + (avg_change / 100))
            rank_range = latest["max_rank"] - latest["min_rank"]
            
            return {
                "year": next_year,
                "predicted_min_rank": max(1, round(predicted_avg - (rank_range/2))),
                "predicted_max_rank": round(predicted_avg + (rank_range/2)),
                "confidence": self._calculate_prediction_confidence(trends),
                "trend_direction": "increasing" if avg_change > 0 else "decreasing",
                "avg_yearly_change": round(avg_change, 2)
            }
            
        except Exception as e:
            print(f"Error predicting next year: {e}")
            return {}
            
    def _calculate_prediction_confidence(self, trends: List[Dict]) -> float:
        """Calculate confidence score for predictions."""
        if len(trends) < 2:
            return 0.5
        try:
            # Get year-over-year changes
            changes = [abs(t.get("yoy_change", 0)) for t in trends[1:]]

            # Calculate standard deviation of changes
            mean = sum(changes) / len(changes)
            variance = sum((x - mean) ** 2 for x in changes) / len(changes)

            # More consistent changes = higher confidence
            consistency = 1 / (1 + (variance / 100))

            # More historical data = higher confidence
            data_factor = min(len(trends) / 5, 1)  # Max boost from 5 years of data

            confidence = (consistency * 0.7 + data_factor * 0.3)
            return round(min(max(confidence, 0.3), 0.9), 2)

        except Exception as e:
            print(f"Error calculating prediction confidence: {e}")
            return 0.5

    # --- Compatibility wrappers ---
    def get_year_wise_trends(self, branch: str, campus: str, category: str) -> Dict:
        """Compatibility wrapper that returns year-wise trends in the shape expected by older code.

        Returns: {"trends": [...], "prediction": {...}}
        """
        if not self.is_connected():
            return {}

        try:
            # Use existing get_trend_info to fetch historical + prediction
            # get_trend_info requires a current_year; use latest year available
            latest = self.get_latest_year() or datetime.utcnow().year
            info = self.get_trend_info(branch, campus, category, latest)

            # get_trend_info returns {"historical": [...], "prediction": {...}}
            historical = info.get("historical", [])
            prediction = info.get("prediction")

            # Normalize to expected shape
            return {"trends": historical, "prediction": prediction}
        except Exception as e:
            print(f"Error in get_year_wise_trends: {e}")
            return {}

    def predict_rank_range(self, branch: str, campus: str, category: str) -> Dict:
        """Compatibility wrapper that returns predicted rank range and summary fields expected by older scripts.

        Returns: {predicted_min_rank, predicted_max_rank, confidence, trend, avg_yearly_change}
        """
        if not self.is_connected():
            return {}

        try:
            latest = self.get_latest_year() or datetime.utcnow().year
            info = self.get_trend_info(branch, campus, category, latest)
            prediction = info.get("prediction")
            if not prediction:
                return {}

            return {
                "predicted_min_rank": prediction.get("predicted_min_rank"),
                "predicted_max_rank": prediction.get("predicted_max_rank"),
                "confidence": prediction.get("confidence"),
                "trend": prediction.get("trend_direction"),
                "avg_yearly_change": prediction.get("avg_yearly_change")
            }
        except Exception as e:
            print(f"Error in predict_rank_range: {e}")
            return {}
    
    def log_query(self, log_data: Dict):
        """Log a query with detailed information."""
        if not self.is_connected():
            return
        try:
            # Ensure basic structure
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