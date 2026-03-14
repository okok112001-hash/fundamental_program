# Contract invariants

## Status / score invariants
- analyzed -> scores.raw != null AND scores.display != null
- gate_fail -> scores.raw == null AND scores.display == null
- special_case_excluded -> scores.raw == null AND scores.display == null
- unsupported_asset -> scores.raw == null AND scores.display == null

## Confidence invariants
- special_case_excluded -> confidence_score == null AND confidence_breakdown == null
- unsupported_asset -> confidence_score == null AND confidence_breakdown == null
- gate_fail -> confidence nullable
- confidence_score == null <-> confidence_breakdown == null

## Exclusion invariants
- unsupported_asset -> gate_stage == unsupported_scope
- special_case_excluded -> gate_stage == universal_exclusion
- unsupported_asset / special_case_excluded must not be emitted as gate_fail

## Routing invariants
- financial branch entry requires enterprise materiality
- preliminary routing may re-route
- if no acceptable template exists after validation -> universal gate: model_incompatible/template_mismatch

## FX invariants
- if cross-currency normalization succeeds, valuation_currency and fx_normalization_method must be present
- if cross-currency normalization fails -> universal gate
