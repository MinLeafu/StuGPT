"""
Testbench Scenario 05 — Healthy Student (No Insights)
=======================================================
A student with stable, good scores in Biology — active recently.
Expected result: zero insights generated, empty action plan.
This verifies the model does NOT fire false positives.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from datetime import datetime, timedelta
from stugpt import LearningEvent, StudentLearningModel

NOW = datetime(2024, 9, 1, 12, 0)

def run():
    model = StudentLearningModel()

    # Stable, consistently good scores — active yesterday
    steady_scores = [0.68, 0.70, 0.71, 0.69, 0.72, 0.70]
    for i, score in enumerate(steady_scores):
        model.ingest_event(LearningEvent(
            timestamp=NOW - timedelta(days=len(steady_scores) - i),
            topic="Biology",
            activity_type="reading_quiz",
            score=score,
            confidence=0.65,
            time_spent_minutes=25,
            hints_used=0,
            completed=True,
        ))

    snap = model.snapshot()["Biology"]
    insights = model.generate_insights(NOW)
    plan = model.generate_action_plan(NOW)

    print("=" * 55)
    print("  SCENARIO 05 — Healthy Student (No Insights)")
    print("=" * 55)
    print(f"\n  Mastery     : {snap['mastery']:.3f}")
    print(f"  Momentum    : {snap['momentum']:+.3f}")
    print(f"  Consistency : {snap['consistency']:.3f}  (expect >= 0.45)")
    print(f"\n  Insights    : {len(insights)}  (expect 0)")
    print(f"  Action plan : {len(plan)} items  (expect 0)")

    assert len(insights) == 0, f"FAIL: expected 0 insights, got {len(insights)}: {[i.message for i in insights]}"
    assert len(plan) == 0, f"FAIL: expected empty plan, got {len(plan)} items"

    print("\n  ✅  PASS — No false positives for healthy student")
    print()

if __name__ == "__main__":
    run()
