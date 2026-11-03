from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.enums import Difficulty, ExperienceLevel, InterviewStatus, InterviewType
from app.schemas.question import QuestionResponse
from app.schemas.answer import AnswerResponse
from app.schemas.evaluation import EvaluationResponse
from app.schemas.result import FinalResultResponse


class InterviewCreate(BaseModel):
    role: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "Python Backend Engineer"})
    experience_level: ExperienceLevel = Field(..., json_schema_extra={"example": ExperienceLevel.JUNIOR})
    interview_type: InterviewType = Field(..., json_schema_extra={"example": InterviewType.TECHNICAL})
    difficulty: Difficulty = Field(..., json_schema_extra={"example": Difficulty.MEDIUM})
    total_questions: int = Field(5, ge=1, le=20, description="Total number of questions in the interview")


class InterviewResponse(BaseModel):
    interview_id: str
    role: str
    experience_level: ExperienceLevel
    interview_type: InterviewType
    difficulty: Difficulty
    total_questions: int
    current_question_number: int
    status: InterviewStatus
    overall_score: Optional[float] = None
    created_at: Optional[str] = None


class InterviewHistoryItem(BaseModel):
    question: Optional[QuestionResponse] = None
    answer: Optional[AnswerResponse] = None
    evaluation: Optional[EvaluationResponse] = None


class DetailedInterviewResponse(InterviewResponse):
    current_question: Optional[QuestionResponse] = None
    current_evaluation: Optional[EvaluationResponse] = Field(
        None,
        description="Pending AI evaluation (shown when the interview is paused for human review)",
    )
    needs_human_review: bool = False
    history: List[InterviewHistoryItem] = Field(default_factory=list)
    final_report: Optional[FinalResultResponse] = None


class InterviewStartResponse(BaseModel):
    interview_id: str
    current_question_number: int
    question: QuestionResponse
    status: InterviewStatus


class DashboardStatsResponse(BaseModel):
    total_interviews: int
    completed_interviews: int
    average_score: float
    highest_score: float
    topic_breakdown: Dict[str, float] = Field(default_factory=dict)
    strongest_areas: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)
    recent_interviews: List[Dict[str, Any]] = Field(default_factory=list)