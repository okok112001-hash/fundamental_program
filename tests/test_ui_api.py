"""
Tests for UI/API 마감 (HANDOVER 15번 4번: 사용자 화면 및 API 최종 정리).
"""
from __future__ import annotations

import re

from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


def test_ui_html_valid_closing_tag():
    """HTML이 올바른 종료 태그를 가진다 (</html>)."""
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")
    html = r.text
    assert "</html>" in html
    assert "</nhtml>" not in html


def test_ui_html_includes_user_facing_labels():
    """HANDOVER §2: 사용자가 보는 항목(수익력, 지속력, 가격매력, 최종점수, 분석 신뢰도, 상태)이 UI에 포함된다."""
    r = client.get("/")
    assert r.status_code == 200
    html = r.text
    labels = ("수익력", "지속력", "가격매력", "최종점수", "분석 신뢰도", "상태")
    for label in labels:
        assert label in html, f"UI should expose label: {label}"


def test_ui_html_includes_summary_and_flags_section():
    """요약 설명, 경고 플래그(또는 탈락 사유) 표시를 위한 구조가 있다."""
    r = client.get("/")
    assert r.status_code == 200
    html = r.text
    assert "요약" in html or "summary" in html.lower()
    assert "경고" in html or "플래그" in html or "flags" in html.lower() or "사유" in html


def test_api_version_stable():
    """API 버전이 마감용으로 v1.4를 노출한다 (문서/앱 버전)."""
    r = client.get("/openapi.json")
    assert r.status_code == 200
    data = r.json()
    assert "v1.4" in data.get("info", {}).get("version", "")


def test_ui_route_returns_same_structure_as_root():
    """GET /ui 는 GET / 와 동일한 UI 구조를 반환한다."""
    r_root = client.get("/")
    r_ui = client.get("/ui")
    assert r_root.status_code == 200
    assert r_ui.status_code == 200
    assert "기본적 분석 프로그램" in r_ui.text
    assert "수익력" in r_ui.text
