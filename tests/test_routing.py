from app.core.router import RoutingContext, preliminary_route


def test_non_corporate_routes_to_unsupported():
    template, reasons, status, stage = preliminary_route(RoutingContext(is_non_corporate_asset=True))
    assert template == "unsupported_non_corporate_asset"
    assert status == "unsupported_asset"
    assert stage == "unsupported_scope"


def test_bank_materiality_route():
    template, reasons, status, stage = preliminary_route(RoutingContext(is_material_financial_group_or_license_holder=True, dominant_regulated_business="bank"))
    assert template == "bank"
    assert status is None
