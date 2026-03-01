from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from statistics import mean
from typing import Dict, List, Literal, Optional


@dataclass
class LearningEvent:
    """Represents a single learning interaction."""

    timestamp: datetime
    topic: str
    activity_type: str
    score: Optional[float] = None
    confidence: Optional[float] = None
    time_spent_minutes: float = 0.0
    hints_used: int = 0
    completed: bool = True


@dataclass
class TopicState:
    """Aggregated evolving state for a single topic."""

    topic: str
    mastery: float = 0.4
    momentum: float = 0.0
    consistency: float = 0.5
    last_active_at: Optional[datetime] = None
    total_attempts: int = 0
    recent_scores: List[float] = field(default_factory=list)
    recent_time_spent: List[float] = field(default_factory=list)
    last_decay_checkpoint: Optional[datetime] = None

    def register_event(self, event: LearningEvent, window: int = 8) -> None:
        self.total_attempts += 1
        self.last_active_at = event.timestamp
        self.last_decay_checkpoint = event.timestamp

        if event.score is not None:
            self.recent_scores.append(max(0.0, min(event.score, 1.0)))
            self.recent_scores = self.recent_scores[-window:]

        self.recent_time_spent.append(max(event.time_spent_minutes, 0.0))
        self.recent_time_spent = self.recent_time_spent[-window:]

        self._update_mastery(event)
        self._update_momentum()
        self._update_consistency()

    def _update_mastery(self, event: LearningEvent) -> None:
        observed = event.score if event.score is not None else self.mastery
        confidence = event.confidence if event.confidence is not None else 0.5

        friction_penalty = min(event.hints_used * 0.015, 0.12)
        completion_boost = 0.03 if event.completed else -0.08
        effective_observed = max(0.0, min(observed - friction_penalty + completion_boost, 1.0))

        alpha = 0.25 + (0.35 * confidence)
        self.mastery = max(0.0, min(((1 - alpha) * self.mastery) + (alpha * effective_observed), 1.0))

    def _update_momentum(self) -> None:
        if len(self.recent_scores) < 3:
            self.momentum = 0.0
            return

        mid = len(self.recent_scores) // 2
        first_half = mean(self.recent_scores[:mid])
        second_half = mean(self.recent_scores[mid:])
        self.momentum = second_half - first_half

    def _update_consistency(self) -> None:
        if not self.recent_scores:
            self.consistency = 0.5
            return

        spread = max(self.recent_scores) - min(self.recent_scores)
        self.consistency = max(0.0, min(1.0 - spread, 1.0))


@dataclass
class Insight:
    topic: str
    severity: Literal["high", "medium", "opportunity"]
    message: str
    evidence: Dict[str, float | int | str]
    recommendation: str


@dataclass
class ActionItem:
    """Concrete next step generated from one or more insights."""

    topic: str
    priority: Literal["p1", "p2", "p3"]
    action: str
    rationale: str
    due_in_days: int


