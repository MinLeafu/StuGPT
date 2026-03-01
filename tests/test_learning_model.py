from datetime import datetime, timedelta

from stugpt.learning_model import LearningEvent, StudentLearningModel


def test_detects_inactivity_and_creates_actionable_insight():
    model = StudentLearningModel()
    start = datetime(2026, 1, 1)

    model.ingest_event(LearningEvent(start, "Geometry", "quiz", score=0.78, confidence=0.7))
    insights = model.generate_insights(start + timedelta(days=20))

    assert any(i.topic == "Geometry" and "inactivity" in i.message for i in insights)


def test_detects_acceleration_opportunity():
    model = StudentLearningModel()
    start = datetime(2026, 1, 1)
    for i, score in enumerate([0.72, 0.84, 0.91, 0.95]):
        model.ingest_event(
            LearningEvent(start + timedelta(days=i), "Chemistry", "challenge", score=score, confidence=0.9)
        )

    insights = model.generate_insights(start + timedelta(days=5))

    assert any(i.topic == "Chemistry" and i.severity == "opportunity" for i in insights)


def test_detects_struggle_zone():
    model = StudentLearningModel()
    start = datetime(2026, 1, 1)
    for i, score in enumerate([0.44, 0.4, 0.39, 0.38]):
        model.ingest_event(
            LearningEvent(
                start + timedelta(days=i),
                "Physics",
                "practice",
                score=score,
                confidence=0.4,
                hints_used=3,
            )
        )

    insights = model.generate_insights(start + timedelta(days=5))

    assert any(i.topic == "Physics" and "struggle zone" in i.message for i in insights)


def test_time_decay_is_idempotent_for_same_timestamp():
    model = StudentLearningModel()
    start = datetime(2026, 1, 1)
    model.ingest_event(LearningEvent(start, "History", "quiz", score=0.9, confidence=0.9))

    now = start + timedelta(days=25)
    model.generate_insights(now)
    first = model.snapshot()["History"]["mastery"]

    model.generate_insights(now)
    second = model.snapshot()["History"]["mastery"]

    assert first == second


def test_insight_contains_explainability_rule_key():
    model = StudentLearningModel()
    start = datetime(2026, 1, 1)
    for i, score in enumerate([0.4, 0.38, 0.36]):
        model.ingest_event(
            LearningEvent(start + timedelta(days=i), "Writing", "practice", score=score, confidence=0.5)
        )

    insight = model.generate_insights(start + timedelta(days=4))[0]
    assert "rule" in insight.evidence


def test_generate_action_plan_prioritizes_high_severity():
    model = StudentLearningModel()
    start = datetime(2026, 1, 1)

    model.ingest_event(LearningEvent(start, "Geometry", "quiz", score=0.75, confidence=0.7))

    for i, score in enumerate([0.88, 0.9, 0.92]):
        model.ingest_event(
            LearningEvent(start + timedelta(days=i), "Chemistry", "challenge", score=score, confidence=0.9)
        )

    plan = model.generate_action_plan(start + timedelta(days=21), max_items=2)

    assert plan[0].topic == "Geometry"
    assert plan[0].priority == "p1"
    assert plan[0].due_in_days == 1


def test_generate_action_plan_is_bounded_by_max_items():
    model = StudentLearningModel()
    start = datetime(2026, 1, 1)

    model.ingest_event(LearningEvent(start, "TopicA", "quiz", score=0.7, confidence=0.6))
    model.ingest_event(LearningEvent(start, "TopicB", "quiz", score=0.4, confidence=0.4))
    model.ingest_event(LearningEvent(start, "TopicC", "quiz", score=0.8, confidence=0.6))

    plan = model.generate_action_plan(start + timedelta(days=20), max_items=1)

    assert len(plan) == 1