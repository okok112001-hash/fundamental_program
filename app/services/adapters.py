from __future__ import annotations

from typing import Any, Dict

from app.core.standard_input import normalize_external_payload, StandardizedInput


def _bounded(v: float) -> float:
    return max(0.0, min(100.0, float(v)))


def _mk_metrics_from_financials(payload: Dict[str, Any]) -> Dict[str, float]:
    m: Dict[str, float] = {}
    fin = payload.get("financials", {})
    market = payload.get("market", {})
    rev = fin.get("revenue_ttm")
    gp = fin.get("gross_profit_ttm")
    op = fin.get("operating_income_ttm")
    cfo = fin.get("cfo_ttm")
    ni = fin.get("net_income_ttm")
    equity = fin.get("equity_latest")
    assets = fin.get("assets_latest")
    shares = market.get("diluted_shares_outstanding") or market.get("shares_outstanding")
    price = market.get("price")
    market_cap = market.get("market_cap")
    if rev and shares:
        m["growth_quality"] = 70.0
    if rev and gp:
        m["margin_quality"] = _bounded(gp / rev * 100.0)
    if rev and op:
        m["margin_quality"] = _bounded(op / rev * 100.0)
    if equity and op:
        m["capital_efficiency"] = _bounded(op / equity * 100.0)
    if ni and cfo:
        ratio = cfo / ni if ni else 0
        m["cash_conversion"] = _bounded(ratio * 50.0)
    if market_cap and op:
        m["absolute_value"] = 60.0
        m["relative_valuation"] = 55.0
        m["implied_expectation"] = 50.0
    # durability proxies
    if rev and op:
        m["competitive_durability"] = 65.0
        m["management_capital_allocation"] = 60.0
        m["financial_resilience"] = 62.0
        m["business_external_risk"] = 55.0
    return m


def _mk_bank_metrics(payload: Dict[str, Any]) -> Dict[str, float]:
    b = payload.get("derived", {}).get("raw_bank_metrics", {})
    out: Dict[str, float] = {}
    if b.get("cet1") is not None:
        out["capital_adequacy"] = _bounded(float(b["cet1"]) * 6)
    if b.get("npl_ratio") is not None:
        out["asset_quality"] = _bounded(100 - float(b["npl_ratio"]) * 10)
    if b.get("nim") is not None:
        out["spread_quality"] = _bounded(float(b["nim"]) * 20)
    if b.get("cost_to_income") is not None:
        out["operating_efficiency"] = _bounded(100 - float(b["cost_to_income"]))
    if b.get("fee_income_mix") is not None:
        out["fee_diversification"] = _bounded(float(b["fee_income_mix"]))
    if b.get("ldr") is not None:
        out["funding_liquidity"] = _bounded(100 - abs(float(b["ldr"]) - 80))
    if out:
        out.setdefault("regulation_governance", 60.0)
        out.setdefault("pb_vs_roe", 55.0)
        out.setdefault("dividend_sustainability", 60.0)
        out.setdefault("relative_valuation", 58.0)
        out.setdefault("normalized_earning_power", 65.0)
    return out


def _mk_reit_metrics(payload: Dict[str, Any]) -> Dict[str, float]:
    r = payload.get("derived", {}).get("raw_reit_metrics", {})
    out: Dict[str, float] = {}
    if r.get("affo_per_share") is not None:
        out["affo_per_share"] = _bounded(float(r["affo_per_share"]) * 10)
    if r.get("ltv") is not None:
        out["leverage_ltv"] = _bounded(100 - float(r["ltv"]))
    if r.get("dscr") is not None:
        out["interest_coverage_refinancing"] = _bounded(float(r["dscr"]) * 25)
    if r.get("nav_discount") is not None:
        out["nav_discount_premium"] = _bounded(50 + float(r["nav_discount"]))
    if out:
        out.setdefault("noi_growth", 60.0)
        out.setdefault("dividend_coverage", 62.0)
        out.setdefault("occupancy_rent_trend", 63.0)
        out.setdefault("tenant_asset_diversification", 61.0)
        out.setdefault("lease_quality_wale", 64.0)
        out.setdefault("maintenance_capex_burden", 58.0)
        out.setdefault("p_affo", 56.0)
        out.setdefault("yield_spread_caprate_value", 57.0)
    return out


def from_sec_companyfacts(payload: Dict[str, Any]) -> StandardizedInput:
    metrics = _mk_metrics_from_financials(payload)
    metrics.update(_mk_bank_metrics(payload))
    metrics.update(_mk_reit_metrics(payload))
    source_map = {k: "sec_companyfacts" for k in metrics}
    availability = {k: "observed" for k in metrics}
    normalized = {
        "security": payload.get("security", {}),
        "classification": payload.get("classification", {}),
        "market": payload.get("market", {}),
        "financials": payload.get("financials", {}),
        "derived": {"metrics": metrics, "availability": availability, "source_map": source_map},
        "metadata": payload.get("metadata", {}),
    }
    return normalize_external_payload(normalized)


def from_opendart(payload: Dict[str, Any]) -> StandardizedInput:
    return from_sec_companyfacts(payload)


def from_polygon(payload: Dict[str, Any]) -> StandardizedInput:
    normalized = {
        "security": payload.get("security", {}),
        "classification": payload.get("classification", {}),
        "market": payload.get("market", {}),
        "financials": payload.get("financials", {}),
        "derived": payload.get("derived", {"metrics": {}, "availability": {}, "source_map": {}}),
        "metadata": payload.get("metadata", {}),
    }
    return normalize_external_payload(normalized)


def adapt_provider(provider: str, payload: Dict[str, Any]) -> StandardizedInput:
    if provider == "sec_companyfacts":
        return from_sec_companyfacts(payload)
    if provider == "opendart":
        return from_opendart(payload)
    if provider == "polygon":
        return from_polygon(payload)
    raise ValueError(f"unsupported_provider: {provider}")
