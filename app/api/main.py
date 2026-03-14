from __future__ import annotations

from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import HTMLResponse

from app.api.schemas import AnalysisResponse
from app.core.demo_engine import build_demo_response
from app.services.adapters import adapt_provider
from app.core.analysis_pipeline import analyze_standardized_input

app = FastAPI(title="Fundamental Analysis Program API", version="v1.4-candidate")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/analysis/{ticker}", response_model=AnalysisResponse)
def get_analysis(ticker: str) -> AnalysisResponse:
    payload = build_demo_response(ticker)
    return AnalysisResponse(**payload)


@app.post("/analysis/provider/{provider}", response_model=AnalysisResponse)
def analyze_provider(provider: str, payload: dict = Body(...)) -> AnalysisResponse:
    try:
        std = adapt_provider(provider, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    result = analyze_standardized_input(std)
    return AnalysisResponse(**result)


_HTML = """
<!doctype html>
<html lang="ko">
<head><meta charset="utf-8"><title>Fundamental Analysis</title></head>
<body>
  <h1>기본적 분석 프로그램</h1>
  <form id="f">
    <input id="ticker" placeholder="티커 입력" value="AAPL" />
    <button type="submit">분석</button>
  </form>
  <pre id="out"></pre>
<script>
const form = document.getElementById('f');
const out = document.getElementById('out');
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const ticker = document.getElementById('ticker').value.trim();
  const res = await fetch(`/analysis/${ticker}`);
  const data = await res.json();
  out.textContent = JSON.stringify(data, null, 2);
});
</script>
</body></nhtml>
"""

@app.get("/", response_class=HTMLResponse)
def root() -> str:
    return _HTML


@app.get("/ui", response_class=HTMLResponse)
def ui() -> str:
    return _HTML
