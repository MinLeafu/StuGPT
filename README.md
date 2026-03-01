# StuGPT
Student GPT
# StuGPT: Adaptive Student Learning State Engine

StuGPT is a reference AI system that models a student's evolving learning state and returns explainable, actionable recommendations.

## Why this design

The implementation is organized around three requirements:

1. **Track learning interactions over time** with structured event data.
2. **Generate recommendations that are explainable** (with explicit evidence + rule triggers).
3. **Adapt to long-term behavior changes** such as inactivity or rapid growth.

## Data model: how interactions are structured

Each interaction is represented by `LearningEvent`:

- `timestamp`, `topic`, `activity_type`
- `score` and `confidence`
- effort/friction fields: `time_spent_minutes`, `hints_used`, `completed`

These are accumulated into per-topic `TopicState` records:

- `mastery`: competence estimate (0..1)
- `momentum`: short-term trajectory (improving/declining)
- `consistency`: stability of recent outcomes
- rolling evidence windows and activity timestamps

## Inference logic: how data is interpreted

### 1) Event ingestion and state updates

During ingestion, the model updates:

- **Mastery** via weighted blend of prior state and observed performance.
- **Friction adjustment** to avoid overestimating mastery when heavy hints or non-completion occur.
- **Momentum** by comparing early vs late slices of the score window.
- **Consistency** from score spread (high spread = unstable performance).

### 2) Long-term adaptation

The model includes inactivity adaptation (`apply_time_decay`):

- after sustained inactivity, mastery/momentum/consistency are decayed,
- decay is checkpointed by timestamp so repeated insight generation at the same time is stable (idempotent).

### 3) Explainable guidance generation

`generate_insights(now)` returns `Insight` objects with:

- `message` (human-readable diagnosis)
- `severity` (high / medium / opportunity)
- `evidence` (numeric context + triggered rule)
- `recommendation` (specific next action)

Built-in guidance types:

- inactivity alert (`inactive_days >= 14`)
- struggle-zone recovery (`mastery < 0.5 and momentum <= 0`)
- acceleration opportunity (`mastery >= 0.8 and momentum > 0.05`)
- inconsistency coaching (`consistency < 0.45`)

### 4) Action planning layer

`generate_action_plan(now, max_items=3)` converts insights into an ordered weekly to-do list:

- priorities: `p1` (urgent), `p2` (important), `p3` (growth/opportunity)
- explicit due windows (`due_in_days`) so students know when to act
- bounded list size to reduce cognitive overload

## Implementation layout

- `src/stugpt/learning_model.py` — core model, insights, and action planning.
- `src/stugpt/demo.py` — simulation/demo script.
- `tests/test_learning_model.py` — regression tests for core adaptation and guidance behavior.

## Run locally

```bash
PYTHONPATH=src python src/stugpt/demo.py
PYTHONPATH=src pytest -q
```

## How this can be used in a product

- **Student dashboard**: topic health + prioritized “next best action” cards.
- **Tutor bot**: explain “why this recommendation” using evidence/rule fields.
- **Intervention agent**: trigger proactive nudges for inactivity or plateau risk.
- **Instructor console**: monitor cohort-level struggle/acceleration patterns.