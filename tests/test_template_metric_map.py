from app.core.loaders import load_json_config
from app.core.scoring_engine import score_template


def test_template_metric_map_has_all_scored_templates():
    registry = load_json_config('template_registry.json')
    metric_map = load_json_config('template_metric_map.json')
    scored = {t['id'] for t in registry['templates']}
    assert scored.issubset(metric_map.keys())


def test_score_template_bank_uses_loaded_metric_map():
    subscores = {
        'axis_1': {'normalized_earning_power': 70.0, 'spread_quality': 68.0, 'operating_efficiency': 62.0, 'fee_diversification': 58.0},
        'axis_2': {'capital_adequacy': 75.0, 'asset_quality': 72.0, 'funding_liquidity': 70.0, 'regulation_governance': 60.0},
        'axis_3': {'pb_vs_roe': 57.0, 'dividend_sustainability': 65.0, 'relative_valuation': 59.0},
    }
    result = score_template('bank', subscores)
    assert result['scores'] is not None
    assert result['scores']['display']['axis_1'] == 6.5
