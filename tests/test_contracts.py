from app.api.schemas import AnalysisResponse, Security, Classification, Analysis, Scores, UILabels, Explanations, Meta


def test_schema_imports():
    resp = AnalysisResponse(
        security=Security(name="X", ticker="X", asset_class="equity"),
        classification=Classification(template_id="general_operating_company", template_label="일반 비금융 기업", compare_scope="동일 템플릿 내 비교 적합"),
        analysis=Analysis(status="gate_fail", gate_stage="universal_gate", gate_reasons=["model_insufficient_data"], confidence_score=None),
        ui_labels=UILabels(),
        scores=Scores(raw=None, display=None),
        subscores=None,
        flags=[],
        explanations=Explanations(summary="x"),
        meta=Meta(confidence_breakdown=None)
    )
    assert resp.analysis.status == "gate_fail"
