"""
Unit tests for provider adapters (app.services.adapters).
HANDOVER §9 Standardized Input, DATA_SOURCE_PLAN metadata, and adapter contract.
"""
from __future__ import annotations

import pytest

from app.core.standard_input import StandardizedInput
from app.services.adapters import (
    adapt_provider,
    from_opendart,
    from_polygon,
    from_sec_companyfacts,
)

# Allowed metric availability values (HANDOVER §9)
AVAILABILITY_VALUES = frozenset({"observed", "proxy_used", "structurally_not_applicable", "missing"})


def _minimal_payload():
    return {
        "security": {"ticker": "T", "name": "Test", "asset_class": "equity", "price_currency": "USD", "reporting_currency": "USD"},
        "classification": {},
        "market": {"price": 20.0, "market_cap": 100_000_000},
        "financials": {},
        "metadata": {},
    }


# --- StandardizedInput shape (HANDOVER §9) ---


def test_standardized_input_has_all_six_sections():
    """StandardizedInput must have security, classification, market, financials, derived, metadata."""
    payload = _minimal_payload()
    out = from_sec_companyfacts(payload)
    assert isinstance(out, StandardizedInput)
    assert hasattr(out, "security") and isinstance(out.security, dict)
    assert hasattr(out, "classification") and isinstance(out.classification, dict)
    assert hasattr(out, "market") and isinstance(out.market, dict)
    assert hasattr(out, "financials") and isinstance(out.financials, dict)
    assert hasattr(out, "derived") and isinstance(out.derived, dict)
    assert hasattr(out, "metadata") and isinstance(out.metadata, dict)


def test_derived_has_metrics_availability_source_map():
    """derived must contain metrics, availability, source_map for downstream gate/score."""
    payload = _minimal_payload()
    payload["financials"] = {"revenue_ttm": 1000, "operating_income_ttm": 200}
    out = from_sec_companyfacts(payload)
    assert "metrics" in out.derived
    assert "availability" in out.derived
    assert "source_map" in out.derived
    assert isinstance(out.derived["metrics"], dict)
    assert isinstance(out.derived["availability"], dict)
    assert isinstance(out.derived["source_map"], dict)


def test_availability_values_only_allowed_codes():
    """Every value in derived.availability must be one of HANDOVER §9 allowed codes."""
    payload = _minimal_payload()
    payload["financials"] = {"revenue_ttm": 1000, "gross_profit_ttm": 400}
    out = from_sec_companyfacts(payload)
    for k, v in out.derived.get("availability", {}).items():
        assert v in AVAILABILITY_VALUES, f"availability['{k}'] = {v!r} not in {AVAILABILITY_VALUES}"


# --- Metadata: provider (DATA_SOURCE_PLAN) ---


def test_metadata_provider_sec_companyfacts():
    """metadata.provider must be set to provider name for sec_companyfacts."""
    out = from_sec_companyfacts(_minimal_payload())
    assert out.metadata.get("provider") == "sec_companyfacts"


def test_metadata_provider_opendart():
    """metadata.provider must be set for opendart."""
    out = from_opendart(_minimal_payload())
    assert out.metadata.get("provider") == "opendart"


def test_metadata_provider_polygon():
    """metadata.provider must be set for polygon."""
    out = from_polygon(_minimal_payload())
    assert out.metadata.get("provider") == "polygon"


# --- Metadata: currency from security (DATA_SOURCE_PLAN) ---


def test_metadata_currency_from_security_price_currency():
    """metadata.currency must be populated from security.price_currency when present."""
    payload = _minimal_payload()
    payload["security"]["price_currency"] = "USD"
    out = from_sec_companyfacts(payload)
    assert out.metadata.get("currency") == "USD"


def test_metadata_currency_fallback_reporting_currency():
    """metadata.currency can fallback to security.reporting_currency when price_currency missing."""
    payload = _minimal_payload()
    del payload["security"]["price_currency"]
    payload["security"]["reporting_currency"] = "KRW"
    out = from_sec_companyfacts(payload)
    assert out.metadata.get("currency") == "KRW"


