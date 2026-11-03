import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.database import InterviewRecord, SessionLocal, init_db
from app.graph import workflow_app
from app.schemas.enums import InterviewStatus
from app.schemas.interview import InterviewCreate

logger = logging.getLogger(__name__)

# Initialize DB on module load
try:
    init_db()
except Exception as e:
    logger.warning(f"Database initialization warning: {e}")

# In-memory dictionary cache
interviews: Dict[str, dict] = {}


def _save_to_db(interview_dict: dict) -> None:
    """Persists or updates interview dictionary into SQLite database."""
    try:
        session = SessionLocal()
        record = session.query(InterviewRecord).filter_by(interview_id=interview_dict["interview_id"]).first()
        if not record:
            record = InterviewRecord(
                interview_id=interview_dict["interview_id"],
                role=interview_dict["role"],
                experience_level=interview_dict["experience_level"],
                interview_type=interview_dict["interview_type"],
                difficulty=interview_dict["difficulty"],
                total_questions=interview_dict.get("total_questions", 5),
            )
            session.add(record)

        record.current_question_number = interview_dict.get("current_question_number", 0)
        record.status = interview_dict.get("status", "created")
        record.overall_score = interview_dict.get("overall_score")
        record.needs_human_review = 1 if interview_dict.get("needs_human_review") else 0
        record.current_question_json = (
            json.dumps(interview_dict["current_question"]) if interview_dict.get("current_question") else None
        )
        record.current_evaluation_json = (
            json.dumps(interview_dict["current_evaluation"]) if interview_dict.get("current_evaluation") else None
        )
        record.history_json = (
            json.dumps(interview_dict["history"]) if interview_dict.get("history") is not None else "[]"
        )
        record.final_report_json = (
            json.dumps(interview_dict["final_report"]) if interview_dict.get("final_report") else None
        )

        session.commit()
        session.close()
    except Exception as exc:
        logger.error(f"Failed to persist interview to DB: {exc}")


def _load_from_db(interview_id: str) -> Optional[dict]:
    """Retrieves an interview from SQLite by ID."""
    try:
        session = SessionLocal()
        record = session.query(InterviewRecord).filter_by(interview_id=interview_id).first()
        if record:
            data = record.to_dict()
            session.close()
            return data
        session.close()
    except Exception as exc:
        logger.error(f"Failed to load interview {interview_id} from DB: {exc}")
    return None


