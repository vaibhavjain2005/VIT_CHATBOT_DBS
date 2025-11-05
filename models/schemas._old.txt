from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class QueryRequest(BaseModel):
    query: str = Field(..., description="User's question or query")
    user_id: Optional[str] = Field(None, description="Optional user identifier for logging")
    year: Optional[int] = Field(None, description="Specific year for cutoff data. If not provided, latest year will be used.")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "I got rank 15000, which branches can I get?",
                "user_id": "user123",
                "year": 2025
            }
        }


class IntentClassification(BaseModel):
    intent: str = Field(..., description="Classified intent type")
    confidence: float = Field(..., description="Confidence score (0-1)")
    reasoning: str = Field(..., description="Explanation for the classification")


class TrendInfo(BaseModel):
    year: int
    min_rank: int
    max_rank: int
    avg_rank: float
    seats: Optional[int]
    filled: Optional[int]
    yoy_change: Optional[float]

class PredictionInfo(BaseModel):
    year: int
    predicted_min_rank: int
    predicted_max_rank: int
    confidence: float
    trend_direction: str
    avg_yearly_change: float

class BranchPrediction(BaseModel):
    campus: str
    branch: str
    category: str
    year: int
    rank_range: List[int]
    seats: Optional[int] = None
    filled: Optional[int] = None
    confidence: str
    confidence_score: float
    historical_trends: List[TrendInfo] = []
    prediction: Optional[PredictionInfo] = None


class QueryResponse(BaseModel):
    answer: str = Field(..., description="Generated response to the query")
    intent: str = Field(..., description="Detected intent type")
    confidence: float = Field(..., description="Intent classification confidence")
    rank_prediction: Optional[Dict] = Field(None, description="Branch predictions if rank-based query")
    year: Optional[int] = Field(None, description="Year of the data used for predictions")
    has_historical_data: bool = Field(default=False, description="Whether historical trend data is available")
    has_prediction: bool = Field(default=False, description="Whether future prediction is available")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    processing_time_ms: Optional[float] = Field(None, description="Query processing time in milliseconds")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Based on your rank of 15000, here are your options for 2025:",
                "intent": "rank_prediction",
                "confidence": 0.95,
                "year": 2025,
                "rank_prediction": {
                    "rank": 15000,
                    "year": 2025,
                    "predictions": [],
                    "trend_summary": "Cutoffs have shown a decreasing trend over the past 3 years"
                },
                "has_historical_data": True,
                "has_prediction": True,
                "timestamp": "2025-11-04T12:00:00",
                "processing_time_ms": 1234.56
            }
        }


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, str]
