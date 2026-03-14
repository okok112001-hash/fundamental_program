from app.core.scoring_engine import metric_from_dims, component_score, score_template


def test_metric_from_one_dim_uses_shrinkage():
    assert round(metric_from_dims(level=100), 1) == 85.0


def test_component_score_ignores_none():
    assert component_score([70, None, 50]) == 60


def test_score_template_general():
    subscores = {
        "axis_1": {"growth_quality": 74.0, "margin_quality": 79.0, "capital_efficiency": 70.0, "cash_conversion": 65.0},
        "axis_2": {"competitive_durability": 72.0, "management_capital_allocation": 63.0, "financial_resilience": 78.0, "business_external_risk": 58.0},
        "axis_3": {"relative_valuation": 61.0, "absolute_value": 69.0, "implied_expectation": 54.0},
    }
    result = score_template("general_operating_company", subscores)
    assert result["scores"]["display"]["axis_1"] == 7.2
    assert result["scores"]["raw"]["total"] == 67.8


def test_score_template_coverage_gate():
    subscores = {"axis_1": {"growth_quality": 70.0}, "axis_2": {}, "axis_3": {}}
    result = score_template("general_operating_company", subscores)
    assert result["scores"] is None
    assert result["gate_reason"] == "required_axis_coverage_insufficient"
