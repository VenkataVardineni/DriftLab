"""Tests for dataset validation command."""

import pandas as pd

from driftlab.validate_datasets import validate_pair


def test_validate_pair_ok(tmp_path):
    ref = tmp_path / "r.csv"
    cur = tmp_path / "c.csv"
    pd.DataFrame({"a": [1, 2]}).to_csv(ref, index=False)
    pd.DataFrame({"a": [3, 4]}).to_csv(cur, index=False)
    out = validate_pair(str(ref), str(cur), None)
    assert out["valid"] is True


def test_validate_pair_missing_required(tmp_path):
    ref = tmp_path / "r.csv"
    cur = tmp_path / "c.csv"
    cfg = tmp_path / "c.yaml"
    pd.DataFrame({"a": [1]}).to_csv(ref, index=False)
    pd.DataFrame({"a": [2]}).to_csv(cur, index=False)
    cfg.write_text(
        "column_types:\n  a: numerical\nrequired_columns:\n  - a\n  - missing\n",
        encoding="utf-8",
    )
    out = validate_pair(str(ref), str(cur), str(cfg))
    assert out["valid"] is False
