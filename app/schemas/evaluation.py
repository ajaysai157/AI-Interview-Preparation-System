from typing import List, Optional
from pydantic import BaseModel, Field


class EvaluationBase(BaseModel):
    score: float = Field(..., ge=0.0, le=10.0, description="Overall score out of 10")
    correctness: float = Field(..., ge=0.0, le=10.0, description="Technical correctness score out of 10")
    completeness: float = Field(..., ge=0.0, le=10.0, description="Completeness score out of 10")
    clarity: float = Field(..., ge=0.0, le=10.0, description="Clarity score out of 10")
    relevance: float = Field(..., ge=0.0, le=10.0, description="Relevance score out of 10")
    feedback: str = Field(..., description="Qualitative evaluation feedback")
    improvement_areas: List[str] = Field(default_factory=list, description="Specific areas of improvement")


class EvaluationResponse(EvaluationBase):
    pass


class HumanReviewSubmit(BaseModel):
    approve: bool = Field(..., description="Whether to approve the AI evaluation as-is")
    modified_evaluation: Optional[EvaluationBase] = Field(None, description="Optional modified evaluation if the reviewer wants to override the AI scores/feedback")
