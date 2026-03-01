"""
Testbench Scenario 01 — Struggle Zone
======================================
A student who has been attempting Algebra repeatedly but declining in score.
Expected insight: HIGH severity, rule "mastery<0.5 and momentum<=0"
Expected action : P1, due in 1 day
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from datetime import datetime, timedelta
from stugpt import LearningEvent, StudentLearningModel

NOW = datetime(2024, 9, 1, 12, 0)

def run():
    model = StudentLearningModel()

    # Declining scores over the last 8 days
    sessions = [
        (8, 0.55, 0.6, 20, 1),
        (7, 0.48, 0.5, 20, 2),
        (6, 0.42, 0.4, 18, 3),
        (5, 0.38, 0.4, 18, 3),
        (4, 0.33, 0.3, 15, 4),
        (3, 0.28, 0.3, 15, 5),
    ]
    for days_ago, score, conf, mins, hints in sessions:
        model.ingest_event(LearningEvent(
            timestamp=NOW - timedelta(days=days_ago),
            topic="Algebra",
            activity_type="problem_set",
            score=score,
            confidence=conf,
            time_spent_minutes=mins,
            hints_used=hints,
            completed=True,
        ))

    snap = model.snapshot()["Algebra"]
    insights = model.generate_insights(NOW)
    plan = model.generate_action_plan(NOW)

    print("=" * 55)
    print("  SCENARIO 01 — Struggle Zone")
    print("=" * 55)
    print(f"\n  Mastery     : {snap['mastery']:.3f}  (expect < 0.5)")
    print(f"  Momentum    : {snap['momentum']:+.3f}  (expect <= 0)")
    print(f"  Consistency : {snap['consistency']:.3f}")

    assert insights, "FAIL: expected at least one insight"
    ins = insights[0]
    assert ins.severity == "high", f"FAIL: expected high, got {ins.severity}"
    assert ins.evidence["rule"] == "mastery<0.5 and momentum<=0", f"FAIL: wrong rule {ins.evidence['rule']}"
    assert plan[0].priority == "p1", f"FAIL: expected p1, got {plan[0].priority}"
    assert plan[0].due_in_days == 1, f"FAIL: expected due_in_days=1, got {plan[0].due_in_days}"

    print(f"\n  Insight     : [{ins.severity.upper()}] {ins.message}")
    print(f"  Rule        : {ins.evidence['rule']}")
    print(f"  Action      : {ins.recommendation}")
    print(f"\n  Plan item   : [{plan[0].priority.upper()}] due in {plan[0].due_in_days} day(s)")
    print("\n  ✅  PASS — Struggle zone detected correctly")
    print()

if __name__ == "__main__":
    run()
