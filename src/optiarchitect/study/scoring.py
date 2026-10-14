"""Scoring of the questionnaires (pure functions, no I/O)."""
from statistics import mean
from typing import Dict, Iterable, Optional

from optiarchitect.study.instruments import CONFIDENCE_IDS, SUS_IDS, USEFULNESS


def _valid(v, lo=1, hi=5) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi


def sus_score(answers: Dict[str, int]) -> Optional[float]:
    """System Usability Scale score 0-100 (Brooke, 1996), or ``None`` if any of the ten items is missing.

    Odd items contribute ``answer - 1``, even items ``5 - answer``; the sum is multiplied by 2.5.
    """
    values = [answers.get(i) for i in SUS_IDS]
    if not all(_valid(v) for v in values):
        return None
    total = sum((v - 1) if n % 2 == 1 else (5 - v) for n, v in enumerate(values, 1))
    return total * 2.5


def mean_of(ids: Iterable[str], answers: Dict[str, int]) -> Optional[float]:
    values = [answers.get(i) for i in ids]
    if not values or not all(_valid(v) for v in values):
        return None
    return round(mean(values), 4)


def confidence_change(pre: Dict[str, int], post: Dict[str, int]) -> Dict[str, Optional[float]]:
    """Per-item and mean change in self-rated confidence (post - pre)."""
    out: Dict[str, Optional[float]] = {}
    for i in CONFIDENCE_IDS:
        out[i] = (post[i] - pre[i]) if _valid(pre.get(i)) and _valid(post.get(i)) else None
    deltas = [v for v in out.values() if v is not None]
    out["mean"] = round(mean(deltas), 4) if len(deltas) == len(CONFIDENCE_IDS) else None
    return out


def derived_metrics(record: dict) -> dict:
    """Headline numbers for one participant record."""
    pre, post = record.get("pre", {}), record.get("post", {})
    problems = record.get("problems", [])
    usage = record.get("usage", {})
    change = confidence_change(pre, post)
    return {
        "sus": sus_score(post),
        "confidence_pre_mean": mean_of(CONFIDENCE_IDS, pre),
        "confidence_post_mean": mean_of(CONFIDENCE_IDS, post),
        "confidence_change_mean": change["mean"],
        "usefulness_mean": mean_of([k for k, _, _ in USEFULNESS], post),
        "n_problems": len(problems),
        "n_own_problems": sum(1 for p in problems if p.get("example") is None),
        "n_example_problems": sum(1 for p in problems if p.get("example") is not None),
        "problem_kinds": sorted({p.get("kind", "") for p in problems}),
        "usage_minutes": round(usage.get("seconds", 0) / 60.0, 1) if usage.get("seconds") is not None else None,
    }
