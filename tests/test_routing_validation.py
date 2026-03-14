from app.core.routing_validation import validate_routing


def test_reroute_financial_non_material():
    result = validate_routing("brokerage_asset_manager", {"financial_materiality": False})
    assert result.action == "rerouted"
    assert result.final_template_id == "general_operating_company"
