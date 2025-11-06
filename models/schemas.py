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


class QueryResponse(BaseModel):
    answer: str = Field(..., description="Generated response to the query")
    intent: str = Field(..., description="Detected intent type")
    confidence: float = Field(..., description="Intent classification confidence")
    rank_prediction: Optional[Dict] = Field(None, description="Branch predictions if rank-based query")
    year: Optional[int] = Field(None, description="Year of the data used")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    processing_time_ms: Optional[float] = Field(None, description="Query processing time in milliseconds")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Based on your rank of 15000, here are your options...",
                "intent": "rank_prediction",
                "confidence": 0.95,
                "year": 2025,
                "rank_prediction": {
                    "rank": 15000,
                    "predictions": [
                        {
                            "campus": "Vellore",
                            "branch": "CSE",
                            "category": "Category 1",
                            "year": 2024,
                            "rank_range": [1, 1840],
                            "confidence": "High",
                            "confidence_score": 0.85,
                            "notes": "Highly competitive"
                        }
                    ]
                },
                "timestamp": "2025-11-04T12:00:00",
                "processing_time_ms": 1234.56
            }
        }


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: dict