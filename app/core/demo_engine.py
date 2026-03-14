from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Optional

from app.core.loaders import load_golden_set
from app.core.scoring_engine import score_template
from app.services.explanations import build_explanations


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _base_payload(ticker: str, name: str, template_id: str, routing_reason: str, status: str, gate_stage: str):
    return {
        "security": {
            "name": name,
            "ticker": ticker,
            "exchange": "DEMO",
            "country": "US",
            "asset_class": "equity" if status != "unsupported_asset" else "etf",
            "sector": None,
            "industry": None,
            "peer_group_id": None,
            "price_currency": "USD",
            "reporting_currency": "USD" if status != "unsupported_asset" else None,
        },
        "classification": {
            "template_id": template_id,
            "template_label": template_id,
            "dominant_segment": None,
            "routing_reason": [r.strip().replace(" ", "_").replace(";", "") for r in routing_reason.split(";")],
            "compare_scope": "동일 템플릿 내 비교 적합" if status == "analyzed" else "비교 부적합",
        },
        "analysis": {
            "status": status,
            "gate_stage": gate_stage,
            "gate_reasons": [],
            "confidence_score": None,
        },
        "ui_labels": {},
        "scores": {"raw": None, "display": None},
        "subscores": None,
        "flags": [],
        "explanations": {"axis_1": None, "axis_2": None, "axis_3": None, "summary": ""},
        "meta": {
            "analysis_timestamp": _now(),
            "price_timestamp": _now(),
            "latest_financial_period": None,
            "latest_filing_date": None,
            "valuation_currency": "USD",
            "currency_mismatch_flag": False,
            "fx_rate_applied": 1.0,
            "fx_rate_timestamp": _now(),
            "fx_source": None,
            "fx_normalization_method": "same_currency",
            "confidence_breakdown": None,
            "analysis_version": "v1.4-final-crosscheck-complete",
        },
    }


def _demo_subscores(template_id: str) -> Dict[str, Dict[str, float]]:
    if template_id == "general_operating_company":
        return {
            "axis_1": {"growth_quality": 74.0, "margin_quality": 79.0, "capital_efficiency": 70.0, "cash_conversion": 65.0},
            "axis_2": {"competitive_durability": 72.0, "management_capital_allocation": 63.0, "financial_resilience": 78.0, "business_external_risk": 58.0},
            "axis_3": {"relative_valuation": 61.0, "absolute_value": 69.0, "implied_expectation": 54.0},
        }
    if template_id == "bank":
        return {
            "axis_1": {"normalized_earning_power": 70.0, "spread_quality": 68.0, "operating_efficiency": 62.0, "fee_diversification": 58.0},
            "axis_2": {"capital_adequacy": 75.0, "asset_quality": 72.0, "funding_liquidity": 70.0, "regulation_governance": 60.0},
            "axis_3": {"pb_vs_roe": 57.0, "dividend_sustainability": 65.0, "relative_valuation": 59.0},
        }
    if template_id == "reit_income_asset":
        return {
            "axis_1": {"affo_per_share": 73.0, "noi_growth": 66.0, "dividend_coverage": 70.0, "occupancy_rent_trend": 64.0},
            "axis_2": {"leverage_ltv": 62.0, "interest_coverage_refinancing": 60.0, "tenant_asset_diversification": 68.0, "lease_quality_wale": 71.0, "maintenance_capex_burden": 59.0},
            "axis_3": {"p_affo": 56.0, "nav_discount_premium": 61.0, "yield_spread_caprate_value": 58.0},
        }
    return {
        "axis_1": {"growth_quality": 65.0, "margin_quality": 60.0, "capital_efficiency": 58.0, "cash_conversion": 55.0},
        "axis_2": {"competitive_durability": 60.0, "management_capital_allocation": 58.0, "financial_resilience": 57.0, "business_external_risk": 52.0},
        "axis_3": {"relative_valuation": 55.0, "absolute_value": 53.0, "implied_expectation": 50.0},
    }


def build_demo_response(ticker: str) -> Dict:
    rows = {row["ticker"]: row for row in load_golden_set()}
    row = rows.get(ticker)
    if row is None:
        row = {
            "ticker": ticker,
            "security_name": ticker,
            "template_id": "general_operating_company",
            "routing_reason": "non_financial_operating_company",
            "status": "analyzed",
            "gate_stage": "all_passed",
        }
    payload = _base_payload(
        row["ticker"],
        row["security_name"],
        row["template_id"],
        row["routing_reason"],
        row["status"],
        row["gate_stage"],
    )
    status = row["status"]
    if status == "analyzed":
        subscores = _demo_subscores(row["template_id"])
        result = score_template(row["template_id"], subscores)
        payload["scores"] = result["scores"]
        payload["subscores"] = subscores
        payload["analysis"]["confidence_score"] = {"raw": 81.0, "display": 8.1}
        payload["meta"]["confidence_breakdown"] = {
            "data_completeness": 90.0,
            "template_fit_certainty": 88.0,
            "normalization_clarity": 78.0,
            "structural_stability": 81.0,
        }
        payload["explanations"] = build_explanations("analyzed", subscores=subscores, score_display=result["scores"]["display"])
    elif status == "gate_fail":
        payload["analysis"]["gate_reasons"] = ["model_insufficient_data"]
        payload["analysis"]["confidence_score"] = {"raw": 62.0, "display": 6.2}
        payload["meta"]["confidence_breakdown"] = {
            "data_completeness": 85.0,
            "template_fit_certainty": 80.0,
            "normalization_clarity": 45.0,
            "structural_stability": 38.0,
        }
        payload["explanations"] = build_explanations("gate_fail", gate_reasons=payload["analysis"]["gate_reasons"])
    else:
        payload["explanations"] = build_explanations(status)
    return payload
