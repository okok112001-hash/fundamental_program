"""
Tests for explanation engine (HANDOVER 15번 품질 보강: 설명 고도화 및 component 결과 반영).
"""
from __future__ import annotations

import pytest

from app.services.explanations import build_axis_text_from_components, build_explanations


# --- component 결과 반영: 템플릿별 한글 라벨이 axis 문장에 반영되는지 ---


def test_axis_text_bank_components_use_korean_labels():
    """Bank 템플릿 컴포넌트(capital_adequacy, asset_quality 등)는 한글 라벨로 설명에 반영된다."""
    comps = {"capital_adequacy": 78.0, "asset_quality": 65.0, "funding_liquidity": 70.0}
    text = build_axis_text_from_components(comps)
    assert text is not None
    # raw key가 그대로 노출되지 않고 한글 라벨이 포함되어야 함
    assert "capital_adequacy" not in text
    assert "asset_quality" not in text


def test_axis_text_reit_components_use_korean_labels():
    """Reit 템플릿 컴포넌트(affo_per_share, leverage_ltv 등)는 한글 라벨로 설명에 반영된다."""
    comps = {"affo_per_share": 72.0, "leverage_ltv": 58.0, "dividend_coverage": 65.0}
    text = build_axis_text_from_components(comps)
    assert text is not None
    assert "affo_per_share" not in text
    assert "leverage_ltv" not in text


def test_axis_text_saas_components_use_korean_labels():
    """Software_saas 템플릿 컴포넌트는 한글 라벨로 설명에 반영된다."""
    comps = {"growth_efficiency": 68.0, "unit_economics": 62.0, "financial_resilience": 70.0}
    text = build_axis_text_from_components(comps)
    assert text is not None
    assert "growth_efficiency" not in text
    assert "unit_economics" not in text


def test_axis_text_cyclical_components_use_korean_labels():
    """Cyclical_company 템플릿 컴포넌트는 한글 라벨로 설명에 반영된다."""
    comps = {"normalized_earning_power": 65.0, "downcycle_survivability": 60.0, "capex_discipline": 58.0}
    text = build_axis_text_from_components(comps)
    assert text is not None
    assert "normalized_earning_power" not in text
    assert "downcycle_survivability" not in text


# --- build_explanations analyzed: subscores에 따라 axis 문장이 채워지는지 ---


def test_build_explanations_analyzed_with_bank_subscores_returns_axis_with_korean():
    """analyzed + bank subscores 시 axis 설명에 한글이 포함된다 (component 결과 반영)."""
    subscores = {
        "axis_1": {"normalized_earning_power": 70.0, "spread_quality": 65.0, "operating_efficiency": 62.0, "fee_diversification": 58.0},
        "axis_2": {"capital_adequacy": 75.0, "asset_quality": 72.0, "funding_liquidity": 70.0, "regulation_governance": 60.0},
        "axis_3": {"pb_vs_roe": 57.0, "dividend_sustainability": 65.0, "relative_valuation": 59.0},
    }
    score_display = {"axis_1": 6.8, "axis_2": 6.9, "axis_3": 6.0, "total": 6.6}
    out = build_explanations("analyzed", subscores=subscores, score_display=score_display)
    assert out["axis_1"] is not None
    assert out["axis_2"] is not None
    assert out["axis_3"] is not None
    assert out["summary"]
    # bank 컴포넌트 raw key가 설명에 그대로 나오면 안 됨
    assert "capital_adequacy" not in (out["axis_2"] or "")
    assert "normalized_earning_power" not in (out["axis_1"] or "")


def test_build_explanations_analyzed_summary_reflects_score_display():
    """summary는 score_display 구간에 따라 다른 문구로 반영된다 (고도화)."""
    subscores = {"axis_1": {"growth_quality": 70.0}, "axis_2": {"competitive_durability": 60.0}, "axis_3": {"relative_valuation": 40.0}}
    # a1 >= 7, a3 < 5 → 가격 부담
    out_high_low = build_explanations("analyzed", subscores=subscores, score_display={"axis_1": 7.2, "axis_2": 6.0, "axis_3": 4.5, "total": 5.9})
    assert "가격" in (out_high_low["summary"] or "")
    # a2 < 5 → 보수적 해석
    out_low_a2 = build_explanations("analyzed", subscores=subscores, score_display={"axis_1": 5.0, "axis_2": 4.5, "axis_3": 5.0, "total": 4.8})
    assert "보수" in (out_low_a2["summary"] or "")


def test_build_explanations_gate_fail_includes_reasons_in_summary():
    """gate_fail 시 summary에 gate_reasons가 반영된다."""
    out = build_explanations("gate_fail", gate_reasons=["model_insufficient_data", "required_axis_coverage_insufficient"])
    assert out["summary"] is not None
    assert "model_insufficient_data" in out["summary"] or "분석이 중단" in out["summary"]
    assert out["axis_1"] is None
    assert out["axis_2"] is None
    assert out["axis_3"] is None
