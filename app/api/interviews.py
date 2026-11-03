from typing import List
from fastapi import APIRouter, HTTPException, status

from app.schemas.answer import AnswerSubmit, AnswerSubmitResponse
from app.schemas.evaluation import HumanReviewSubmit
from app.schemas.interview import (
    DashboardStatsResponse,
    DetailedInterviewResponse,
    InterviewCreate,
    InterviewResponse,
    InterviewStartResponse,
)
from app.schemas.result import FinalResultResponse
from app.services.interview_service import (
    continue_interview_session,
    create_interview,
    delete_interview,
    get_dashboard_stats,
    get_interview,
    list_interviews,
    start_interview_session,
    submit_answer_to_session,
)

router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"],
)


@router.post(
    "",
    response_model=InterviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new interview session",
    include_in_schema=False,
)
@router.post(
    "/",
    response_model=InterviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new interview session",
    description="Registers a new mock interview session with candidate preferences.",
    responses={
        422: {
            "description": "Validation error (missing/invalid fields, unsupported enum values)",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"loc": ["body", "role"], "msg": "field required", "type": "missing"}
                        ]
                    }
                }
            },
        }
    },
)
def create_new_interview(data: InterviewCreate):
    return create_interview(data)


@router.get(
    "",
    response_model=List[DetailedInterviewResponse],
    status_code=status.HTTP_200_OK,
    summary="List all interview sessions",
    include_in_schema=False,
)
@router.get(
    "/",
    response_model=List[DetailedInterviewResponse],
    status_code=status.HTTP_200_OK,
    summary="List all interview sessions",
    description="Returns a list of all historical and active interview sessions.",
)
def get_all_interviews():
    return list_interviews()



@router.get(
    "/stats/summary",
    response_model=DashboardStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get aggregated dashboard statistics",
    description="Calculates real statistics across all completed and active interviews.",
)
def get_stats():
    return get_dashboard_stats()


@router.get(
    "/{interview_id}",
    response_model=DetailedInterviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current interview state and history",
    description="Returns full information about the interview state, the current question, pending evaluation (when paused), and past chat history.",
    responses={
        404: {
            "description": "Interview session not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Interview session '<interview_id>' not found."}
                }
            },
        }
    },
)
def get_interview_by_id(interview_id: str):
    interview = get_interview(interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session '{interview_id}' not found.",
        )
    return interview


@router.delete(
    "/{interview_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an interview session",
    description="Removes an interview from history.",
)
def delete_interview_by_id(interview_id: str):
    success = delete_interview(interview_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session '{interview_id}' not found.",
        )
    return {"status": "deleted", "interview_id": interview_id}


@router.post(
    "/{interview_id}/start",
    response_model=InterviewStartResponse,
    status_code=status.HTTP_200_OK,
    summary="Start the interview session",
    description="Transitions the interview session to active and generates the first question.",
    responses={
        404: {"description": "Interview session not found"},
        400: {
            "description": "Invalid state transition (e.g. already started)",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Cannot start interview session. Current status is 'in_progress' but must be 'created'."
                    }
                }
            },
        },
        502: {"description": "LLM returned malformed output while generating the first question"},
        503: {"description": "LLM provider unavailable, timed out, or failed"},
    },
)
async def start_interview(interview_id: str):
    try:
        interview = await start_interview_session(interview_id)
        return {
            "interview_id": interview["interview_id"],
            "current_question_number": interview["current_question_number"],
            "question": interview["current_question"],
            "status": interview["status"],
        }
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


@router.post(
    "/{interview_id}/answer",
    response_model=AnswerSubmitResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit answer for the current question",
    description="Submits candidate answer. Triggers evaluation and next question generation (or completion). Can trigger a human review pause.",
    responses={
        404: {"description": "Interview session not found"},
        400: {
            "description": "Invalid state transition (not started, already completed, paused for human review)",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Cannot submit answer. The interview session is currently paused and awaiting human review."
                    }
                }
            },
        },
        422: {
            "description": "Validation error (empty answer)",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "answer"],
                                "msg": "String should have at least 1 character",
                                "type": "string_too_short",
                            }
                        ]
                    }
                }
            },
        },
        502: {"description": "LLM returned malformed output while evaluating the answer"},
        503: {"description": "LLM provider unavailable, timed out, or failed"},
    },
)
async def submit_answer(interview_id: str, data: AnswerSubmit):
    try:
        interview = await submit_answer_to_session(interview_id, data.answer)

        # If it paused for human review, return a paused payload
        if interview.get("needs_human_review", False):
            return {
                "evaluation": None,
                "status": interview["status"],
                "needs_human_review": True,
                "next_question": None,
            }

        # Otherwise, the evaluation of this answer is saved in the last history item
        last_history_item = interview["history"][-1]
        return {
            "evaluation": last_history_item["evaluation"],
            "status": interview["status"],
            "needs_human_review": False,
            "next_question": interview.get("current_question"),
        }
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


@router.post(
    "/{interview_id}/continue",
    response_model=AnswerSubmitResponse,
    status_code=status.HTTP_200_OK,
    summary="Resume a paused interview session",
    description="Resumes the interview after a human reviewer has approved the AI evaluation or provided a corrected evaluation.",
    responses={
        404: {"description": "Interview session not found"},
        400: {
            "description": "Invalid resume operation (session is not paused for human review)",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Cannot continue interview session. The session is not currently paused for human review."
                    }
                }
            },
        },
        422: {"description": "Validation error (invalid reviewer decision or evaluation override)"},
        502: {"description": "LLM returned malformed output while generating the next question"},
        503: {"description": "LLM provider unavailable, timed out, or failed"},
    },
)
async def resume_interview(interview_id: str, data: HumanReviewSubmit):
    try:
        modified_dict = None
        if data.modified_evaluation:
            modified_dict = data.modified_evaluation.model_dump()

        interview = await continue_interview_session(
            interview_id, approve=data.approve, modified_evaluation=modified_dict
        )

        last_history_item = interview["history"][-1]
        return {
            "evaluation": last_history_item["evaluation"],
            "status": interview["status"],
            "needs_human_review": False,
            "next_question": interview.get("current_question"),
        }
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


@router.get(
    "/{interview_id}/result",
    response_model=FinalResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Get final interview performance report",
    description="Returns the aggregated final score and feedback (only accessible if interview status is 'completed').",
    responses={
        404: {"description": "Interview session not found"},
        400: {
            "description": "Interview has not been completed yet",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Cannot fetch result. The interview session has not been completed yet."
                    }
                }
            },
        },
    },
)
def get_interview_result(interview_id: str):
    interview = get_interview(interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session '{interview_id}' not found.",
        )

    if interview["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot fetch result. The interview session has not been completed yet.",
        )

    return interview["final_report"]