from pydantic import BaseModel, Field
from app.schemas.enums import Difficulty


class QuestionBase(BaseModel):
    question: str = Field(..., description="The interview question text")
    topic: str = Field(..., description="The main topic of the question")
    difficulty: Difficulty = Field(..., description="The difficulty level of the question")


class QuestionResponse(QuestionBase):
    question_id: str = Field(..., description="Unique identifier for the question")
    question_number: int = Field(..., description="Sequence number of the question in the interview")
