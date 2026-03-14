from __future__ import annotations

from typing import Any, Dict, Optional


def availability_from_value(value: Any) -> str:
    if value == "STRUCTURALLY_NA":
        return "structurally_not_applicable"
    if value is None:
        return "missing"
    return "observed"


def choose_metric_value(direct: Any = None, proxy: Any = None, structurally_not_applicable: bool = False) -> tuple[Optional[float], str]:
    if structurally_not_applicable:
        return None, "structurally_not_applicable"
    if direct is not None:
        return float(direct), "observed"
    if proxy is not None:
        return float(proxy), "proxy_used"
    return None, "missing"


def confidence_minimum_inputs_available(metadata: Dict[str, Any]) -> bool:
    completeness = metadata.get("data_completeness_raw")
    fit = metadata.get("template_fit_certainty_raw")
    clarity = metadata.get("normalization_clarity_raw")
    stability = metadata.get("structural_stability_raw")
    if completeness is None or fit is None:
        return False
    return clarity is not None or stability is not None
