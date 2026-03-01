"""
Testbench Scenario 02 — Acceleration Opportunity
==================================================
A student who has been steadily improving in Calculus and is now ready
for transfer tasks.
Expected insight: OPPORTUNITY severity, rule "mastery>=0.8 and momentum>0.05"
Expected action : P3, due in 5 days
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from datetime import datetime, timedelta
from stugpt import LearningEvent, StudentLearningModel

NOW = datetime(2024, 9, 1, 12, 0)

def run():
    model = StudentLearningModel()

    # Rising scores — strong finish
    sessions = [
        (10, 0.55, 0.6, 25, 2),
        (8,  0.65, 0.7, 28, 1),
        (6,  0.72, 0.7, 30, 1),
        (4,  0.80, 0.8, 32, 0),
        (3,  0.85, 0.85, 35, 0),
        (2,  0.88, 0.9, 35, 0),
        (1,  0.92, 0.95, 40, 0),
    ]
    for days_ago, score, conf, mins, hints in sessions:
        model.ingest_event(LearningEvent(
            timestamp=NOW - timedelta(days=days_ago),
            topic="Calculus",
            activity_type="problem_set",
            score=score,
            confidence=conf,
            time_spent_minutes=mins,
            hints_used=hints,
            completed=True,
        ))

    snap = model.snapshot()["Calculus"]
    insights = model.generate_insights(NOW)
    plan = model.generate_action_plan(NOW)

    print("=" * 55)
    print("  SCENARIO 02 — Acceleration Opportunity")
    print("=" * 55)
    print(f"\n  Mastery     : {snap['mastery']:.3f}  (expect >= 0.8)")
    print(f"  Momentum    : {snap['momentum']:+.3f}  (expect > 0.05)")
    print(f"  Consistency : {snap['consistency']:.3f}")

    assert insights, "FAIL: expected at least one insight"
    opp = next((i for i in insights if i.severity == "opportunity"), None)
    assert opp is not None, "FAIL: no opportunity insight found"
    assert opp.evidence["rule"] == "mastery>=0.8 and momentum>0.05", f"FAIL: wrong rule {opp.evidence['rule']}"

    p3 = next((a for a in plan if a.priority == "p3"), None)
    assert p3 is not None, "FAIL: expected a p3 action item"
    assert p3.due_in_days == 5, f"FAIL: expected due_in_days=5, got {p3.due_in_days}"

    print(f"\n  Insight     : [{opp.severity.upper()}] {opp.message}")
    print(f"  Rule        : {opp.evidence['rule']}")
    print(f"  Action      : {opp.recommendation}")
    print(f"\n  Plan item   : [{p3.priority.upper()}] due in {p3.due_in_days} day(s)")
    print("\n  ✅  PASS — Acceleration opportunity detected correctly")
    print()

if __name__ == "__main__":
    run()
