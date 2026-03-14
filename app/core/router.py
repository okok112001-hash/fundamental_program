from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class RoutingContext:
    is_non_corporate_asset: bool = False
    is_preprofit_biotech_or_event_driven: bool = False
    is_reit: bool = False
    is_material_financial_group_or_license_holder: bool = False
    dominant_regulated_business: Optional[str] = None
    is_non_financial_holding_company: bool = False
    is_regulated_utility_infrastructure: bool = False
    is_upstream_commodity_energy_producer: bool = False
    is_software_saas: bool = False
    is_digital_platform_marketplace: bool = False
    is_cyclical_company: bool = False


def preliminary_route(ctx: RoutingContext) -> tuple[str, list[str], Optional[str], Optional[str]]:
    """
    Returns:
        template_id,
        routing_reason,
        terminal_status,
        terminal_gate_stage
    """
    reasons = []

    if ctx.is_non_corporate_asset:
        return "unsupported_non_corporate_asset", ["non_corporate_asset"], "unsupported_asset", "unsupported_scope"

    if ctx.is_preprofit_biotech_or_event_driven:
        return "special_case_excluded_preprofit_biotech_eventdriven", ["preprofit_event_driven_biotech"], "special_case_excluded", "universal_exclusion"

    if ctx.is_reit:
        return "reit_income_asset", ["reit_legal_form"], None, None

    if ctx.is_material_financial_group_or_license_holder:
        reasons.append("material_financial_group")
        if ctx.dominant_regulated_business == "bank":
            reasons.append("dominant_regulated_business_bank")
            return "bank", reasons, None, None
        if ctx.dominant_regulated_business == "insurance":
            reasons.append("dominant_regulated_business_insurance")
            return "insurance", reasons, None, None
        if ctx.dominant_regulated_business == "brokerage_asset_manager":
            reasons.append("dominant_regulated_business_brokerage_asset_manager")
            return "brokerage_asset_manager", reasons, None, None
        reasons.append("mixed_financial_group")
        return "brokerage_asset_manager", reasons, None, None

    if ctx.is_non_financial_holding_company:
        return "holding_company", ["non_financial_holding_company"], None, None

    if ctx.is_regulated_utility_infrastructure:
        return "regulated_utility_infrastructure", ["regulated_utility_infrastructure"], None, None

    if ctx.is_upstream_commodity_energy_producer:
        return "commodity_energy_producer", ["upstream_commodity_energy_producer"], None, None

    if ctx.is_software_saas:
        return "software_saas", ["recurring_revenue_software"], None, None

    if ctx.is_digital_platform_marketplace:
        return "digital_platform_marketplace", ["digital_platform_marketplace"], None, None

    if ctx.is_cyclical_company:
        return "cyclical_company", ["cyclical_revenue_profile"], None, None

    return "general_operating_company", ["non_financial_operating_company"], None, None
