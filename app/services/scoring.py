"""Deterministic interview scoring and adaptive-difficulty helpers.

The aggregated numbers shown in the final report are computed locally from the
per-question LLM evaluations (each a composite 0-10 score). This keeps scoring
transparent, deterministic, and unit-testable — independent of free-form numbers
that the language model might happen to emit.
"""

from typing import Dict, List


def normalize_to_100(score: float) -> float:
    """Converts a 0-10 composite score to the 0-100 scale."""
    return round(float(score) * 10, 1)


def overall_score(question_scores: List[float]) -> float:
    """Aggregates per-question composite scores (0-10) into an overall 0-100 score."""
    if not question_scores:
        return 0.0
    average = sum(question_scores) / len(question_scores)
    return normalize_to_100(average)


def topic_performance(history: List[dict]) -> Dict[str, float]:
    """Computes deterministic per-topic performance (0-100) from interview history.

    Each history item is expected to contain a ``question`` (with ``topic``) and an
    ``evaluation`` (with ``score``). Topics with no evaluation are skipped.
    """
    topic_scores: Dict[str, List[float]] = {}
    for item in history:
        question = item.get("question") or {}
        evaluation = item.get("evaluation") or {}
        topic = question.get("topic")
        score = evaluation.get("score")
        if topic and score is not None:
            topic_scores.setdefault(topic, []).append(float(score))

    return {
        topic: normalize_to_100(sum(scores) / len(scores))
        for topic, scores in topic_scores.items()
    }


def next_difficulty(
    current: str,
    score: float,
    upgrade_threshold: float,
    downgrade_threshold: float,
) -> str:
    """Adapts difficulty one step at a time based on the latest composite score.

    - score >= upgrade_threshold   -> increase difficulty (never more than one level)
    - score <  downgrade_threshold -> decrease difficulty (never more than one level)
    - otherwise                    -> keep the current difficulty

    Unknown difficulty values are returned unchanged.
    """
    ordering = ["easy", "medium", "hard"]
    if current not in ordering:
        return current
    index = ordering.index(current)
    if score >= upgrade_threshold and index < len(ordering) - 1:
        return ordering[index + 1]
    if score < downgrade_threshold and index > 0:
        return ordering[index - 1]
    return current