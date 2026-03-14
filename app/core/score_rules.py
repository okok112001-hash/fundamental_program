from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


NEUTRAL_SCORE = 50.0


def weighted_average(values: Iterable[tuple[float, float]]) -> float:
    values = list(values)
    total_weight = sum(w for _, w in values)
    if total_weight == 0:
        raise ValueError("total_weight must be > 0")
    return sum(v * w for v, w in values) / total_weight


def apply_one_dimension_defense(observed_score: float, shrinkage_strength: float = 0.3) -> float:
    """
    Default V1.x guidance:
    - when only one valid dimension exists, shrink toward neutral
    - exact coefficient remains tunable
    """
    return observed_score * (1 - shrinkage_strength) + NEUTRAL_SCORE * shrinkage_strength
