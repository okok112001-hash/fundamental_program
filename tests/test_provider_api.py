from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)


def test_provider_analysis_general_analyzed():
    payload = {
        "security": {"ticker": "AAPL", "name": "Apple", "asset_class": "equity", "price_currency": "USD", "reporting_currency": "USD"},
        "classification": {},
        "market": {"price": 190.0, "market_cap": 3_000_000_000_000, "shares_outstanding": 15_000_000_000},
        "financials": {
            "revenue_ttm": 400_000_000_000,
            "gross_profit_ttm": 180_000_000_000,
            "operating_income_ttm": 120_000_000_000,
            "cfo_ttm": 110_000_000_000,
            "net_income_ttm": 100_000_000_000,
            "equity_latest": 70_000_000_000,
            "assets_latest": 350_000_000_000,
        },
        "metadata": {},
    }
    r = client.post('/analysis/provider/sec_companyfacts', json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data['analysis']['status'] == 'analyzed'
    assert data['scores']['display']['axis_1'] is not None
    assert data['meta']['confidence_breakdown'] is not None


def test_provider_analysis_bank_analyzed():
    payload = {
        "security": {"ticker": "JPM", "name": "JPM", "asset_class": "equity", "price_currency": "USD", "reporting_currency": "USD"},
        "classification": {"is_material_financial_group_or_license_holder": True, "dominant_regulated_business": "bank"},
        "market": {"price": 200.0, "market_cap": 500_000_000_000},
        "financials": {},
        "derived": {"raw_bank_metrics": {"cet1": 14.0, "npl_ratio": 1.2, "nim": 2.8, "cost_to_income": 55.0, "fee_income_mix": 35.0, "ldr": 78.0}},
        "metadata": {"data_completeness_raw": 90.0, "template_fit_certainty_raw": 88.0, "normalization_clarity_raw": 80.0, "structural_stability_raw": 82.0},
    }
    r = client.post('/analysis/provider/sec_companyfacts', json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data['classification']['template_id'] == 'bank'
    assert data['analysis']['status'] == 'analyzed'
    assert data['scores']['display']['axis_2'] is not None


def test_provider_analysis_reit_analyzed():
    payload = {
        "security": {"ticker": "O", "name": "Realty Income", "asset_class": "equity", "price_currency": "USD", "reporting_currency": "USD"},
        "classification": {"is_reit": True},
        "market": {"price": 55.0, "market_cap": 40_000_000_000},
        "financials": {},
        "derived": {"raw_reit_metrics": {"affo_per_share": 4.2, "ltv": 42.0, "dscr": 3.1, "nav_discount": 8.0}},
        "metadata": {"data_completeness_raw": 90.0, "template_fit_certainty_raw": 88.0, "normalization_clarity_raw": 80.0, "structural_stability_raw": 82.0},
    }
    r = client.post('/analysis/provider/sec_companyfacts', json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data['classification']['template_id'] == 'reit_income_asset'
    assert data['analysis']['status'] == 'analyzed'


def test_provider_unsupported_provider():
    r = client.post('/analysis/provider/unknown', json={})
    assert r.status_code == 400
