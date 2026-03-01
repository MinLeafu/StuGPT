"""
Testbench Scenario 08 — Friction Effects (Hints & Incomplete Sessions)
=======================================================================
Compares three students with identical raw scores but different friction:
  - Student A : no hints, always completes        → highest mastery
  - Student B : 8 hints per session               → lower mastery
  - Student C : completes=False every session     → lowest mastery

Verifies the friction adjustments in _update_mastery work as intended.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from datetime import datetime, timedelta
from stugpt import LearningEvent, StudentLearningModel

NOW = datetime(2024, 9, 1, 12, 0)
SCORE = 0.75
CONF  = 0.70

def build_model(hints: int, completed: bool) -> StudentLearningModel:
    m = StudentLearningModel()
    for i in range(6):
        m.ingest_event(LearningEvent(
            timestamp=NOW - timedelta(days=6 - i),
            topic="Economics",
            activity_type="quiz",
            score=SCORE,
            confidence=CONF,
            time_spent_minutes=20,
            hints_used=hints,
            completed=completed,
        ))
    return m

def run():
    model_a = build_model(hints=0, completed=True)
    model_b = build_model(hints=8, completed=True)
    model_c = build_model(hints=0, completed=False)

    mastery_a = model_a.snapshot()["Economics"]["mastery"]
    mastery_b = model_b.snapshot()["Economics"]["mastery"]
    mastery_c = model_c.snapshot()["Economics"]["mastery"]

    print("=" * 55)
    print("  SCENARIO 08 — Friction Effects")
    print("=" * 55)
    print(f"\n  Raw score for all students : {SCORE}")
    print(f"\n  Student A (no hints, completed)    mastery = {mastery_a:.4f}")
    print(f"  Student B (8 hints, completed)     mastery = {mastery_b:.4f}  (expect < A)")
    print(f"  Student C (no hints, incomplete)   mastery = {mastery_c:.4f}  (expect < A)")

    assert mastery_a > mastery_b, \
        f"FAIL: hints should reduce mastery. A={mastery_a:.4f}, B={mastery_b:.4f}"
    assert mastery_a > mastery_c, \
        f"FAIL: incompletion should reduce mastery. A={mastery_a:.4f}, C={mastery_c:.4f}"

    print("\n  ✅  PASS — Hints and incompletion correctly penalise mastery")
    print()

if __name__ == "__main__":
    run()
