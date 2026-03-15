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


def test_provider_analysis_saas_analyzed():
    """연결 강화: adapter가 software_saas 메트릭을 채우면 pipeline→scoring으로 주입되어 analyzed + 점수 반환."""
    payload = {
        "security": {"ticker": "CRM", "name": "Salesforce", "asset_class": "equity", "price_currency": "USD", "reporting_currency": "USD"},
        "classification": {"is_software_saas": True},
        "market": {"price": 280.0, "market_cap": 280_000_000_000, "shares_outstanding": 1_000_000_000},
        "financials": {
            "revenue_ttm": 34_000_000_000,
            "gross_profit_ttm": 24_000_000_000,
            "operating_income_ttm": 5_000_000_000,
            "cfo_ttm": 10_000_000_000,
            "net_income_ttm": 4_000_000_000,
            "equity_latest": 58_000_000_000,
        },
        "metadata": {},
    }
    r = client.post("/analysis/provider/sec_companyfacts", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["classification"]["template_id"] == "software_saas"
    assert data["analysis"]["status"] == "analyzed"
    assert data["scores"]["display"] is not None
    assert data["scores"]["display"]["axis_1"] is not None


def test_provider_analysis_cyclical_analyzed():
    """연결 강화: adapter가 cyclical_company 메트릭을 채우면 pipeline→scoring으로 주입되어 analyzed + 점수 반환."""
    payload = {
        "security": {"ticker": "CAT", "name": "Caterpillar", "asset_class": "equity", "price_currency": "USD", "reporting_currency": "USD"},
        "classification": {"is_cyclical_company": True},
        "market": {"price": 380.0, "market_cap": 190_000_000_000, "shares_outstanding": 500_000_000},
        "financials": {
            "revenue_ttm": 67_000_000_000,
            "operating_income_ttm": 10_000_000_000,
            "cfo_ttm": 12_000_000_000,
            "net_income_ttm": 10_000_000_000,
            "equity_latest": 19_000_000_000,
        },
        "metadata": {},
    }
    r = client.post("/analysis/provider/sec_companyfacts", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["classification"]["template_id"] == "cyclical_company"
    assert data["analysis"]["status"] == "analyzed"
    assert data["scores"]["display"] is not None
    assert data["scores"]["display"]["axis_1"] is not None


def test_provider_unsupported_provider():
    r = client.post('/analysis/provider/unknown', json={})
    assert r.status_code == 400


# --- 테스트 확대: provider 입력 기반 gate_fail 케이스 (HANDOVER 15번 5번) ---


def test_provider_gate_fail_required_axis_coverage_insufficient():
    """Provider payload에 필수 데이터가 없으면 required_axis_coverage_insufficient로 gate_fail."""
    payload = {
        "security": {"ticker": "X", "name": "Unknown", "asset_class": "equity", "price_currency": "USD", "reporting_currency": "USD"},
        "classification": {},
        "market": {"price": 10.0},
        "financials": {},
        "metadata": {},
    }
    r = client.post("/analysis/provider/sec_companyfacts", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["analysis"]["status"] == "gate_fail"
    assert data["analysis"]["gate_stage"] == "universal_gate"
    assert "required_axis_coverage_insufficient" in data["analysis"]["gate_reasons"]
    assert data["scores"]["raw"] is None
    assert data["scores"]["display"] is None


def test_provider_gate_fail_template_mismatch():
    """classification.template_mismatch 시 template_mismatch로 gate_fail."""
    payload = {
        "security": {"ticker": "Y", "name": "Y", "asset_class": "equity", "price_currency": "USD", "reporting_currency": "USD"},
        "classification": {"template_mismatch": True},
        "market": {"price": 50.0, "market_cap": 1_000_000_000, "shares_outstanding": 20_000_000},
        "financials": {"revenue_ttm": 100_000_000, "operating_income_ttm": 10_000_000},
        "metadata": {},
    }
    r = client.post("/analysis/provider/sec_companyfacts", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["analysis"]["status"] == "gate_fail"
    assert "template_mismatch" in data["analysis"]["gate_reasons"]
    assert data["scores"]["raw"] is None
    assert data["scores"]["display"] is None


def test_provider_gate_fail_contract_scores_null():
    """gate_fail 시 CONTRACT: scores.raw/display null, confidence는 조건부."""
    payload = {
        "security": {"ticker": "Z", "name": "Z", "asset_class": "equity", "price_currency": "USD", "reporting_currency": "USD"},
        "classification": {},
        "market": {},
        "financials": {},
        "metadata": {},
    }
    r = client.post("/analysis/provider/sec_companyfacts", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["analysis"]["status"] == "gate_fail"
    assert data["scores"]["raw"] is None
    assert data["scores"]["display"] is None
    if data["analysis"].get("confidence_score") is not None:
        assert data["meta"].get("confidence_breakdown") is not None


# --- 테스트 확대: provider 입력 기반 analyzed 케이스 (opendart 등) ---


def test_provider_opendart_general_analyzed():
    """opendart provider로 일반 기업 payload 시 analyzed + 점수 반환."""
    payload = {
        "security": {"ticker": "005930", "name": "Samsung", "asset_class": "equity", "price_currency": "KRW", "reporting_currency": "KRW"},
        "classification": {},
        "market": {"price": 70000.0, "market_cap": 400_000_000_000_000, "shares_outstanding": 5_000_000_000},
        "financials": {
            "revenue_ttm": 250_000_000_000_000,
            "gross_profit_ttm": 80_000_000_000_000,
            "operating_income_ttm": 40_000_000_000_000,
            "cfo_ttm": 35_000_000_000_000,
            "net_income_ttm": 30_000_000_000_000,
            "equity_latest": 200_000_000_000_000,
            "assets_latest": 400_000_000_000_000,
        },
        "metadata": {},
    }
    r = client.post("/analysis/provider/opendart", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["classification"]["template_id"] == "general_operating_company"
    assert data["analysis"]["status"] == "analyzed"
    assert data["scores"]["display"] is not None
    assert data["scores"]["display"]["axis_1"] is not None
    assert data["meta"]["confidence_breakdown"] is not None
