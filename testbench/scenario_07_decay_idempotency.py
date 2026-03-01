"""
Testbench Scenario 07 — Time Decay Idempotency
===============================================
Verifies that calling generate_insights (which triggers apply_time_decay)
multiple times with the same `now` timestamp does NOT compound the decay.
Mastery after the first call should equal mastery after the second call.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from datetime import datetime, timedelta
from stugpt import LearningEvent, StudentLearningModel

NOW = datetime(2024, 9, 1, 12, 0)

def run():
    model = StudentLearningModel()

    # Topic inactive for 21 days — decay should fire
    for days_ago in [28, 26, 24, 21]:
        model.ingest_event(LearningEvent(
            timestamp=NOW - timedelta(days=days_ago),
            topic="Geography",
            activity_type="map_quiz",
            score=0.75, confidence=0.7, time_spent_minutes=25,
            hints_used=0, completed=True,
        ))

    print("=" * 55)
    print("  SCENARIO 07 — Time Decay Idempotency")
    print("=" * 55)

    # First call
    model.generate_insights(NOW)
    mastery_first = model.snapshot()["Geography"]["mastery"]

    # Second call — same NOW, should NOT decay again
    model.generate_insights(NOW)
    mastery_second = model.snapshot()["Geography"]["mastery"]

    # Third call — still same NOW
    model.generate_insights(NOW)
    mastery_third = model.snapshot()["Geography"]["mastery"]

    print(f"\n  Mastery after call 1 : {mastery_first:.6f}")
    print(f"  Mastery after call 2 : {mastery_second:.6f}  (expect same)")
    print(f"  Mastery after call 3 : {mastery_third:.6f}  (expect same)")

    assert abs(mastery_first - mastery_second) < 1e-9, \
        f"FAIL: second call changed mastery from {mastery_first} to {mastery_second}"
    assert abs(mastery_first - mastery_third) < 1e-9, \
        f"FAIL: third call changed mastery from {mastery_first} to {mastery_third}"

    # But advancing time by 30 more days SHOULD decay further
    LATER = NOW + timedelta(days=30)
    model.generate_insights(LATER)
    mastery_later = model.snapshot()["Geography"]["mastery"]
    assert mastery_later < mastery_first, \
        f"FAIL: advancing time should reduce mastery, got {mastery_later} >= {mastery_first}"

    print(f"\n  Mastery after +30 days : {mastery_later:.6f}  (expect < {mastery_first:.6f})")
    print("\n  ✅  PASS — Decay is idempotent for same timestamp, advances with time")
    print()

if __name__ == "__main__":
    run()
