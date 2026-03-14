import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_golden_set_exists():
    p = ROOT / "data" / "golden_set.csv"
    assert p.exists()


def test_special_case_and_unsupported_have_null_policies():
    p = ROOT / "data" / "golden_set.csv"
    rows = list(csv.DictReader(p.open(encoding="utf-8-sig")))
    special = [r for r in rows if r["status"] == "special_case_excluded"]
    unsupported = [r for r in rows if r["status"] == "unsupported_asset"]
    assert all(r["scores_should_be_null"] == "true" for r in special + unsupported)
    assert all(r["confidence_should_be_null"] == "true" for r in special + unsupported)
