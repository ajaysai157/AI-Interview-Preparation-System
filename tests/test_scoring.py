"""Unit tests for deterministic scoring and adaptive difficulty logic."""

from app.services.scoring import next_difficulty, normalize_to_100, overall_score, topic_performance


class TestOverallScore:
    def test_empty_history_scores_zero(self):
        assert overall_score([]) == 0.0

    def test_single_question(self):
        assert overall_score([7.5]) == 75.0

    def test_average_scaled_to_100(self):
        # (7.5 + 6.0) / 2 = 6.75 -> 67.5
        assert overall_score([7.5, 6.0]) == 67.5

    def test_perfect_scores(self):
        assert overall_score([9.5, 9.5]) == 95.0

    def test_normalize_to_100_rounds_to_one_decimal(self):
        assert normalize_to_100(7.05) == 70.5


class TestTopicPerformance:
    def test_groups_by_topic_and_averages(self):
        history = [
            {"question": {"topic": "Python Core"}, "evaluation": {"score": 8.0}},
            {"question": {"topic": "Concurrency"}, "evaluation": {"score": 3.0}},
            {"question": {"topic": "Python Core"}, "evaluation": {"score": 9.0}},
        ]
        assert topic_performance(history) == {
            "Python Core": 85.0,
            "Concurrency": 30.0,
        }

    def test_skips_items_without_topic_or_score(self):
        history = [
            {"question": {"topic": "Python Core"}, "evaluation": {"score": 8.0}},
            {"question": {"topic": None}, "evaluation": {"score": 5.0}},
            {"question": {"topic": "Networking"}, "evaluation": {}},
            {},
        ]
        assert topic_performance(history) == {"Python Core": 80.0}

    def test_empty_history(self):
        assert topic_performance([]) == {}


class TestNextDifficulty:
    def test_strong_score_upgrades(self):
        assert next_difficulty("easy", 9.0, 8.0, 5.0) == "medium"
        assert next_difficulty("medium", 9.0, 8.0, 5.0) == "hard"

    def test_already_max_stays_max(self):
        assert next_difficulty("hard", 9.0, 8.0, 5.0) == "hard"

    def test_weak_score_downgrades(self):
        assert next_difficulty("hard", 3.0, 8.0, 5.0) == "medium"
        assert next_difficulty("medium", 3.0, 8.0, 5.0) == "easy"

    def test_already_min_stays_min(self):
        assert next_difficulty("easy", 3.0, 8.0, 5.0) == "easy"

    def test_average_score_keeps_difficulty(self):
        assert next_difficulty("medium", 6.0, 8.0, 5.0) == "medium"

    def test_boundary_upgrade_inclusive(self):
        # score == upgrade threshold upgrades (>=)
        assert next_difficulty("medium", 8.0, 8.0, 5.0) == "hard"

    def test_boundary_downgrade_exclusive(self):
        # score == downgrade threshold does NOT downgrade (<)
        assert next_difficulty("medium", 5.0, 8.0, 5.0) == "medium"
        assert next_difficulty("medium", 4.9, 8.0, 5.0) == "easy"

    def test_never_jumps_more_than_one_level(self):
        assert next_difficulty("easy", 10.0, 8.0, 5.0) == "medium"
        assert next_difficulty("hard", 0.0, 8.0, 5.0) == "medium"

    def test_unknown_difficulty_unchanged(self):
        assert next_difficulty("unknown", 9.0, 8.0, 5.0) == "unknown"