"""Main drift analysis runner."""

from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd

from driftlab.io.load import load_dataframe
from driftlab.io.schema import Schema
from driftlab.profiles.tabular import TabularProfile
from driftlab.profiles.text import TextProfile
from driftlab.reports.evidently_report import generate_evidently_report
from driftlab.reports.render import save_json_report
from driftlab.alerts.rules import DatasetDriftRule, FeatureDriftPersistenceRule
from driftlab.alerts.thresholds import ThresholdCalibrator


def run_drift_analysis(
    ref_path: str,
    cur_path: str,
    output_dir: str,
    config_path: Optional[str] = None
) -> None:
    """
    Run complete drift analysis pipeline.
    
    Args:
        ref_path: Path to reference dataset
        cur_path: Path to current dataset
        output_dir: Output directory for reports
        config_path: Optional config file path
    """
    # Load configuration if provided
    config = {}
    if config_path:
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    
    # Load datasets
    ref_df = load_dataframe(ref_path)
    cur_df = load_dataframe(cur_path)
    
    # Schema validation
    column_types = config.get('column_types', {})
    schema = Schema(column_types=column_types)
    ref_validation = schema.validate(ref_df)
    cur_validation = schema.validate(cur_df)
    
    # Generate reports
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get text columns from config or auto-detect
    text_columns = config.get('text_columns', None)
    column_mapping = config.get('column_mapping', None)
    
    # Filter out text columns for Evidently (it has issues with text processing)
    column_types = config.get('column_types', {})
    text_cols_set = set(text_columns or [])
    # Also detect text columns from column_types
    for col, col_type in column_types.items():
        if col_type == 'text':
            text_cols_set.add(col)
    
    # Create dataframes without text columns for Evidently
    ref_df_tabular = ref_df.drop(columns=[c for c in text_cols_set if c in ref_df.columns], errors='ignore')
    cur_df_tabular = cur_df.drop(columns=[c for c in text_cols_set if c in cur_df.columns], errors='ignore')
    
    # Run profiles
    tabular_profile = TabularProfile(column_mapping=column_mapping)
    tabular_results = tabular_profile.run(ref_df, cur_df)
    
    text_profile = TextProfile(text_columns=text_columns)
    text_results = text_profile.run(ref_df, cur_df)
    
    # Generate Evidently report (only on non-text columns)
    evidently_results = generate_evidently_report(
        ref_df_tabular, cur_df_tabular, output_dir, column_mapping=column_mapping
    )
    
    # Combine all metrics
    all_metrics = {
        **tabular_results.get("metrics", {}),
        **text_results.get("metrics", {}),
        **evidently_results.get("metrics", {})
    }
    
    # Setup threshold calibrator
    history_file = config.get('history_file', '.driftlab_history.json')
    calibrator = ThresholdCalibrator(history_file=history_file)
    
    # Setup alert rules with calibrated thresholds
    alert_config = config.get('alerts', {})
    alert_rules = [
        DatasetDriftRule(
            threshold=alert_config.get('dataset_drift_threshold'),
            calibrator=calibrator
        ),
        FeatureDriftPersistenceRule(
            threshold=alert_config.get('feature_drift_threshold'),
            consecutive_runs=alert_config.get('consecutive_runs', 3),
            calibrator=calibrator,
            history_file=history_file
        )
    ]
    
    # Add metrics to history for calibration
    calibrator.add_metrics(all_metrics)
    
    # Evaluate alerts
    all_alerts = []
    for rule in alert_rules:
        alerts = rule.evaluate(all_metrics)
        all_alerts.extend(alerts)
    
    # Save summary
    summary = {
        "run_id": output_path.name,
        "reference_path": ref_path,
        "current_path": cur_path,
        "validation": {
            "reference": ref_validation,
            "current": cur_validation
        },
        "metrics": all_metrics,
        "alerts": all_alerts,
        "reports": {
            "html": evidently_results.get("html_path"),
            "json": str(output_path / "drift_summary.json")
        }
    }
    
    save_json_report(summary, str(output_path / "drift_summary.json"))
    
    # Print alerts
    print(f"\n=== Drift Analysis Complete ===")
    print(f"Report saved to: {output_path}")
    print(f"HTML report: {evidently_results.get('html_path')}")
    print(f"JSON summary: {output_path / 'drift_summary.json'}")
    
    if all_alerts:
        alert_messages = []
        for alert in all_alerts:
            if alert.get("severity") == "critical":
                metric_name = alert.get("metric_name", "unknown")
                message = alert.get("message", "Drift detected")
                # Format for specific columns
                if "payload_bytes" in str(metric_name) or "run_duration_ms" in str(metric_name):
                    alert_messages.append(f"ALERT: drift in {metric_name} exceeded threshold")
                else:
                    alert_messages.append(f"ALERT: {message}")
        
        if alert_messages:
            print(f"\n=== Alerts ({len(alert_messages)}) ===")
            print("\n".join(alert_messages))
    else:
        print("\nNo alerts triggered.")
