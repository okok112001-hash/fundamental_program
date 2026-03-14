from app.core.score_rules import apply_one_dimension_defense, weighted_average


def test_weighted_average():
    assert round(weighted_average([(50, 1), (100, 1)]), 1) == 75.0


def test_one_dimension_defense():
    assert round(apply_one_dimension_defense(100.0, 0.3), 1) == 85.0
