"""Tests for alert rules."""

from driftlab.alerts.rules import FeatureDriftPersistenceRule


def test_persistence_rule_default_file_distinct_from_calibrator_history():
    """Regression: persistence JSON must not default to the calibrator metrics file."""
    rule = FeatureDriftPersistenceRule(threshold=0.3, consecutive_runs=2)
    assert rule.history_file == ".driftlab_persistence.json"
    assert rule.history_file != ".driftlab_history.json"
