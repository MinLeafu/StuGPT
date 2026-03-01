"""
run_all.py — Execute every testbench scenario in sequence.
Prints a summary pass/fail table at the end.
Usage:  python testbench/run_all.py
"""

import sys
import os
import importlib
import traceback

# Ensure src/ is importable regardless of where this script is called from
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

SCENARIOS = [
    ("scenario_01_struggle_zone",       "Struggle Zone"),
    ("scenario_02_acceleration",        "Acceleration Opportunity"),
    ("scenario_03_inactivity",          "Inactivity / Stale Topic"),
    ("scenario_04_inconsistency",       "Inconsistency Coaching"),
    ("scenario_05_healthy_no_insights", "Healthy Student — No Insights"),
    ("scenario_06_multi_topic_priority","Multi-Topic Priority Ordering"),
    ("scenario_07_decay_idempotency",   "Time Decay Idempotency"),
    ("scenario_08_friction_effects",    "Friction Effects"),
]

def main():
    testbench_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, testbench_dir)

    results = []

    print("\n" + "=" * 60)
    print("  StuGPT Testbench — Running all scenarios")
    print("=" * 60 + "\n")

    for module_name, label in SCENARIOS:
        try:
            mod = importlib.import_module(module_name)
            mod.run()
            results.append((label, "PASS", None))
        except AssertionError as e:
            results.append((label, "FAIL", str(e)))
            print(f"  ❌  FAIL — {label}")
            print(f"       {e}\n")
        except Exception as e:
            results.append((label, "ERROR", traceback.format_exc()))
            print(f"  💥  ERROR — {label}")
            traceback.print_exc()
            print()

    # Summary table
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, status, _ in results if status == "PASS")
    total  = len(results)
    for label, status, _ in results:
        icon = "✅" if status == "PASS" else ("❌" if status == "FAIL" else "💥")
        print(f"  {icon}  {label}")
    print(f"\n  {passed}/{total} scenarios passed")
    print("=" * 60 + "\n")

    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
