# 기본적 분석 프로그램 인수인계 문서 (V1.4 최신)

## 1. 이 문서의 목적
이 문서는 **다른 AI가 이 프로젝트를 그대로 이어받아 구현을 계속할 수 있도록** 작성된 인수인계 문서입니다.

이 문서를 사용하는 AI는 아래 원칙을 지켜야 합니다.
- 설계를 새로 뒤집지 말 것
- 현재 코드 작업본을 먼저 확인할 것
- 테스트를 먼저 실행해 현재 상태를 파악할 것
- 이미 합의된 상태/null/contract 규칙을 절대 깨지 말 것
- V1.x 범위를 불필요하게 확장하지 말 것

---

## 2. 프로젝트 목적
이 프로젝트는 **기업형 상장 종목용 기본적 분석 프로그램**을 만드는 것입니다.

사용자가 종목명 또는 티커를 검색하면 아래 결과를 봅니다.
- 수익력
- 지속력
- 가격매력
- 최종점수
- 분석 신뢰도
- 상태(analyzed / gate_fail / special_case_excluded / unsupported_asset)
- 탈락 사유 또는 제외 사유
- 요약 설명
- 경고 플래그

현재 범위:
- 지원: 기업형 상장 종목
- 제외: ETF, 채권, 암호자산, 적자 바이오/이벤트형 고위험 종목

---

## 3. 핵심 설계 원칙
1. 공통 UI, 템플릿별 내부 계산식
2. Gate가 점수보다 우선
3. Hard Gate / Critical Flag / 일반 경고 구분
4. 서로 다른 템플릿 간 점수 직접 비교 금지
5. status에 따라 점수/null 정책 엄격 적용
6. confidence는 점수와 분리
7. flat flags 유지
8. 템플릿 내부 state/subtype 허용
9. 직접 지표가 어려운 경우 proxy fallback 허용
10. excluded / unsupported는 일반 gate_fail과 중복되지 않음

---

## 4. 상태값과 핵심 출력 규칙

### 상태값
- `analyzed`
- `gate_fail`
- `special_case_excluded`
- `unsupported_asset`

### gate_stage
- `all_passed`
- `universal_gate`
- `template_specific_gate`
- `universal_exclusion`
- `unsupported_scope`

### 출력 계약
- `analyzed` → 점수 표시 가능
- `gate_fail` → 사업 점수 null, confidence는 조건부 nullable
- `special_case_excluded` → 사업 점수 null, confidence null
- `unsupported_asset` → 사업 점수 null, confidence null

### confidence 동기화 규칙
- `analysis.confidence_score == null` 이면 `meta.confidence_breakdown == null`
- `analysis.confidence_score != null` 이면 `meta.confidence_breakdown != null`

### code 형식
- `routing_reason`, `gate_reasons`, `flags`는 machine-readable `snake_case` code만 허용

---

## 5. 템플릿 목록

### 점수화 템플릿 (11개)
1. `general_operating_company`
2. `cyclical_company`
3. `commodity_energy_producer`
4. `software_saas`
5. `digital_platform_marketplace`
6. `regulated_utility_infrastructure`
7. `bank`
8. `insurance`
9. `brokerage_asset_manager`
10. `reit_income_asset`
11. `holding_company`

### 비점수화 상태 템플릿
12. `special_case_excluded_preprofit_biotech_eventdriven`
13. `unsupported_non_corporate_asset`

---

## 6. 라우팅 핵심 원칙

### 기본 흐름
- preliminary routing
- data collection / normalization
- routing validation / reroute
- universal gate
- template-specific gate
- score
- explanation

### 금융 브랜치 진입
- 단순 금융 라이선스 보유만으로는 금융 브랜치에 들어가지 않음
- 반드시 **enterprise materiality**를 먼저 통과해야 함
- captive finance / minor payment license는 보통 일반 템플릿에 남음

### mixed 금융그룹
- scoring template: 지배적 규제 사업 기준
- gate coverage: material한 금융 자회사 전체 반영

---

## 7. Gate 구조

### Universal Gate
- 필수 데이터 부족
- critical metric + proxy 모두 없음
- FX 정렬 실패
- 중대한 회계 품질 이상
- 중대한 공시 문제
- `model_incompatible / template_mismatch`
- `required_axis_coverage_insufficient`
- `model_insufficient_data`

### Template-specific Gate
템플릿별 생존성/건전성/구조 리스크

### Critical Flag
- material_regulatory_litigation_risk
- contingent_liability_risk
- controlling_shareholder_risk
- low_free_float_marketability_risk
- customer_concentration
- country_regulatory_concentration
- refinancing_risk
- share_count_uptrend
- event_dependency
- accounting_adjustment_heavy

---

## 8. 점수 구조

4단계:
1. metric
2. component
3. axis
4. total

