from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from app.graph.nodes import (
    approve_evaluation,
    evaluate_answer,
    generate_final_report,
    generate_question,
    initialize_interview,
    update_performance,
)
from app.graph.routing import route_after_evaluation, route_after_performance
from app.graph.state import InterviewState


def create_workflow():
    """Assembles and compiles the LangGraph interview workflow."""
    workflow = StateGraph(InterviewState)

    # 1. Add Nodes
    workflow.add_node("initialize_interview", initialize_interview)
    workflow.add_node("generate_question", generate_question)
    workflow.add_node("evaluate_answer", evaluate_answer)
    workflow.add_node("approve_evaluation", approve_evaluation)
    workflow.add_node("update_performance", update_performance)
    workflow.add_node("generate_final_report", generate_final_report)

    # 2. Set Entry Point
    workflow.set_entry_point("initialize_interview")

    # 3. Define Static Transitions
    workflow.add_edge("initialize_interview", "generate_question")

    # Transitions to evaluate_answer (will interrupt before executing to wait for candidate's answer)
    workflow.add_edge("generate_question", "evaluate_answer")

    # 4. Define Conditional Transitions
    # After evaluation, either go to approve_evaluation (interrupt if score < threshold) or update_performance
    workflow.add_conditional_edges(
        "evaluate_answer",
        route_after_evaluation,
        {
            "approve_evaluation": "approve_evaluation",
            "update_performance": "update_performance",
        },
    )

    # After approval/human override, progress to update_performance
    workflow.add_edge("approve_evaluation", "update_performance")

    # After updating performance, decide whether to generate next question or compile report
    workflow.add_conditional_edges(
        "update_performance",
        route_after_performance,
        {
            "generate_question": "generate_question",
            "generate_final_report": "generate_final_report",
        },
    )

    # After report generation, end session workflow
    workflow.add_edge("generate_final_report", END)

    # 5. Checkpointer for state saving and thread resumption
    memory = MemorySaver()

    # 6. Compile with interrupts
    # - Interrupt before evaluate_answer: to wait for candidate to submit an answer.
    # - Interrupt before approve_evaluation: to wait for human reviewer approval/override.
    app = workflow.compile(
        checkpointer=memory,
        interrupt_before=["evaluate_answer", "approve_evaluation"],
    )

    return app


# Single compiled application workflow instance
workflow_app = create_workflow()
