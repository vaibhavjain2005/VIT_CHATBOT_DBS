from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class CutoffData(BaseModel):
    year: int = Field(..., description="Academic year")
    campus: str = Field(..., description="Campus location")
    branch: str = Field(..., description="Branch/program name")
    category: str = Field(..., description="Admission category")
    round: Optional[int] = Field(None, description="Counselling round number")
    rank_range: List[int] = Field(..., description="[min_rank, max_rank]")
    seats: Optional[int] = Field(None, description="Number of seats")
    filled: Optional[int] = Field(None, description="Number of seats filled")
    notes: Optional[str] = Field(None, description="Additional information")
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class YearwiseTrend(BaseModel):
    branch: str
    campus: str
    category: str
    years: List[int]
    trend_data: List[Dict] = Field(..., description="Year-wise cutoff trends")
    prediction_2026: Optional[Dict] = Field(None, description="Predicted cutoffs for 2026")

class BranchInfo(BaseModel):
    branch: str
    description: str
    scope: str
    placements: Dict
    fees: Dict
    duration: str
    specializations: Optional[List[str]]