# --- Metadata: retrieval_timestamp, filing_period, filing_date (DATA_SOURCE_PLAN) ---


def test_metadata_retrieval_timestamp_when_in_payload():
    """metadata.retrieval_timestamp must be set when payload has retrieval_timestamp at top level."""
    payload = _minimal_payload()
    payload["retrieval_timestamp"] = "2025-03-14T12:00:00Z"
    out = from_sec_companyfacts(payload)
    assert out.metadata.get("retrieval_timestamp") == "2025-03-14T12:00:00Z"


def test_metadata_filing_period_and_date_when_in_payload():
    """metadata must include filing_period and filing_date when present in payload."""
    payload = _minimal_payload()
    payload["filing_period"] = "FY2024"
    payload["filing_date"] = "2025-02-28"
    out = from_sec_companyfacts(payload)
    assert out.metadata.get("filing_period") == "FY2024"
    assert out.metadata.get("filing_date") == "2025-02-28"


# --- Metadata: FX fields (HANDOVER §10) ---


def test_metadata_fx_fields_from_security_when_present():
    """FX fields in security must flow into metadata for downstream normalization."""
    payload = _minimal_payload()
    payload["security"]["valuation_currency"] = "USD"
    payload["security"]["fx_rate_applied"] = 1.0
    payload["security"]["fx_normalization_method"] = "spot_end_of_period"
    out = from_sec_companyfacts(payload)
    assert out.metadata.get("valuation_currency") == "USD"
    assert out.metadata.get("fx_rate_applied") == 1.0
    assert out.metadata.get("fx_normalization_method") == "spot_end_of_period"


# --- adapt_provider dispatch and unsupported ---


def test_adapt_provider_sec_companyfacts():
    """adapt_provider('sec_companyfacts', payload) returns same shape as from_sec_companyfacts."""
    payload = _minimal_payload()
    out = adapt_provider("sec_companyfacts", payload)
    assert out.metadata.get("provider") == "sec_companyfacts"


def test_adapt_provider_opendart():
    """adapt_provider('opendart', payload) returns opendart metadata."""
    payload = _minimal_payload()
    out = adapt_provider("opendart", payload)
    assert out.metadata.get("provider") == "opendart"


def test_adapt_provider_polygon():
    """adapt_provider('polygon', payload) returns polygon metadata."""
    payload = _minimal_payload()
    out = adapt_provider("polygon", payload)
    assert out.metadata.get("provider") == "polygon"


def test_adapt_provider_unsupported_raises():
    """adapt_provider(unknown) must raise ValueError with unsupported_provider."""
    with pytest.raises(ValueError, match="unsupported_provider"):
        adapt_provider("unknown", _minimal_payload())


# --- Source map and metrics shape (adapter contract) ---


def test_sec_companyfacts_source_map_keys_match_metrics():
    """For sec_companyfacts, source_map and availability keys must match metrics keys."""
    payload = _minimal_payload()
    payload["financials"] = {"revenue_ttm": 1000, "operating_income_ttm": 100}
    out = from_sec_companyfacts(payload)
    m = out.derived["metrics"]
    s = out.derived["source_map"]
    a = out.derived["availability"]
    assert set(s.keys()) == set(m.keys())
    assert set(a.keys()) == set(m.keys())
    assert all(s[k] == "sec_companyfacts" for k in s)


def test_opendart_source_map_keys_match_metrics():
    """For opendart, source_map keys match metrics; source_map values are 'opendart'."""
    payload = _minimal_payload()
    payload["financials"] = {"revenue_ttm": 1000}
    out = from_opendart(payload)
    m = out.derived["metrics"]
    s = out.derived["source_map"]
    assert set(s.keys()) == set(m.keys())
    assert all(s[k] == "opendart" for k in s)
