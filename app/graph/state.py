from typing import Dict, List, Optional, TypedDict


class InterviewState(TypedDict):
    interview_id: str
    role: str
    experience_level: str
    interview_type: str
    difficulty: str
    total_questions: int
    current_question_number: int
    current_question: Optional[dict]  # Contains: question_id, question, topic, difficulty, question_number
    current_answer: Optional[dict]  # Contains: answer_id, question_id, answer, submitted_at
    current_evaluation: Optional[dict]  # Contains: score, correctness, completeness, clarity, relevance, feedback, improvement_areas
    history: List[dict]  # List of dicts matching InterviewHistoryItem
    overall_score: Optional[float]
    status: str  # created, in_progress, paused, completed
    needs_human_review: bool
    final_report: Optional[dict]  # Contains: overall_score, strengths, weaknesses, topic_performance, recommendations, interview_summary
