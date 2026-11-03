from app.graph.state import InterviewState


def route_after_evaluation(state: InterviewState) -> str:
    """Routes the workflow after answer evaluation based on human review requirement."""
    if state.get("needs_human_review", False):
        return "approve_evaluation"
    return "update_performance"


def route_after_performance(state: InterviewState) -> str:
    """Routes the workflow after performance update.

    Returns 'generate_final_report' if all questions have been asked, otherwise 'generate_question'.
    """
    current_num = state.get("current_question_number") or 0
    total_num = state.get("total_questions") or 5

    if current_num >= total_num:
        return "generate_final_report"
    return "generate_question"
