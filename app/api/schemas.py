from __future__ import annotations

import re
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

Status = Literal["analyzed", "gate_fail", "special_case_excluded", "unsupported_asset"]
GateStage = Literal["all_passed", "universal_gate", "template_specific_gate", "universal_exclusion", "unsupported_scope"]
CODE_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")


class ConfidenceScore(BaseModel):
    raw: float
    display: float


class ScoreBlockRaw(BaseModel):
    axis_1: float
    axis_2: float
    axis_3: float
    total: float


class ScoreBlockDisplay(BaseModel):
    axis_1: float
    axis_2: float
    axis_3: float
    total: float


class Scores(BaseModel):
    raw: Optional[ScoreBlockRaw] = None
    display: Optional[ScoreBlockDisplay] = None

    @model_validator(mode="after")
    def validate_pair(self) -> "Scores":
        if (self.raw is None) != (self.display is None):
            raise ValueError("scores.raw and scores.display must be both null or both non-null")
        return self


class Security(BaseModel):
    name: str
    ticker: str
    exchange: Optional[str] = None
    country: Optional[str] = None
    asset_class: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    peer_group_id: Optional[str] = None
    price_currency: Optional[str] = None
    reporting_currency: Optional[str] = None


class Classification(BaseModel):
    template_id: str
    template_label: str
    dominant_segment: Optional[str] = None
    routing_reason: List[str] = Field(default_factory=list)
    compare_scope: str


class Analysis(BaseModel):
    status: Status
    gate_stage: GateStage
    gate_reasons: List[str] = Field(default_factory=list)
    confidence_score: Optional[ConfidenceScore] = None


class UILabels(BaseModel):
    axis_1: str = "수익력"
    axis_2: str = "지속력"
    axis_3: str = "가격매력"
    total: str = "최종점수"
    confidence: str = "분석 신뢰도"


class Explanations(BaseModel):
    axis_1: Optional[str] = None
    axis_2: Optional[str] = None
    axis_3: Optional[str] = None
    summary: str


class Meta(BaseModel):
    analysis_timestamp: Optional[str] = None
    price_timestamp: Optional[str] = None
    latest_financial_period: Optional[str] = None
    latest_filing_date: Optional[str] = None
    valuation_currency: Optional[str] = None
    currency_mismatch_flag: Optional[bool] = None
    fx_rate_applied: Optional[float] = None
    fx_rate_timestamp: Optional[str] = None
    fx_source: Optional[str] = None
    fx_normalization_method: Optional[str] = None
    confidence_breakdown: Optional[Dict[str, float]] = None
    analysis_version: str = "v1.4-final-crosscheck-complete"


class AnalysisResponse(BaseModel):
    security: Security
    classification: Classification
    analysis: Analysis
    ui_labels: UILabels = Field(default_factory=UILabels)
    scores: Scores
    subscores: Optional[Dict[str, Dict[str, float]]] = None
    flags: List[str] = Field(default_factory=list)
    explanations: Explanations
    meta: Meta

    @model_validator(mode="after")
    def validate_contract(self) -> "AnalysisResponse":
        status = self.analysis.status
        gate_stage = self.analysis.gate_stage
        scores_present = self.scores.raw is not None
        confidence_present = self.analysis.confidence_score is not None
        breakdown_present = self.meta.confidence_breakdown is not None

        valid_pairs = {
            ("analyzed", "all_passed"),
            ("gate_fail", "universal_gate"),
            ("gate_fail", "template_specific_gate"),
            ("special_case_excluded", "universal_exclusion"),
            ("unsupported_asset", "unsupported_scope"),
        }
        if (status, gate_stage) not in valid_pairs:
            raise ValueError("invalid status/gate_stage combination")

        if status == "analyzed":
            if not scores_present:
                raise ValueError("analyzed responses must expose scores")
            if self.analysis.gate_reasons:
                raise ValueError("analyzed responses must have empty gate_reasons")
        else:
            if scores_present:
                raise ValueError("non-analyzed responses must not expose scores")

        if status in {"special_case_excluded", "unsupported_asset"} and confidence_present:
            raise ValueError("excluded/unsupported responses must not expose confidence")

        if confidence_present != breakdown_present:
            raise ValueError("confidence_score and confidence_breakdown must be synchronized")

        if status == "analyzed" and confidence_present is False:
            raise ValueError("analyzed responses must expose confidence")

        for values in (self.classification.routing_reason, self.analysis.gate_reasons, self.flags):
            for value in values:
                if not CODE_RE.match(value):
                    raise ValueError(f"non machine-readable code found: {value}")

        return self
