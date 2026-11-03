import logging
from uuid import uuid4

from app.ai.chains import (
    get_answer_evaluation_chain,
    get_question_generation_chain,
    get_report_generation_chain,
    safe_invoke,
)
from app.config import settings
from app.graph.state import InterviewState
from app.services.scoring import next_difficulty, overall_score, topic_performance

logger = logging.getLogger(__name__)


def initialize_interview(state: InterviewState) -> dict:
    """Initializes the interview status to in_progress."""
    logger.info(f"Initializing interview session {state.get('interview_id')}")
    return {"status": "in_progress"}


def generate_question(state: InterviewState) -> dict:
    """Generates the next interview question using LLM."""
    current_question_number = state.get("current_question_number") or 0
    logger.info(f"Generating question {current_question_number + 1} for session {state.get('interview_id')}")

    # Build context from history to avoid repeating questions
    history = state.get("history") or []
    previous_questions = [item["question"]["question"] for item in history if item.get("question")]

    # Build candidate performance history text
    perf_list = []
    for item in history:
        if item.get("question") and item.get("evaluation"):
            perf_list.append(
                f"Topic: {item['question']['topic']} | Question: {item['question']['question']} | Score: {item['evaluation']['score']}/10"
            )
    performance_context = "\n".join(perf_list) if perf_list else "No questions answered yet."

    chain = get_question_generation_chain()
    res = safe_invoke(
        chain,
        {
            "role": state.get("role"),
            "experience_level": state.get("experience_level"),
            "interview_type": state.get("interview_type"),
            "difficulty": state.get("difficulty"),
            "previous_questions": str(previous_questions),
            "performance_context": performance_context,
        },
        operation="generating the next question",
    )

    next_question_number = (state.get("current_question_number") or 0) + 1

    question_dict = {
        "question_id": str(uuid4()),
        "question": res.question,
        "topic": res.topic,
        "difficulty": res.difficulty.value,
        "question_number": next_question_number,
    }

    return {
        "current_question_number": next_question_number,
        "current_question": question_dict,
        "status": "in_progress",
    }


def evaluate_answer(state: InterviewState) -> dict:
    """Evaluates candidate's current answer using LLM."""
    current_question_number = state.get("current_question_number") or 0
    logger.info(f"Evaluating answer for question {current_question_number} in session {state.get('interview_id')}")

    current_q = state.get("current_question")
    current_ans = state.get("current_answer")

    if not current_q or not current_ans:
        raise ValueError("Cannot evaluate answer: current_question or current_answer is missing in state.")

    chain = get_answer_evaluation_chain()
    res = safe_invoke(
        chain,
        {
            "role": state.get("role"),
            "difficulty": state.get("difficulty"),
            "question": current_q.get("question"),
            "candidate_answer": current_ans.get("answer"),
        },
        operation="evaluating the candidate answer",
    )

    evaluation_dict = {
        "score": res.score,
        "correctness": res.correctness,
        "completeness": res.completeness,
        "clarity": res.clarity,
        "relevance": res.relevance,
        "feedback": res.feedback,
        "improvement_areas": res.improvement_areas,
    }

    # Human review mechanism based on threshold
    needs_review = res.score < settings.HUMAN_REVIEW_THRESHOLD
    next_status = "paused" if needs_review else "in_progress"

    return {
        "current_evaluation": evaluation_dict,
        "needs_human_review": needs_review,
        "status": next_status,
    }


def approve_evaluation(state: InterviewState) -> dict:
    """Clears human review status to resume candidate path."""
    logger.info(f"Approving/modifying evaluation for session {state.get('interview_id')}")
    return {
        "needs_human_review": False,
        "status": "in_progress",
    }


def update_performance(state: InterviewState) -> dict:
    """Saves current question, answer, and evaluation to history and adjusts difficulty."""
    logger.info(f"Updating history and performance metrics for session {state.get('interview_id')}")

    history_item = {
        "question": state.get("current_question"),
        "answer": state.get("current_answer"),
        "evaluation": state.get("current_evaluation"),
    }

    updated_history = list(state.get("history") or [])
    updated_history.append(history_item)

    # Adaptive interview logic (difficulty adjustment based on last score)
    current_evaluation = state.get("current_evaluation") or {}
    score = current_evaluation.get("score", 7.0)
    current_diff = state.get("difficulty", "medium")
    next_diff = next_difficulty(
        current=current_diff,
        score=score,
        upgrade_threshold=settings.DIFFICULTY_UPGRADE_THRESHOLD,
        downgrade_threshold=settings.DIFFICULTY_DOWNGRADE_THRESHOLD,
    )
    if next_diff != current_diff:
        logger.info(
            f"Score {score}: adjusting difficulty from '{current_diff}' to '{next_diff}' "
            f"([{settings.DIFFICULTY_DOWNGRADE_THRESHOLD}, {settings.DIFFICULTY_UPGRADE_THRESHOLD}) stays the same)."
        )
    else:
        logger.info(f"Score {score}: keeping difficulty at '{current_diff}'.")

    return {
        "history": updated_history,
        "difficulty": next_diff,
        "current_question": None,
        "current_answer": None,
        "current_evaluation": None,
    }


def generate_final_report(state: InterviewState) -> dict:
    """Generates the final comprehensive interview performance report."""
    logger.info(f"Generating final interview report for session {state.get('interview_id')}")

    history = state.get("history") or []
    if not history:
        raise ValueError("Cannot generate final report: Interview history is empty.")

    # Format history transcript for the LLM
    transcript_parts = []
    for i, item in enumerate(history):
        transcript_parts.append(
            f"Question {i+1} [{item['question']['topic']} - {item['question']['difficulty']}]: {item['question']['question']}\n"
            f"Candidate Answer: {item['answer']['answer']}\n"
            f"AI Evaluation Score: {item['evaluation']['score']}/10\n"
            f"Feedback: {item['evaluation']['feedback']}\n"
        )
    history_transcript = "\n---\n".join(transcript_parts)

    chain = get_report_generation_chain()
    res = safe_invoke(
        chain,
        {
            "role": state.get("role"),
            "experience_level": state.get("experience_level"),
            "history": history_transcript,
        },
        operation="generating the final report",
    )

    # Deterministic scoring: overall score is the average of per-question composite
    # scores scaled to 0-100; topic performance is computed per topic.
    question_scores = [
        item["evaluation"]["score"] for item in history if item.get("evaluation")
    ]
    deterministic_overall_score = overall_score(question_scores)
    deterministic_topic_performance = topic_performance(history)

    report_dict = {
        "overall_score": deterministic_overall_score,
        "strengths": res.strengths,
        "weaknesses": res.weaknesses,
        "topic_performance": deterministic_topic_performance,
        "recommendations": res.recommendations,
        "interview_summary": res.interview_summary,
    }

    return {
        "final_report": report_dict,
        "overall_score": deterministic_overall_score,
        "status": "completed",
    }
