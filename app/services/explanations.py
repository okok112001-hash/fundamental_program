from __future__ import annotations

from typing import Dict, Optional

LABELS = {
    "growth_quality": "성장",
    "margin_quality": "마진",
    "capital_efficiency": "자본효율",
    "cash_conversion": "현금전환",
    "competitive_durability": "경쟁력 지속성",
    "management_capital_allocation": "자본배분",
    "financial_resilience": "재무안정성",
    "business_external_risk": "사업 리스크",
    "relative_valuation": "상대가치",
    "absolute_value": "절대가치",
    "implied_expectation": "내재 기대치",
}


def build_axis_text_from_components(component_scores: Dict[str, float]) -> Optional[str]:
    if not component_scores:
        return None
    best_key = max(component_scores, key=component_scores.get)
    worst_key = min(component_scores, key=component_scores.get)
    best = LABELS.get(best_key, best_key)
    worst = LABELS.get(worst_key, worst_key)
    return f"{best}은 상대적으로 양호하지만 {worst}은 보완이 필요합니다."


def build_explanations(status: str, subscores: Optional[Dict[str, Dict[str, float]]] = None, gate_reasons: Optional[list[str]] = None, score_display: Optional[Dict[str, float]] = None) -> Dict[str, Optional[str]]:
    if status == "gate_fail":
        reason = ", ".join((gate_reasons or [])[:2]) if gate_reasons else "분석 적합성 부족"
        return {"axis_1": None, "axis_2": None, "axis_3": None, "summary": f"현재 기준으로 분석이 중단되었습니다. 주요 사유: {reason}."}
    if status == "special_case_excluded":
        return {"axis_1": None, "axis_2": None, "axis_3": None, "summary": "현재 버전의 일반 기본적 분석 모델 적용 대상이 아닙니다."}
    if status == "unsupported_asset":
        return {"axis_1": None, "axis_2": None, "axis_3": None, "summary": "현재 버전 지원 범위 밖의 자산입니다."}
    axis1 = build_axis_text_from_components((subscores or {}).get("axis_1", {}))
    axis2 = build_axis_text_from_components((subscores or {}).get("axis_2", {}))
    axis3 = build_axis_text_from_components((subscores or {}).get("axis_3", {}))
    summary = "수익력, 지속력, 가격의 균형이 비교적 양호합니다."
    if score_display:
        a1 = score_display.get("axis_1", 0)
        a2 = score_display.get("axis_2", 0)
        a3 = score_display.get("axis_3", 0)
        if a1 >= 7 and a3 < 5:
            summary = "사업의 질은 양호하지만 가격 부담이 존재합니다."
        elif a1 >= 7 and a2 < 5:
            summary = "수익력은 좋지만 지속 가능성 확인이 필요합니다."
        elif a2 < 5:
            summary = "보수적인 해석이 필요한 종목입니다."
    return {"axis_1": axis1, "axis_2": axis2, "axis_3": axis3, "summary": summary}
