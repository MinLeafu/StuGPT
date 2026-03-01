# StuGPT Testbench — Setup & Run Guide

This document walks you through setting up the project and running every testbench scenario from scratch.

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10 or later |
| pip | bundled with Python 3.10+ |

No other tools or accounts are required. All runtime code uses the Python standard library only. `pytest` is needed only for the unit tests in `tests/`.

---

## Step 1 — Get the project

If you received a zip file, unzip it. If cloning from a repo:

```bash
git clone https://github.com/yourname/stugpt.git
cd stugpt
```

Confirm the layout looks like this:

```
stugpt/
├── README.md
├── pyproject.toml
├── src/
│   └── stugpt/
│       ├── __init__.py
│       ├── learning_model.py
│       └── demo.py
├── tests/
│   └── test_learning_model.py
└── testbench/
    ├── SETUP_AND_RUN.md          ← you are here
    ├── run_all.py
    ├── scenario_01_struggle_zone.py
    ├── scenario_02_acceleration.py
    ├── scenario_03_inactivity.py
    ├── scenario_04_inconsistency.py
    ├── scenario_05_healthy_no_insights.py
    ├── scenario_06_multi_topic_priority.py
    ├── scenario_07_decay_idempotency.py
    └── scenario_08_friction_effects.py
```

---

## Step 2 — Create a virtual environment

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (Command Prompt)
python -m venv .venv
.venv\Scripts\activate.bat

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

You should see `(.venv)` prepended to your shell prompt.

---

## Step 3 — Install the package

```bash
pip install -e ".[dev]"
```

This installs `stugpt` in editable mode and also brings in `pytest` for the unit tests.

> **No internet?** The core package has zero runtime dependencies. You only need network access to install `pytest`. If offline, skip `.[dev]` and use `pip install -e .` — testbench scenarios will still run fine without pytest.

---

## Step 4 — Run the full testbench (all 8 scenarios)

```bash
python testbench/run_all.py
```

Expected output ends with:

```
============================================================
  SUMMARY
============================================================
  ✅  Struggle Zone
  ✅  Acceleration Opportunity
  ✅  Inactivity / Stale Topic
  ✅  Inconsistency Coaching
  ✅  Healthy Student — No Insights
  ✅  Multi-Topic Priority Ordering
  ✅  Time Decay Idempotency
  ✅  Friction Effects

  8/8 scenarios passed
============================================================
```

Exit code `0` means all passed. Exit code `1` means at least one scenario failed — check the output above the summary for the failing assertion message.

---

## Step 5 — Run individual scenarios

Each scenario file is a standalone script. Run any one on its own:

```bash
python testbench/scenario_01_struggle_zone.py
python testbench/scenario_02_acceleration.py
python testbench/scenario_03_inactivity.py
python testbench/scenario_04_inconsistency.py
python testbench/scenario_05_healthy_no_insights.py
python testbench/scenario_06_multi_topic_priority.py
python testbench/scenario_07_decay_idempotency.py
python testbench/scenario_08_friction_effects.py
```

Each script prints the measured values, the triggered insight rule, the recommended action, and a clear ✅ PASS or ❌ FAIL line.

---

## Step 6 — Run the demo (optional)

The demo simulates a full student history across three topics and prints a live snapshot + action plan:

```bash
python src/stugpt/demo.py
```

---

## Step 7 — Run the unit test suite (optional, requires pytest)

```bash
pytest tests/ -v
```

Or with coverage:

```bash
pytest tests/ -v --cov=stugpt --cov-report=term-missing
```

---

## Scenario reference

| File | What it tests | Expected insight |
|---|---|---|
| `scenario_01_struggle_zone.py` | Declining scores → low mastery + negative momentum | HIGH — `mastery<0.5 and momentum<=0` |
| `scenario_02_acceleration.py` | Steadily rising scores past mastery ceiling | OPPORTUNITY — `mastery>=0.8 and momentum>0.05` |
| `scenario_03_inactivity.py` | Topic abandoned 20 days ago + decay verification | HIGH — `inactivity>=14` |
| `scenario_04_inconsistency.py` | Wildly alternating scores | MEDIUM — `consistency<0.45` |
| `scenario_05_healthy_no_insights.py` | Stable, good scores, recently active | Zero insights (no false positives) |
| `scenario_06_multi_topic_priority.py` | Three topics covering all severity levels simultaneously | P1 before P2 before P3; `max_items` cap respected |
| `scenario_07_decay_idempotency.py` | Calling insights twice with the same timestamp | Mastery unchanged on repeat; advances with future timestamp |
| `scenario_08_friction_effects.py` | Same raw score, varying hints and completion | Hints and incompletion lower mastery relative to clean attempt |

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'stugpt'`**
You are running a script without the package installed. Either run `pip install -e .` first, or prefix the command with `PYTHONPATH=src`:
```bash
PYTHONPATH=src python testbench/run_all.py
```

**`python: command not found`**
Use `python3` instead of `python` on some Linux/macOS systems:
```bash
python3 testbench/run_all.py
```

**Virtual environment not activating on Windows PowerShell**
You may need to allow script execution:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
Then re-run `.venv\Scripts\Activate.ps1`.
