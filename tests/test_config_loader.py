"""Tests for config loading."""

import pytest

from driftlab.config_loader import DEFAULTS, deep_merge, load_config


def test_deep_merge_nested():
    base = {"a": {"x": 1}, "b": 2}
    over = {"a": {"y": 3}, "c": 4}
    m = deep_merge(base, over)
    assert m["a"]["x"] == 1
    assert m["a"]["y"] == 3
    assert m["b"] == 2
    assert m["c"] == 4


def test_load_config_none():
    c = load_config(None)
    assert "history_file" in c
    assert c["history_file"] == DEFAULTS["history_file"]


def test_load_config_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(str(tmp_path / "nope.yaml"))
