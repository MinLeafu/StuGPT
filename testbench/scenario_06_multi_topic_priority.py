"""
Testbench Scenario 06 — Multi-Topic Priority Ordering
=======================================================
Three topics simultaneously active:
  - History   : stale (20 days inactive)       → HIGH   → P1
  - Statistics : inconsistent scores            → MEDIUM → P2
  - Calculus  : accelerating                   → OPPORTUNITY → P3

Verifies that generate_action_plan returns items in correct priority order
and that max_items cap is respected.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from datetime import datetime, timedelta
from stugpt import LearningEvent, StudentLearningModel

NOW = datetime(2024, 9, 1, 12, 0)

def run():
    model = StudentLearningModel()

    # History — stale (last active 20 days ago)
    for days_ago in [25, 23, 21, 20]:
        model.ingest_event(LearningEvent(
            timestamp=NOW - timedelta(days=days_ago),
            topic="History",
            activity_type="essay",
            score=0.72, confidence=0.7, time_spent_minutes=30,
            hints_used=0, completed=True,
        ))

    # Statistics — volatile scores (inconsistent)
    for i, score in enumerate([0.80, 0.20, 0.75, 0.15, 0.85, 0.10]):
        model.ingest_event(LearningEvent(
            timestamp=NOW - timedelta(days=6 - i),
            topic="Statistics",
            activity_type="quiz",
            score=score, confidence=0.5, time_spent_minutes=20,
            hints_used=0, completed=True,
        ))

    # Calculus — rising to mastery
    for i, (score, conf) in enumerate([(0.60,0.6),(0.70,0.7),(0.78,0.75),(0.84,0.8),(0.89,0.9),(0.93,0.95)]):
        model.ingest_event(LearningEvent(
            timestamp=NOW - timedelta(days=6 - i),
            topic="Calculus",
            activity_type="problem_set",
            score=score, confidence=conf, time_spent_minutes=35,
            hints_used=0, completed=True,
        ))

    insights = model.generate_insights(NOW)
    plan_full = model.generate_action_plan(NOW, max_items=10)
    plan_capped = model.generate_action_plan(NOW, max_items=2)

    print("=" * 55)
    print("  SCENARIO 06 — Multi-Topic Priority Ordering")
    print("=" * 55)
    print(f"\n  Total insights   : {len(insights)}")
    for ins in insights:
        print(f"    [{ins.severity.upper():11}] {ins.topic:12} — {ins.evidence.get('rule')}")

    print(f"\n  Full plan ({len(plan_full)} items):")
    for item in plan_full:
        print(f"    [{item.priority.upper()}] {item.topic:12} — due in {item.due_in_days}d")

    print(f"\n  Capped plan (max_items=2) → {len(plan_capped)} items:")
    for item in plan_capped:
        print(f"    [{item.priority.upper()}] {item.topic:12} — due in {item.due_in_days}d")

    # Assertions
    priorities = [item.priority for item in plan_full]
    assert len(plan_capped) <= 2, f"FAIL: capped plan has {len(plan_capped)} items, expected <= 2"

    p1_idx = next((i for i, p in enumerate(priorities) if p == "p1"), None)
    p3_idx = next((i for i, p in enumerate(priorities) if p == "p3"), None)
    if p1_idx is not None and p3_idx is not None:
        assert p1_idx < p3_idx, "FAIL: p1 should appear before p3 in the plan"

    history_item = next((a for a in plan_full if a.topic == "History"), None)
    assert history_item is not None, "FAIL: History should appear in plan"
    assert history_item.priority == "p1", f"FAIL: History should be p1, got {history_item.priority}"

    print("\n  ✅  PASS — Priority ordering and max_items cap correct")
    print()

if __name__ == "__main__":
    run()
