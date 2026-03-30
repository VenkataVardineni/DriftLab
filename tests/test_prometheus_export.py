"""Tests for Prometheus textfile export."""

from driftlab.reports.prometheus_export import metrics_from_summary, write_prometheus_textfile


def test_metrics_from_summary_lines():
    summary = {
        "run_id": "r1",
        "metrics": {"dataset_drift_score": 0.42, "drifting_columns_share": 0.1},
        "alerts": [{"severity": "critical"}, {"severity": "info"}],
    }
    lines = metrics_from_summary(summary)
    assert any("driftlab_dataset_drift_score" in ln for ln in lines)
    assert any("driftlab_critical_alerts" in ln and " 1" in ln for ln in lines)


def test_write_prometheus_textfile(tmp_path):
    summary = {"run_id": "x", "metrics": {"dataset_drift_score": 1.0}, "alerts": []}
    p = tmp_path / "m.prom"
    write_prometheus_textfile(summary, str(p))
    text = p.read_text()
    assert "driftlab_dataset_drift_score" in text