class StudentLearningModel:
    """Tracks evolving learning state and produces explainable guidance."""

    def __init__(self) -> None:
        self.topic_states: Dict[str, TopicState] = {}
        self.global_last_activity: Optional[datetime] = None

    def ingest_event(self, event: LearningEvent) -> None:
        state = self.topic_states.setdefault(event.topic, TopicState(topic=event.topic))
        state.register_event(event)
        self.global_last_activity = max([d for d in [self.global_last_activity, event.timestamp] if d is not None])

    def apply_time_decay(self, now: datetime) -> None:
        """Adapt the model to inactivity by decaying estimates once per elapsed day."""
        for state in self.topic_states.values():
            if state.last_active_at is None:
                continue

            checkpoint = state.last_decay_checkpoint or state.last_active_at
            if now <= checkpoint:
                continue

            elapsed_days = (now - checkpoint).days
            if elapsed_days <= 0:
                continue

            inactive_days = (now - state.last_active_at).days
            if inactive_days < 7:
                state.last_decay_checkpoint = now
                continue

            decay_factor = min(elapsed_days * 0.006, 0.25)
            state.mastery = max(0.0, state.mastery * (1 - decay_factor))
            state.momentum = state.momentum * (1 - min(decay_factor * 1.5, 0.45))
            state.consistency = max(0.0, state.consistency - min(decay_factor * 0.7, 0.2))
            state.last_decay_checkpoint = now

    def generate_insights(self, now: datetime) -> List[Insight]:
        self.apply_time_decay(now)

        insights: List[Insight] = []
        for topic, state in self.topic_states.items():
            inactive_days = (now - state.last_active_at).days if state.last_active_at else 0

            if inactive_days >= 14:
                insights.append(
                    Insight(
                        topic=topic,
                        severity="high",
                        message=f"{topic} appears stale after {inactive_days} days of inactivity.",
                        evidence={
                            "inactive_days": inactive_days,
                            "mastery": round(state.mastery, 2),
                            "consistency": round(state.consistency, 2),
                            "rule": "inactivity>=14",
                        },
                        recommendation=(
                            "Do a 15-minute retrieval practice session today and schedule two short "
                            "refreshers this week."
                        ),
                    )
                )
                continue

            if state.mastery < 0.5 and state.momentum <= 0:
                insights.append(
                    Insight(
                        topic=topic,
                        severity="high",
                        message=f"{topic} is in a struggle zone: low mastery and no upward trend.",
                        evidence={
                            "mastery": round(state.mastery, 2),
                            "momentum": round(state.momentum, 2),
                            "attempts": state.total_attempts,
                            "rule": "mastery<0.5 and momentum<=0",
                        },
                        recommendation=(
                            "Switch to scaffolded practice (worked example -> guided question -> "
                            "independent attempt) for the next 3 sessions."
                        ),
                    )
                )
            elif state.mastery >= 0.8 and state.momentum > 0.05:
                insights.append(
                    Insight(
                        topic=topic,
                        severity="opportunity",
                        message=f"{topic} is accelerating. You are ready for transfer tasks.",
                        evidence={
                            "mastery": round(state.mastery, 2),
                            "momentum": round(state.momentum, 2),
                            "consistency": round(state.consistency, 2),
                            "rule": "mastery>=0.8 and momentum>0.05",
                        },
                        recommendation=(
                            "Attempt one mixed-topic challenge and explain your solution in your "
                            "own words to lock in deeper understanding."
                        ),
                    )
                )
            elif state.consistency < 0.45:
                insights.append(
                    Insight(
                        topic=topic,
                        severity="medium",
                        message=f"{topic} performance is inconsistent even when average scores are fair.",
                        evidence={
                            "mastery": round(state.mastery, 2),
                            "consistency": round(state.consistency, 2),
                            "recent_scores": ",".join(str(round(v, 2)) for v in state.recent_scores[-5:]),
                            "rule": "consistency<0.45",
                        },
                        recommendation=(
                            "Reduce variance by using a fixed routine: 5-minute recap, 2 core "
                            "problems, then 1 reflection note after each session."
                        ),
                    )
                )

        return insights

    def generate_action_plan(self, now: datetime, max_items: int = 3) -> List[ActionItem]:
        """Convert insights into prioritized, concrete steps students can execute this week."""
        insights = self.generate_insights(now)
        severity_rank = {"high": 0, "medium": 1, "opportunity": 2}

        ordered = sorted(
            insights,
            key=lambda i: (
                severity_rank[i.severity],
                -float(i.evidence.get("inactive_days", 0)),
                i.topic,
            ),
        )

        action_items: List[ActionItem] = []
        for insight in ordered[:max_items]:
            if insight.severity == "high":
                priority: Literal["p1", "p2", "p3"] = "p1"
                due_in_days = 1
            elif insight.severity == "medium":
                priority = "p2"
                due_in_days = 3
            else:
                priority = "p3"
                due_in_days = 5

            action_items.append(
                ActionItem(
                    topic=insight.topic,
                    priority=priority,
                    action=insight.recommendation,
                    rationale=insight.message,
                    due_in_days=due_in_days,
                )
            )

        return action_items

    def snapshot(self) -> Dict[str, Dict[str, float | int | str | None]]:
        return {
            topic: {
                "mastery": round(state.mastery, 3),
                "momentum": round(state.momentum, 3),
                "consistency": round(state.consistency, 3),
                "attempts": state.total_attempts,
                "last_active_at": state.last_active_at.isoformat() if state.last_active_at else None,
                "last_decay_checkpoint": (
                    state.last_decay_checkpoint.isoformat() if state.last_decay_checkpoint else None
                ),
            }
            for topic, state in self.topic_states.items()
        }