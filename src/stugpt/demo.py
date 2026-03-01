from datetime import datetime, timedelta
from pprint import pprint

from stugpt.learning_model import LearningEvent, StudentLearningModel


if __name__ == "__main__":
    model = StudentLearningModel()
    start = datetime(2026, 1, 10, 16, 0)

    events = [
        LearningEvent(start, "Algebra", "quiz", score=0.42, confidence=0.4, hints_used=3, time_spent_minutes=24),
        LearningEvent(start + timedelta(days=1), "Algebra", "practice", score=0.47, confidence=0.5, hints_used=2, time_spent_minutes=18),
        LearningEvent(start + timedelta(days=3), "Algebra", "practice", score=0.51, confidence=0.55, hints_used=2, time_spent_minutes=20),
        LearningEvent(start + timedelta(days=4), "Biology", "quiz", score=0.81, confidence=0.7, hints_used=0, time_spent_minutes=16),
        LearningEvent(start + timedelta(days=5), "Biology", "challenge", score=0.87, confidence=0.8, hints_used=0, time_spent_minutes=19),
        LearningEvent(start + timedelta(days=6), "Biology", "challenge", score=0.91, confidence=0.85, hints_used=0, time_spent_minutes=22),
        LearningEvent(start + timedelta(days=7), "Writing", "practice", score=0.55, confidence=0.6, hints_used=0, time_spent_minutes=20),
        LearningEvent(start + timedelta(days=8), "Writing", "practice", score=0.32, confidence=0.5, hints_used=2, time_spent_minutes=20),
        LearningEvent(start + timedelta(days=9), "Writing", "practice", score=0.64, confidence=0.6, hints_used=0, time_spent_minutes=20),
    ]

    for event in events:
        model.ingest_event(event)

    now = start + timedelta(days=24)
    print("Current state snapshot:")
    pprint(model.snapshot())

    print("\nGenerated insights:")
    insights = model.generate_insights(now)
    for insight in insights:
        pprint(insight)

    print("\nAction plan:")
    for action_item in model.generate_action_plan(now):
        pprint(action_item)