"""Maturity scoring: domain averages, gaps to target, impact-weighted priority and consensus."""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


@dataclass
class DomainScore:
    name: str
    current: float
    target: float
    impact: int
    spread: float  # standard deviation of stakeholder scores: how much they disagree
    by_stakeholder: dict

    gap = property(lambda s: round(max(0.0, s.target - s.current), 2))
    priority = property(lambda s: round(s.gap * s.impact, 2))   # weight the gap by business impact

    @property
    def consensus(self) -> str:
        return "Strong" if self.spread < 0.6 else "Moderate" if self.spread < 1.0 else "Weak"


def level_name(score: float, levels: list[str]) -> str:
    return levels[min(len(levels) - 1, int(round(score)))]


def score(responses: dict, framework: dict) -> list[DomainScore]:
    results = []
    for name, cfg in framework["domains"].items():
        questions = [q for q in responses["questions"] if q["domain"] == name]
        all_scores = [s for q in questions for s in q["scores"].values()]
        by_person = {p: round(statistics.mean(q["scores"][p] for q in questions), 2) for p in responses["stakeholders"]}
        results.append(DomainScore(name, round(statistics.mean(all_scores), 2), cfg["target"], cfg["impact"],
                                   round(statistics.pstdev(all_scores), 2), by_person))
    return results


def overall(domains: list[DomainScore]) -> tuple[float, float]:
    """Impact-weighted current and target maturity."""
    weight = sum(d.impact for d in domains)
    return (round(sum(d.current * d.impact for d in domains) / weight, 2),
            round(sum(d.target * d.impact for d in domains) / weight, 2))
