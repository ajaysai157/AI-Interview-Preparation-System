from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.schemas.question import QuestionResponse
from app.schemas.evaluation import EvaluationResponse


class AnswerSubmit(BaseModel):
    answer: str = Field(..., min_length=1, max_length=5000, description="The candidate's answer text")

    @field_validator("answer")
    @classmethod
    def answer_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("answer must not be blank")
        return value


class AnswerResponse(BaseModel):
    answer_id: str = Field(..., description="Unique identifier for this answer submission")
    question_id: str = Field(..., description="The ID of the question this answer is responding to")
    answer: str = Field(..., description="The candidate's answer text")
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp when the answer was submitted")


class AnswerSubmitResponse(BaseModel):
    evaluation: Optional[EvaluationResponse] = Field(None, description="The AI evaluation results (None if paused for human review)")
    status: str = Field(..., description="Current status of the interview ('in_progress', 'paused', 'completed')")
    needs_human_review: bool = Field(..., description="Indicates if this answer's evaluation is paused for human review")
    next_question: Optional[QuestionResponse] = Field(None, description="The next generated question (None if paused or completed)")
