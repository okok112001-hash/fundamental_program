from __future__ import annotations

from typing import Dict, Optional

# 한글 라벨: template_metric_map 컴포넌트별 설명 문구용 (HANDOVER 15번 품질 보강)
LABELS = {
    # general_operating_company
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
    # bank
    "normalized_earning_power": "정규화 수익력",
    "spread_quality": "스프레드 품질",
    "operating_efficiency": "운영 효율",
    "fee_diversification": "수수료 다각화",
    "capital_adequacy": "자본건전성",
    "asset_quality": "자산건전성",
    "funding_liquidity": "자금 유동성",
    "regulation_governance": "규제·거버넌스",
    "pb_vs_roe": "P/B 대비 ROE",
    "dividend_sustainability": "배당 지속가능성",
    # reit_income_asset
    "affo_per_share": "주당 AFFO",
    "noi_growth": "NOI 성장",
    "dividend_coverage": "배당 커버리지",
    "occupancy_rent_trend": "입주율·임대 추이",
    "leverage_ltv": "LTV 레버리지",
    "interest_coverage_refinancing": "이자·재융자 커버리지",
    "tenant_asset_diversification": "임차인·자산 다각화",
    "lease_quality_wale": "리스 품질·WALE",
    "maintenance_capex_burden": "유지·설비 부담",
    "p_affo": "P/AFFO",
    "nav_discount_premium": "NAV 할인·프리미엄",
    "yield_spread_caprate_value": "수익률 스프레드·캡레이트",
    # software_saas
    "growth_efficiency": "성장 효율",
    "gross_profit_cash_quality": "매출총이익·현금 품질",
    "unit_economics": "단위 경제성",
    "diluted_per_share_growth": "주당 성장",
    "recurring_revenue_retention_moat_proxy": "반복매출·리텐션·해자",
    "capital_allocation_sbc_control": "자본배분·SBC 관리",
    "customer_product_concentration": "고객·제품 집중",
    "absolute_value_support": "절대가치 근거",
    # cyclical_company
    "cost_position_asset_efficiency": "원가 포지션·자산 효율",
    "midcycle_cash_generation": "중기 현금 창출",
    "downcycle_survivability": "하락국면 생존력",
    "capex_discipline": "설비투자 규율",
    "commodity_cycle_risk": "원자재 사이클 리스크",
    "normalized_valuation": "정규화 밸류에이션",
    "balance_sheet_floor_value": "재무 안전마진",
    "cycle_expectation_reflection": "사이클 기대 반영",
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
