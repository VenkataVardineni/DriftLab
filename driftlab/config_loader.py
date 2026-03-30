"""YAML config loading with nested defaults."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULTS: Dict[str, Any] = {
    "fingerprint_sample_rows": 5,
    "prometheus_textfile": False,
    "history_file": ".driftlab_history.json",
    "persistence_history_file": ".driftlab_persistence.json",
    "alerts": {
        "consecutive_runs": 3,
    },
    "output": {
        "directory": "reports",
    },
}


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(base)
    for key, val in override.items():
        if (
            key in out
            and isinstance(out[key], dict)
            and isinstance(val, dict)
        ):
            out[key] = deep_merge(out[key], val)
        else:
            out[key] = copy.deepcopy(val)
    return out


def load_config(config_path: Optional[str]) -> Dict[str, Any]:
    if not config_path:
        return copy.deepcopy(DEFAULTS)
    path = Path(config_path)
    if not path.is_file():
        raise FileNotFoundError(f"Config not found: {config_path}")
    import yaml

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError("Config root must be a mapping")
    return deep_merge(DEFAULTS, raw)
