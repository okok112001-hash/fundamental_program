# Execution plan

## Phase 1 — Contracts
Deliverables:
- frozen schema
- enums registry
- template registry
- critical metric matrix

## Phase 2 — Routing
Deliverables:
- preliminary router
- routing validation / re-routing
- golden routing tests

## Phase 3 — Gates
Deliverables:
- universal gate runner
- template-specific gate runner
- mixed financial group gate runner

## Phase 4 — Scoring
Deliverables:
- metric engine
- component engine
- axis aggregation
- total aggregation
- confidence engine

## Phase 5 — API + UI support
Deliverables:
- analyzed response
- gate_fail response
- excluded / unsupported response
- explanation payload

## Acceptance checkpoints
Checkpoint A:
- routing golden set passes

Checkpoint B:
- gate/status/nullability contract passes

Checkpoint C:
- score engine returns stable outputs for analyzed cases
