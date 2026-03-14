from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class GateResult:
    status: str
    gate_stage: str
    gate_reasons: List[str] = field(default_factory=list)
    confidence_allowed: bool = False


def finalize_gate_fail(stage: str, reasons: List[str], confidence_minimum_inputs_available: bool) -> GateResult:
    return GateResult(
        status="gate_fail",
        gate_stage=stage,
        gate_reasons=reasons,
        confidence_allowed=confidence_minimum_inputs_available,
    )
