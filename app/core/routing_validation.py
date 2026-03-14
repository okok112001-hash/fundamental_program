from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RoutingValidationResult:
    action: str  # accepted | rerouted | unacceptable_fit
    final_template_id: str
    reasons: List[str] = field(default_factory=list)
    fit_penalty: float = 0.0


def validate_routing(preliminary_template_id: str, ctx: dict) -> RoutingValidationResult:
    if preliminary_template_id == "brokerage_asset_manager" and not ctx.get("financial_materiality", True):
        return RoutingValidationResult(
            action="rerouted",
            final_template_id="general_operating_company",
            reasons=["financial_branch_entry_not_material"],
            fit_penalty=10.0,
        )
    if ctx.get("template_mismatch"):
        return RoutingValidationResult(
            action="unacceptable_fit",
            final_template_id=preliminary_template_id,
            reasons=["template_mismatch"],
            fit_penalty=25.0,
        )
    if ctx.get("mixed_financial_group"):
        return RoutingValidationResult(
            action="accepted",
            final_template_id=preliminary_template_id,
            reasons=["mixed_financial_group"],
            fit_penalty=5.0,
        )
    return RoutingValidationResult(
        action="accepted",
        final_template_id=preliminary_template_id,
        reasons=[],
        fit_penalty=0.0,
    )
