"""Prometheus textfile-style metrics from drift summaries."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def _escape_label(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def metrics_from_summary(summary: Dict[str, Any]) -> List[str]:
    """Build Prometheus exposition lines (no types/help for minimal node_exporter textfile use)."""
    lines: List[str] = []
    run_id = summary.get("run_id", "unknown")
    rid = _escape_label(str(run_id))

    m = summary.get("metrics") or {}
    ds = m.get("dataset_drift_score")
    if ds is not None:
        lines.append(f'driftlab_dataset_drift_score{{run_id="{rid}"}} {float(ds)}')

    dshare = m.get("drifting_columns_share")
    if dshare is not None:
        lines.append(f'driftlab_drifting_columns_share{{run_id="{rid}"}} {float(dshare)}')

    crit = sum(1 for a in summary.get("alerts") or [] if a.get("severity") == "critical")
    lines.append(f'driftlab_critical_alerts{{run_id="{rid}"}} {int(crit)}')

    return lines


def write_prometheus_textfile(summary: Dict[str, Any], output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(metrics_from_summary(summary)) + "\n"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(body, encoding="utf-8")
    tmp.replace(path)
