import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.interview_service import interviews

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    interviews.clear()


def test_generate_question_handles_missing_question_index():
    from app.graph.nodes import generate_question

    state = {
        "interview_id": "test-session",
        "role": "Python Developer",
        "experience_level": "junior",
        "interview_type": "technical",
        "difficulty": "medium",
        "current_question_number": None,
        "history": [],
    }

    result = generate_question(state)

    assert result["current_question_number"] == 1
    assert result["current_question"]["question_number"] == 1
    assert result["status"] == "in_progress"


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "AI Interview System"}


def test_create_interview_validation():
    # Invalid: missing role
    response = client.post(
        "/interviews",
        json={
            "experience_level": "junior",
            "interview_type": "technical",
            "difficulty": "medium",
            "total_questions": 5,
        },
    )
    assert response.status_code == 422

    # Valid
    response = client.post(
        "/interviews",
        json={
            "role": "Python Developer",
            "experience_level": "junior",
            "interview_type": "technical",
            "difficulty": "medium",
            "total_questions": 3,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "interview_id" in data
    assert data["role"] == "Python Developer"
    assert data["status"] == "created"


def test_interview_not_found():
    response = client.get("/interviews/non-existent-id")
    assert response.status_code == 404

    response = client.post("/interviews/non-existent-id/start")
    assert response.status_code == 404


def test_complete_interview_flow():
    # 1. Create interview with 2 questions
    response = client.post(
        "/interviews",
        json={
            "role": "Python Developer",
            "experience_level": "junior",
            "interview_type": "technical",
            "difficulty": "medium",
            "total_questions": 2,
        },
    )
    assert response.status_code == 201
    interview_id = response.json()["interview_id"]

    # 2. Get detailed interview before start
    response = client.get(f"/interviews/{interview_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "created"

    # Try answering before starting
    response = client.post(f"/interviews/{interview_id}/answer", json={"answer": "My answer"})
    assert response.status_code == 400

    # 3. Start interview
    response = client.post(f"/interviews/{interview_id}/start")
    assert response.status_code == 200
    start_data = response.json()
    assert start_data["current_question_number"] == 1
    assert "question" in start_data["question"]

    # Try starting it again
    response = client.post(f"/interviews/{interview_id}/start")
    assert response.status_code == 400

    # 4. Submit first answer (Average path - score 7.5)
    response = client.post(f"/interviews/{interview_id}/answer", json={"answer": "This is a normal correct response."})
    assert response.status_code == 200
    ans_data = response.json()
    assert ans_data["needs_human_review"] is False
    assert ans_data["status"] == "in_progress"
    assert ans_data["evaluation"]["score"] == 7.5
    assert ans_data["next_question"]["question_number"] == 2

    # 5. Submit second answer (Weak answer - score 3.0, triggers human review)
    response = client.post(f"/interviews/{interview_id}/answer", json={"answer": "I don't know, this is a poor fail answer."})
    assert response.status_code == 200
    ans_data = response.json()
    assert ans_data["needs_human_review"] is True
    assert ans_data["status"] == "paused"
    assert ans_data["evaluation"] is None
    assert ans_data["next_question"] is None

    # Try to submit another answer when paused
    response = client.post(f"/interviews/{interview_id}/answer", json={"answer": "Another answer"})
    assert response.status_code == 400

    # Try getting result before completed
    response = client.get(f"/interviews/{interview_id}/result")
    assert response.status_code == 400

    # 6. Continue/resume interview with override
    response = client.post(
        f"/interviews/{interview_id}/continue",
        json={
            "approve": False,
            "modified_evaluation": {
                "score": 6.0,
                "correctness": 6.0,
                "completeness": 5.0,
                "clarity": 7.0,
                "relevance": 8.0,
                "feedback": "Modified by human reviewer.",
                "improvement_areas": ["Needs more detail"],
            },
        },
    )
    assert response.status_code == 200
    resume_data = response.json()
    assert resume_data["status"] == "completed"
    assert resume_data["evaluation"]["score"] == 6.0
    assert resume_data["next_question"] is None

    # 7. Get final report
    response = client.get(f"/interviews/{interview_id}/result")
    assert response.status_code == 200
    res_data = response.json()
    assert "overall_score" in res_data
    # 1st score: 7.5, 2nd score (modified): 6.0. Avg: 6.75 * 10 = 67.5 overall score
    assert res_data["overall_score"] == 67.5
    assert len(res_data["strengths"]) > 0


def test_approve_path_keeps_ai_evaluation():
    # 1-question interview; poor answer triggers human review
    response = client.post(
        "/interviews",
        json={
            "role": "Python Developer",
            "experience_level": "junior",
            "interview_type": "technical",
            "difficulty": "medium",
            "total_questions": 1,
        },
    )
    interview_id = response.json()["interview_id"]

    response = client.post(f"/interviews/{interview_id}/start")
    assert response.status_code == 200

    response = client.post(f"/interviews/{interview_id}/answer", json={"answer": "I gave a poor fail answer."})
    assert response.status_code == 200
    assert response.json()["needs_human_review"] is True
    assert response.json()["status"] == "paused"

    # Approve the AI evaluation without any modification
    response = client.post(
        f"/interviews/{interview_id}/continue",
        json={"approve": True},
    )
    assert response.status_code == 200
    resume_data = response.json()
    assert resume_data["status"] == "completed"
    assert resume_data["evaluation"]["score"] == 3.0
    assert resume_data["next_question"] is None


def test_resume_when_not_paused_is_rejected():
    response = client.post(
        "/interviews",
        json={
            "role": "Python Developer",
            "experience_level": "junior",
            "interview_type": "technical",
            "difficulty": "medium",
            "total_questions": 2,
        },
    )
    interview_id = response.json()["interview_id"]

    # Continue before the interview has ever paused
    response = client.post(f"/interviews/{interview_id}/continue", json={"approve": True})
    assert response.status_code == 400


def test_answer_after_completion_is_rejected():
    response = client.post(
        "/interviews",
        json={
            "role": "Python Developer",
            "experience_level": "junior",
            "interview_type": "technical",
            "difficulty": "medium",
            "total_questions": 1,
        },
    )
    interview_id = response.json()["interview_id"]
    client.post(f"/interviews/{interview_id}/start")
    client.post(f"/interviews/{interview_id}/answer", json={"answer": "A normal correct response."})
    assert client.get(f"/interviews/{interview_id}/result").status_code == 200

    response = client.post(f"/interviews/{interview_id}/answer", json={"answer": "Too late."})
    assert response.status_code == 400


def test_malformed_llm_output_returns_clean_error(monkeypatch):
    from langchain_core.exceptions import OutputParserException

    class MalformedChain:
        def invoke(self, inputs, config=None):
            raise OutputParserException("Invalid JSON output from model.")

    monkeypatch.setattr("app.graph.nodes.get_answer_evaluation_chain", lambda: MalformedChain())

    response = client.post(
        "/interviews",
        json={
            "role": "Python Developer",
            "experience_level": "junior",
            "interview_type": "technical",
            "difficulty": "medium",
            "total_questions": 1,
        },
    )
    interview_id = response.json()["interview_id"]
    client.post(f"/interviews/{interview_id}/start")

    response = client.post(f"/interviews/{interview_id}/answer", json={"answer": "My answer"})
    assert response.status_code == 502
    assert "could not be parsed" in response.json()["detail"]
    assert "Traceback" not in response.text


def test_unexpected_error_returns_generic_500(monkeypatch):
    # TestClient re-raises server exceptions by default; use a client that
    # surfaces the actual HTTP response so we can assert on the 500 body.
    import app.services.interview_service as service_module

    from_app = TestClient(app, raise_server_exceptions=False)

    class FailingWorkflowApp:
        async def ainvoke(self, *args, **kwargs):
            raise RuntimeError("internal bug")

    monkeypatch.setattr(service_module, "workflow_app", FailingWorkflowApp())

    response = from_app.post(
        "/interviews",
        json={
            "role": "Python Developer",
            "experience_level": "junior",
            "interview_type": "technical",
            "difficulty": "medium",
            "total_questions": 1,
        },
    )
    interview_id = response.json()["interview_id"]

    response = from_app.post(f"/interviews/{interview_id}/start")
    assert response.status_code == 500
    assert response.json()["detail"] == "An unexpected internal server error occurred."
    assert "RuntimeError" not in response.text


def test_strong_answer_upgrades_difficulty():
    # Strong answers (score 9.5) should upgrade difficulty from medium to hard
    response = client.post(
        "/interviews",
        json={
            "role": "Python Developer",
            "experience_level": "mid",
            "interview_type": "technical",
            "difficulty": "medium",
            "total_questions": 2,
        },
    )
    interview_id = response.json()["interview_id"]

    client.post(f"/interviews/{interview_id}/start")

    detail = client.get(f"/interviews/{interview_id}").json()
    assert detail["difficulty"] == "medium"

    response = client.post(
        f"/interviews/{interview_id}/answer",
        json={"answer": "An excellent, strong, perfect answer."},
    )
    assert response.status_code == 200
    assert response.json()["evaluation"]["score"] == 9.5

    detail = client.get(f"/interviews/{interview_id}").json()
    assert detail["difficulty"] == "hard"

    # Completing the interview produces a scaled aggregate report
    response = client.post(
        f"/interviews/{interview_id}/answer",
        json={"answer": "Another excellent, strong, perfect answer."},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"

    result = client.get(f"/interviews/{interview_id}/result")
    assert result.status_code == 200
    assert result.json()["overall_score"] == 95.0


def test_llm_unavailable_returns_503(monkeypatch):
    import app.graph.nodes as nodes_module

    class UnavailableChain:
        def invoke(self, inputs, config=None):
            raise TimeoutError("model timed out")

    monkeypatch.setattr(nodes_module, "get_question_generation_chain", lambda: UnavailableChain())

    response = client.post(
        "/interviews",
        json={
            "role": "Python Developer",
            "experience_level": "junior",
            "interview_type": "technical",
            "difficulty": "medium",
            "total_questions": 1,
        },
    )
    interview_id = response.json()["interview_id"]

    response = client.post(f"/interviews/{interview_id}/start")
    assert response.status_code == 503
    assert "Traceback" not in response.text


def test_paused_interview_exposes_pending_evaluation():
    response = client.post(
        "/interviews",
        json={
            "role": "Python Developer",
            "experience_level": "junior",
            "interview_type": "technical",
            "difficulty": "medium",
            "total_questions": 1,
        },
    )
    interview_id = response.json()["interview_id"]
    client.post(f"/interviews/{interview_id}/start")
    client.post(f"/interviews/{interview_id}/answer", json={"answer": "I gave a poor fail answer."})

    detail = client.get(f"/interviews/{interview_id}").json()
    assert detail["status"] == "paused"
    assert detail["needs_human_review"] is True
    # The pending AI evaluation must be visible for a human reviewer to approve or override
    assert detail["current_evaluation"] is not None
    assert detail["current_evaluation"]["score"] == 3.0


def test_empty_answer_is_rejected():
    response = client.post(
        "/interviews",
        json={
            "role": "Python Developer",
            "experience_level": "junior",
            "interview_type": "technical",
            "difficulty": "medium",
            "total_questions": 1,
        },
    )
    interview_id = response.json()["interview_id"]
    client.post(f"/interviews/{interview_id}/start")

    response = client.post(f"/interviews/{interview_id}/answer", json={"answer": ""})
    assert response.status_code == 422

    response = client.post(f"/interviews/{interview_id}/answer", json={})
    assert response.status_code == 422


def test_list_and_stats_endpoints():
    # 1. Test stats summary
    stats_res = client.get("/interviews/stats/summary")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert "total_interviews" in stats
    assert "completed_interviews" in stats
    assert "average_score" in stats

    # 2. Test list interviews
    list_res = client.get("/interviews")
    assert list_res.status_code == 200
    assert isinstance(list_res.json(), list)

    # 3. Create, list, delete
    create_res = client.post(
        "/interviews",
        json={
            "role": "Fullstack Engineer",
            "experience_level": "mid",
            "interview_type": "technical",
            "difficulty": "medium",
            "total_questions": 3,
        },
    )
    assert create_res.status_code == 201
    created_id = create_res.json()["interview_id"]

    # Verify present in list
    list_after = client.get("/interviews").json()
    ids = [i["interview_id"] for i in list_after]
    assert created_id in ids

    # Delete
    del_res = client.delete(f"/interviews/{created_id}")
    assert del_res.status_code == 200

    # Verify gone
    del_check = client.get(f"/interviews/{created_id}")
    assert del_check.status_code == 404

