"""
Testbench Scenario 04 — Inconsistency Coaching
================================================
A student whose Chemistry scores swing wildly between high and low,
producing a consistency score below 0.45 despite a fair average.
Expected insight: MEDIUM severity, rule "consistency<0.45"
Expected action : P2, due in 3 days
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from datetime import datetime, timedelta
from stugpt import LearningEvent, StudentLearningModel

NOW = datetime(2024, 9, 1, 12, 0)

def run():
    model = StudentLearningModel()

    # Volatile scores: alternating high and low
    volatile_scores = [0.85, 0.20, 0.80, 0.15, 0.90, 0.10, 0.75]
    for i, score in enumerate(volatile_scores):
        model.ingest_event(LearningEvent(
            timestamp=NOW - timedelta(days=len(volatile_scores) - i),
            topic="Chemistry",
            activity_type="quiz",
            score=score,
            confidence=0.5,
            time_spent_minutes=20,
            hints_used=0,
            completed=True,
        ))

    snap = model.snapshot()["Chemistry"]
    insights = model.generate_insights(NOW)
    plan = model.generate_action_plan(NOW)

    print("=" * 55)
    print("  SCENARIO 04 — Inconsistency Coaching")
    print("=" * 55)
    print(f"\n  Mastery     : {snap['mastery']:.3f}")
    print(f"  Momentum    : {snap['momentum']:+.3f}")
    print(f"  Consistency : {snap['consistency']:.3f}  (expect < 0.45)")

    assert insights, "FAIL: expected at least one insight"
    med = next((i for i in insights if i.severity == "medium"), None)
    assert med is not None, "FAIL: no medium insight found"
    assert med.evidence["rule"] == "consistency<0.45", f"FAIL: wrong rule {med.evidence['rule']}"
    assert snap["consistency"] < 0.45, f"FAIL: consistency {snap['consistency']} should be < 0.45"

    p2 = next((a for a in plan if a.priority == "p2"), None)
    assert p2 is not None, "FAIL: expected a p2 action item"
    assert p2.due_in_days == 3, f"FAIL: expected due_in_days=3, got {p2.due_in_days}"

    print(f"\n  Insight     : [{med.severity.upper()}] {med.message}")
    print(f"  Rule        : {med.evidence['rule']}")
    print(f"  Recent scores: {med.evidence['recent_scores']}")
    print(f"  Action      : {med.recommendation}")
    print(f"\n  Plan item   : [{p2.priority.upper()}] due in {p2.due_in_days} day(s)")
    print("\n  ✅  PASS — Inconsistency coaching triggered correctly")
    print()

if __name__ == "__main__":
    run()
