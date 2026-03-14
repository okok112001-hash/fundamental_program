# Fundamental Analysis Program — Implementation Starter Pack (V1.4)

This pack is the handoff from design to build.
It contains:

- repository structure
- API contract skeleton
- config-first template registry
- status / gate / confidence invariants
- golden routing dataset
- starter FastAPI + Pydantic + pytest scaffold
- human-only review checklist

Use this pack together with the frozen design document:
`기본적_분석_프로그램_설계도_및_제품설명서_V1.4.md`

## Recommended build order

1. Lock config + enums
2. Implement preliminary routing
3. Implement routing validation
4. Implement universal gate
5. Implement template-specific gates
6. Implement score engine
7. Implement confidence engine
8. Run golden-set tests
9. Wire UI API responses

## Public vs internal rule

Public API:
- no shadow scores
- `scores == null` when `status != analyzed`
- `confidence_score` nullable
- flat `flags`

Internal diagnostics:
- may keep `shadow_scores`
- may keep route traces / proxy traces / gate traces
- never expose those directly to users
