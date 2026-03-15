from __future__ import annotations

from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import HTMLResponse

from app.api.schemas import AnalysisResponse
from app.core.demo_engine import build_demo_response
from app.services.adapters import adapt_provider
from app.core.analysis_pipeline import analyze_standardized_input

app = FastAPI(title="Fundamental Analysis Program API", version="v1.4")


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
<head>
  <meta charset="utf-8">
  <title>기본적 분석 프로그램</title>
  <style>
    #result { margin-top: 1rem; padding: 1rem; border: 1px solid #ccc; max-width: 40rem; }
    #result dl { margin: 0.5rem 0; }
    #result dt { font-weight: bold; margin-top: 0.5rem; }
    #result .status { font-weight: bold; }
    #result .scores table { border-collapse: collapse; }
    #result .scores th, #result .scores td { padding: 0.25rem 0.5rem; text-align: left; }
  </style>
</head>
<body>
  <h1>기본적 분석 프로그램</h1>
  <form id="f">
    <input id="ticker" placeholder="티커 입력" value="AAPL" />
    <button type="submit">분석</button>
  </form>
  <div id="result" style="display:none;">
    <p class="status">상태: <span id="analysis-status"></span></p>
    <section aria-label="점수">
      <h2>점수</h2>
      <p>수익력: <span id="axis-1"></span></p>
      <p>지속력: <span id="axis-2"></span></p>
      <p>가격매력: <span id="axis-3"></span></p>
      <p>최종점수: <span id="total"></span></p>
    </section>
    <p>분석 신뢰도: <span id="confidence"></span></p>
    <p>요약 설명: <span id="summary"></span></p>
    <p>탈락·제외 사유: <span id="gate-reasons"></span></p>
    <p>경고 플래그: <span id="flags"></span></p>
    <pre id="out"></pre>
  </div>
<script>
const form = document.getElementById('f');
const result = document.getElementById('result');
const out = document.getElementById('out');
function render(data) {
  result.style.display = 'block';
  document.getElementById('analysis-status').textContent = data.analysis?.status || '-';
  const scores = data.scores?.display;
  if (scores) {
    document.getElementById('axis-1').textContent = scores.axis_1 != null ? scores.axis_1 : '-';
    document.getElementById('axis-2').textContent = scores.axis_2 != null ? scores.axis_2 : '-';
    document.getElementById('axis-3').textContent = scores.axis_3 != null ? scores.axis_3 : '-';
    document.getElementById('total').textContent = scores.total != null ? scores.total : '-';
  } else {
    document.getElementById('axis-1').textContent = '-';
    document.getElementById('axis-2').textContent = '-';
    document.getElementById('axis-3').textContent = '-';
    document.getElementById('total').textContent = '-';
  }
  const conf = data.analysis?.confidence_score?.display;
  document.getElementById('confidence').textContent = conf != null ? conf : '-';
  document.getElementById('summary').textContent = data.explanations?.summary || '-';
  document.getElementById('gate-reasons').textContent = (data.analysis?.gate_reasons?.length) ? data.analysis.gate_reasons.join(', ') : '-';
  document.getElementById('flags').textContent = (data.flags?.length) ? data.flags.join(', ') : '-';
  out.textContent = JSON.stringify(data, null, 2);
}
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const ticker = document.getElementById('ticker').value.trim();
  const res = await fetch('/analysis/' + encodeURIComponent(ticker));
  const data = await res.json();
  render(data);
});
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def root() -> str:
    return _HTML


@app.get("/ui", response_class=HTMLResponse)
def ui() -> str:
    return _HTML
