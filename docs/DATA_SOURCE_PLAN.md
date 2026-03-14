# Data source plan (implementation view)

## Source of truth
- US filings / financials: SEC EDGAR / data.sec.gov
- KR filings / financials: OpenDART
- KR listed company / disclosure metadata: KIND / KRX
- FX + market data operational layer: provider abstraction (current recommendation: market-data API with equity + FX support)
- Convenience layer only: convenience financial API (never source of truth)

## Engineering rule
Always store:
- provider name
- retrieval timestamp
- currency
- filing period
- filing date
- FX normalization method
