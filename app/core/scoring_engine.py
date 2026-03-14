from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.core.loaders import load_json_config
from app.core.score_rules import apply_one_dimension_defense, weighted_average

TEMPLATE_WEIGHTS: Dict[str, Tuple[float, float, float]] = {
    "general_operating_company": (40, 35, 25),
    "cyclical_company": (35, 40, 25),
    "commodity_energy_producer": (30, 45, 25),
    "software_saas": (40, 35, 25),
    "digital_platform_marketplace": (35, 40, 25),
    "regulated_utility_infrastructure": (30, 50, 20),
    "bank": (35, 45, 20),
    "insurance": (35, 45, 20),
    "brokerage_asset_manager": (35, 40, 25),
    "reit_income_asset": (35, 40, 25),
    "holding_company": (30, 40, 30),
}

TEMPLATE_METRIC_MAP = load_json_config("template_metric_map.json")


def get_template_components(template_id: str) -> Dict[str, List[str]]:
    return TEMPLATE_METRIC_MAP.get(template_id, {}).get("components", {})


def get_template_min_component_coverage(template_id: str) -> Dict[str, float]:
    return TEMPLATE_METRIC_MAP.get(template_id, {}).get("minimum_effective_component_coverage", {})



def metric_from_dims(level: float | None = None, trend: float | None = None, stability: float | None = None) -> float | None:
    dims = []
    if level is not None:
        dims.append((level, 40.0))
    if trend is not None:
        dims.append((trend, 35.0))
    if stability is not None:
        dims.append((stability, 25.0))
    if not dims:
        return None
    observed = weighted_average(dims)
    if len(dims) == 1:
        return apply_one_dimension_defense(observed)
    return observed


def component_score(metric_values: List[float | None]) -> float | None:
    valid = [m for m in metric_values if m is not None]
    if not valid:
        return None
    return sum(valid) / len(valid)


def axis_score(component_scores: List[float | None], min_coverage: float = 0.5) -> tuple[float | None, bool]:
    total = len(component_scores)
    valid = [c for c in component_scores if c is not None]
    coverage = len(valid) / total if total else 0.0
    if total == 0 or coverage < min_coverage:
        return None, False
    return sum(valid) / len(valid), True


def score_template(template_id: str, subscores: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
    components_cfg = get_template_components(template_id)
    if not components_cfg:
        return {"scores": None, "subscores": subscores, "gate_reason": None}
    axes = components_cfg
    mins = get_template_min_component_coverage(template_id)
    raw_axes: Dict[str, float] = {}
    gate_reason = None
    for axis_name, components in axes.items():
        axis_sub = subscores.get(axis_name, {})
        comp_vals = [axis_sub.get(name) for name in components]
        raw, ok = axis_score(comp_vals, mins.get(axis_name, 0.5))
        if not ok:
            gate_reason = "required_axis_coverage_insufficient"
            return {"scores": None, "subscores": subscores, "gate_reason": gate_reason}
        raw_axes[axis_name] = raw  # type: ignore[assignment]
    w1, w2, w3 = TEMPLATE_WEIGHTS[template_id]
    total = round((raw_axes["axis_1"] * w1 + raw_axes["axis_2"] * w2 + raw_axes["axis_3"] * w3) / 100.0, 1)
    return {
        "scores": {
            "raw": {
                "axis_1": round(raw_axes["axis_1"], 1),
                "axis_2": round(raw_axes["axis_2"], 1),
                "axis_3": round(raw_axes["axis_3"], 1),
                "total": total,
            },
            "display": {
                "axis_1": round(raw_axes["axis_1"] / 10.0, 1),
                "axis_2": round(raw_axes["axis_2"] / 10.0, 1),
                "axis_3": round(raw_axes["axis_3"] / 10.0, 1),
                "total": total,
            },
        },
        "subscores": subscores,
        "gate_reason": None,
    }
