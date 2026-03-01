"""
Testbench Scenario 03 — Inactivity / Stale Topic
==================================================
A student who did well in Physics but abandoned it 20 days ago.
Expected insight: HIGH severity, rule "inactivity>=14"
Expected action : P1, due in 1 day
Also verifies that time decay reduced mastery from its peak.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from datetime import datetime, timedelta
from stugpt import LearningEvent, StudentLearningModel

NOW = datetime(2024, 9, 1, 12, 0)

def run():
    model = StudentLearningModel()

    # Good sessions, all 20+ days ago
    sessions = [
        (25, 0.70, 0.7, 30, 1),
        (23, 0.74, 0.7, 30, 0),
        (21, 0.78, 0.8, 35, 0),
        (20, 0.82, 0.85, 35, 0),
    ]
    for days_ago, score, conf, mins, hints in sessions:
        model.ingest_event(LearningEvent(
            timestamp=NOW - timedelta(days=days_ago),
            topic="Physics",
            activity_type="lab_report",
            score=score,
            confidence=conf,
            time_spent_minutes=mins,
            hints_used=hints,
            completed=True,
        ))

    mastery_before_decay = model.snapshot()["Physics"]["mastery"]

    insights = model.generate_insights(NOW)  # triggers decay internally
    plan = model.generate_action_plan(NOW)

    snap = model.snapshot()["Physics"]

    print("=" * 55)
    print("  SCENARIO 03 — Inactivity / Stale Topic")
    print("=" * 55)
    print(f"\n  Mastery before decay : {mastery_before_decay:.3f}")
    print(f"  Mastery after decay  : {snap['mastery']:.3f}  (expect lower)")
    print(f"  Inactive days        : 20  (expect >= 14)")

    assert insights, "FAIL: expected at least one insight"
    ins = insights[0]
    assert ins.severity == "high", f"FAIL: expected high, got {ins.severity}"
    assert ins.evidence["rule"] == "inactivity>=14", f"FAIL: wrong rule {ins.evidence['rule']}"
    assert int(ins.evidence["inactive_days"]) >= 14, "FAIL: inactive_days should be >= 14"
    assert snap["mastery"] < mastery_before_decay, "FAIL: decay should have reduced mastery"
    assert plan[0].priority == "p1", f"FAIL: expected p1, got {plan[0].priority}"

    print(f"\n  Insight     : [{ins.severity.upper()}] {ins.message}")
    print(f"  Rule        : {ins.evidence['rule']}")
    print(f"  Action      : {ins.recommendation}")
    print(f"\n  Plan item   : [{plan[0].priority.upper()}] due in {plan[0].due_in_days} day(s)")
    print("\n  ✅  PASS — Inactivity alert and decay triggered correctly")
    print()

if __name__ == "__main__":
    run()
