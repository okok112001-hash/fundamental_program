# Public / internal schema split

## Public
Expose:
- security
- classification
- analysis
- ui_labels
- scores
- subscores (optional)
- flags
- explanations
- meta

Never expose:
- shadow_scores
- route trace internals
- proxy trace internals
- detailed gate runner traces
- raw provider payloads

## Internal
Allowed:
- shadow_scores
- route trace
- gate trace
- proxy used trace
- confidence intermediate values
- raw metric availability matrix
