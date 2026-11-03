from typing import Dict, List
from pydantic import BaseModel, Field


class FinalResultResponse(BaseModel):
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall scaled interview score out of 100")
    strengths: List[str] = Field(default_factory=list, description="Key candidate strengths identified")
    weaknesses: List[str] = Field(default_factory=list, description="Key candidate weaknesses or gaps")
    topic_performance: Dict[str, float] = Field(
        default_factory=dict, description="Performance scores broken down by topic (out of 100)"
    )
    recommendations: List[str] = Field(default_factory=list, description="Tailored learning recommendations")
    interview_summary: str = Field(..., description="High-level descriptive summary of interview performance")
