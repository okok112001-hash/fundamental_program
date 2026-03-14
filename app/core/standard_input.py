from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class StandardizedInput:
    security: Dict[str, Any] = field(default_factory=dict)
    classification: Dict[str, Any] = field(default_factory=dict)
    market: Dict[str, Any] = field(default_factory=dict)
    financials: Dict[str, Any] = field(default_factory=dict)
    derived: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


def normalize_external_payload(payload: Dict[str, Any]) -> StandardizedInput:
    return StandardizedInput(
        security=payload.get("security", {}),
        classification=payload.get("classification", {}),
        market=payload.get("market", {}),
        financials=payload.get("financials", {}),
        derived=payload.get("derived", {}),
        metadata=payload.get("metadata", {}),
    )