### metric 기본
- Level 40
- Trend 35
- Stability 25

### 차원 부족
- 2차원: 재정규화
- 1차원: 재정규화 + neutral shrinkage + confidence penalty

### coverage 규칙
- 특정 axis의 유효 component coverage가 너무 낮으면
  - 억지 재정규화하지 않고
  - `required_axis_coverage_insufficient` 또는 `model_insufficient_data`
  - 로 gate 가능

### critical metric 규칙
- direct 없음 + approved proxy 없음 → 기본적으로 Universal Gate

---

## 9. 내부 표준 입력 객체(Standardized Input)
모든 외부 데이터는 먼저 표준 입력 객체로 변환됩니다.

구조:
- `security`
- `classification`
- `market`
- `financials`
- `derived`
- `metadata`

metric availability 상태:
- `observed`
- `proxy_used`
- `structurally_not_applicable`
- `missing`

---

## 10. FX / 통화 처리
사용 필드:
- `price_currency`
- `reporting_currency`
- `valuation_currency`
- `fx_rate_applied`
- `fx_rate_timestamp`
- `fx_source`
- `fx_normalization_method`

원칙:
- 통화가 다르면 valuation currency 기준으로 정규화
- 실패 시 Universal Gate
- 시계열 monetary metric은 일관된 FX method로만 계산

---

## 11. 현재 코드 구조 요약

### 루트
- `README.md`

### docs
- docs/BUILD_BACKLOG.md
- docs/CONTRACT_INVARIANTS.md
- docs/DATA_SOURCE_PLAN.md
- docs/EXECUTION_PLAN.md
- docs/HUMAN_ACTIONS_ONLY.md
- docs/PUBLIC_INTERNAL_SCHEMA.md

### app/api
- app/api/__init__.py
- app/api/main.py
- app/api/schemas.py

### app/core
- app/core/__init__.py
- app/core/analysis_pipeline.py
- app/core/demo_engine.py
- app/core/gates.py
- app/core/loaders.py
- app/core/quality.py
- app/core/router.py
- app/core/routing_validation.py
- app/core/score_rules.py
- app/core/scoring_engine.py
- app/core/standard_input.py

### app/config
- app/config/flag_codes.json
- app/config/gate_reason_codes.json
- app/config/status_contract.json
- app/config/template_metric_map.json
- app/config/template_registry.json

### app/services
- app/services/__init__.py
- app/services/adapters.py
- app/services/explanations.py

### data
- data/critical_metric_matrix.csv
- data/golden_set.csv

### tests
- tests/conftest.py
- tests/test_contracts.py
- tests/test_demo_api.py
- tests/test_golden_set.py
- tests/test_provider_api.py
- tests/test_routing.py
- tests/test_routing_validation.py
- tests/test_schema_invariants.py
- tests/test_score_rules.py
- tests/test_scoring_engine.py
- tests/test_template_metric_map.py

---

## 12. 절대 깨면 안 되는 것
- `status != analyzed`일 때 점수 노출 금지
- `special_case_excluded / unsupported_asset`에서 confidence null
- `confidence_score ↔ confidence_breakdown` 동기화
- 금융 브랜치 진입 전 enterprise materiality
- mixed 금융그룹의 scoring vs gate 분리
- critical metric + proxy rule
- minimum_effective_component_coverage
- flat flags 유지
- 템플릿 간 직접 점수 비교 금지

---

## 13. 개발 환경 정보
- Python 3.1x (가상환경 venv 사용)
- 주요 프레임워크: FastAPI, Pytest
- Git 관리: 로컬 개발 시 항상 커밋 단위로 변경 사항 확인

---

## 14. 품질 관리 원칙
- 모든 코드는 pytest를 통해 검증한다.
- 개발 및 수정 전후로 테스트를 실행하여 기준선을 유지한다.
- 의존성(라이브러리) 관리를 철저히 하여, 언제 어디서든 동일한 테스트 결과가 재현되도록 한다.

---

## 15. 향후 로드맵 (진행 예정 작업)
이 목록은 프로젝트의 핵심 마일스톤입니다. AI는 작업 시작 전 항상 이 목록을 확인하고, 현재 완료된 항목을 제외한 최우선 과제를 스스로 선정하여 작업하십시오.

1. **provider adapter 확장**: 실제 데이터 필드를 metrics에 매핑 (`metrics / availability / source_map` 채우기)
2. **연결 강화**: adapter 데이터를 scoring engine에 주입 (`general / bank / reit / saas / cyclical` 우선)
3. **품질 보강**: 설명(explanation) 엔진 로직 고도화 및 component 결과 반영
4. **UI/API 마감**: 사용자 화면 및 API 최종 정리
5. **테스트 확대**: provider 입력 기반 `analyzed / gate_fail` 케이스 확장