def create_interview(data: InterviewCreate) -> dict:
    interview_id = str(uuid4())

    interview = {
        "interview_id": interview_id,
        "role": data.role,
        "experience_level": data.experience_level.value,
        "interview_type": data.interview_type.value,
        "difficulty": data.difficulty.value,
        "total_questions": data.total_questions,
        "current_question_number": 0,
        "status": InterviewStatus.CREATED.value,
        "current_question": None,
        "current_evaluation": None,
        "overall_score": None,
        "needs_human_review": False,
        "history": [],
        "final_report": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    interviews[interview_id] = interview
    _save_to_db(interview)
    return interview


def get_interview(interview_id: str) -> Optional[dict]:
    if interview_id in interviews:
        return interviews[interview_id]
    db_item = _load_from_db(interview_id)
    if db_item:
        interviews[interview_id] = db_item
        return db_item
    return None


def list_interviews() -> List[dict]:
    """Returns all interviews stored in DB and memory, sorted by recency."""
    try:
        session = SessionLocal()
        records = session.query(InterviewRecord).order_by(InterviewRecord.created_at.desc()).all()
        results = [r.to_dict() for r in records]
        session.close()
        return results
    except Exception as exc:
        logger.error(f"Failed to list interviews from DB: {exc}")
        return list(interviews.values())


def delete_interview(interview_id: str) -> bool:
    """Deletes an interview from DB and memory cache."""
    if interview_id in interviews:
        del interviews[interview_id]
    try:
        session = SessionLocal()
        record = session.query(InterviewRecord).filter_by(interview_id=interview_id).first()
        if record:
            session.delete(record)
            session.commit()
            session.close()
            return True
        session.close()
    except Exception as exc:
        logger.error(f"Failed to delete interview {interview_id}: {exc}")
    return False


def get_dashboard_stats() -> dict:
    """Aggregates real statistics across all stored interviews."""
    all_interviews = list_interviews()
    completed = [i for i in all_interviews if i.get("status") == "completed"]
    
    total_completed = len(completed)
    scores = [i.get("overall_score") for i in completed if i.get("overall_score") is not None]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
    
    # Calculate topic strengths & weaknesses from history and reports
    topic_aggregates: Dict[str, List[float]] = {}
    for item in completed:
        report = item.get("final_report") or {}
        topic_perf = report.get("topic_performance") or {}
        for topic, score in topic_perf.items():
            topic_aggregates.setdefault(topic, []).append(float(score))
    
    topic_scores = {
        topic: round(sum(vals) / len(vals), 1)
        for topic, vals in topic_aggregates.items()
    }
    
    sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
    strongest_areas = [f"{t[0]} ({t[1]}%)" for t in sorted_topics[:3]]
    improvement_areas = [f"{t[0]} ({t[1]}%)" for t in sorted_topics[-3:] if t[1] < 75.0]

    return {
        "total_interviews": len(all_interviews),
        "completed_interviews": total_completed,
        "average_score": avg_score,
        "highest_score": max(scores) if scores else 0.0,
        "topic_breakdown": topic_scores,
        "strongest_areas": strongest_areas,
        "improvement_areas": improvement_areas,
        "recent_interviews": all_interviews[:5],
    }


def validate_start_interview(interview: dict) -> None:
    status = interview.get("status")
    if status != InterviewStatus.CREATED.value:
        raise ValueError(
            f"Cannot start interview session. Current status is '{status}' but must be '{InterviewStatus.CREATED.value}'."
        )


def validate_submit_answer(interview: dict) -> None:
    status = interview.get("status")
    if status == InterviewStatus.CREATED.value:
        raise ValueError("Cannot submit answer. The interview session has not been started yet.")
    if status == InterviewStatus.COMPLETED.value:
        raise ValueError("Cannot submit answer. The interview session is already completed.")
    if status == InterviewStatus.PAUSED.value or interview.get("needs_human_review", False):
        raise ValueError("Cannot submit answer. The interview session is currently paused and awaiting human review.")


def validate_continue_interview(interview: dict) -> None:
    status = interview.get("status")
    if status != InterviewStatus.PAUSED.value and not interview.get("needs_human_review", False):
        raise ValueError("Cannot continue interview session. The session is not currently paused for human review.")


async def start_interview_session(interview_id: str) -> dict:
    interview = get_interview(interview_id)
    if not interview:
        raise ValueError(f"Interview session '{interview_id}' not found.")

    validate_start_interview(interview)

    config = {"configurable": {"thread_id": interview_id}}
    initial_state = {
        "interview_id": interview_id,
        "role": interview["role"],
        "experience_level": interview["experience_level"],
        "interview_type": interview["interview_type"],
        "difficulty": interview["difficulty"],
        "total_questions": interview["total_questions"],
        "current_question_number": 0,
        "history": [],
        "status": "created",
        "needs_human_review": False,
    }

    # Run the graph until the first interrupt (evaluate_answer)
    await workflow_app.ainvoke(initial_state, config)

    # Load updated state from checkpointer
    state = await workflow_app.aget_state(config)
    interview.update(state.values)
    interviews[interview_id] = interview
    _save_to_db(interview)
    return interview


async def submit_answer_to_session(interview_id: str, answer_text: str) -> dict:
    interview = get_interview(interview_id)
    if not interview:
        raise ValueError(f"Interview session '{interview_id}' not found.")

    validate_submit_answer(interview)

    config = {"configurable": {"thread_id": interview_id}}
    current_ans = {
        "answer_id": str(uuid4()),
        "question_id": interview["current_question"]["question_id"],
        "answer": answer_text,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }

    # Store the answer in state
    await workflow_app.aupdate_state(config, {"current_answer": current_ans})

    # Resume graph execution (enters evaluate_answer)
    await workflow_app.ainvoke(None, config)

    # Load updated state
    state = await workflow_app.aget_state(config)
    interview.update(state.values)
    interviews[interview_id] = interview
    _save_to_db(interview)
    return interview


async def continue_interview_session(
    interview_id: str, approve: bool, modified_evaluation: Optional[dict] = None
) -> dict:
    interview = get_interview(interview_id)
    if not interview:
        raise ValueError(f"Interview session '{interview_id}' not found.")

    validate_continue_interview(interview)

    config = {"configurable": {"thread_id": interview_id}}

    if modified_evaluation:
        await workflow_app.aupdate_state(config, {"current_evaluation": modified_evaluation})

    # Resume graph execution (enters approve_evaluation)
    await workflow_app.ainvoke(None, config)

    # Load updated state
    state = await workflow_app.aget_state(config)
    interview.update(state.values)
    interviews[interview_id] = interview
    _save_to_db(interview)
    return interview