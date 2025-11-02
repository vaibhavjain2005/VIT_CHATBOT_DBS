from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class QueryRequest(BaseModel):
    query: str = Field(..., description="User's question or query")
    user_id: Optional[str] = Field(None, description="Optional user identifier for logging")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "I got rank 15000, which branches can I get?",
                "user_id": "user123"
            }
        }


class IntentClassification(BaseModel):
    intent: str = Field(..., description="Classified intent type")
    confidence: float = Field(..., description="Confidence score (0-1)")
    reasoning: str = Field(..., description="Explanation for the classification")


class BranchPrediction(BaseModel):
    campus: str
    branch: str
    category: str
    rank_range: List[int]
    confidence: str
    confidence_score: float


class QueryResponse(BaseModel):
    answer: str = Field(..., description="Generated response to the query")
    intent: str = Field(..., description="Detected intent type")
    confidence: float = Field(..., description="Intent classification confidence")
    rank_prediction: Optional[Dict] = Field(None, description="Branch predictions if rank-based query")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    processing_time_ms: Optional[float] = Field(None, description="Query processing time in milliseconds")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Based on your rank of 15000, you have good chances for CSE at VIT Chennai...",
                "intent": "rank_prediction",
                "confidence": 0.95,
                "rank_prediction": {
                    "rank": 15000,
                    "predictions": []
                },
                "timestamp": "2025-11-02T12:00:00",
                "processing_time_ms": 1234.56
            }
        }


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, str]
