import pytest

from app.api.schemas import AnalysisResponse
from app.core.demo_engine import build_demo_response


def test_analyzed_contract():
    resp = AnalysisResponse(**build_demo_response("AAPL"))
    assert resp.analysis.status == "analyzed"
    assert resp.scores.raw is not None
    assert resp.analysis.confidence_score is not None


def test_excluded_contract():
    resp = AnalysisResponse(**build_demo_response("SANA"))
    assert resp.analysis.status == "special_case_excluded"
    assert resp.scores.raw is None
    assert resp.analysis.confidence_score is None
    assert resp.meta.confidence_breakdown is None


def test_unsupported_contract():
    resp = AnalysisResponse(**build_demo_response("SPY"))
    assert resp.analysis.status == "unsupported_asset"
    assert resp.analysis.confidence_score is None


def test_machine_code_validation():
    payload = build_demo_response("AAPL")
    payload["flags"] = ["Not Machine Code"]
    with pytest.raises(Exception):
        AnalysisResponse(**payload)
