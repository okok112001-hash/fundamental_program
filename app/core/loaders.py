from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
CONFIG = ROOT / "app" / "config"


def load_json_config(name: str) -> Any:
    with (CONFIG / name).open(encoding="utf-8") as f:
        return json.load(f)


def load_golden_set() -> List[Dict[str, str]]:
    with (DATA / "golden_set.csv").open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_critical_metric_matrix() -> List[Dict[str, str]]:
    with (DATA / "critical_metric_matrix.csv").open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))
