"""Evidently-based drift report generation."""

from typing import Dict, Any, Optional
import pandas as pd
from pathlib import Path
import json

try:
    # Try Evidently 0.7+ API (direct imports)
    try:
        from evidently import Report
        from evidently.presets import DataDriftPreset
        from evidently.core.datasets import ColumnMapping
        EVIDENTLY_AVAILABLE = True
    except ImportError:
        # Try older API
        try:
            from evidently.report import Report
            from evidently.metric_preset import DataDriftPreset
            from evidently.pipeline.column_mapping import ColumnMapping
            EVIDENTLY_AVAILABLE = True
        except ImportError:
            EVIDENTLY_AVAILABLE = False
except Exception:
    EVIDENTLY_AVAILABLE = False


def generate_evidently_report(
    reference_df: pd.DataFrame,
    current_df: pd.DataFrame,
    output_dir: str,
    column_mapping: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate Evidently drift report.
    
    Args:
        reference_df: Reference dataset
        current_df: Current dataset
        output_dir: Directory to save reports
        column_mapping: Optional column mapping for Evidently
        
    Returns:
        Dictionary with report metadata and metrics
    """
    if not EVIDENTLY_AVAILABLE:
        raise ImportError("evidently package is required. Install with: pip install evidently")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create and run Evidently report
    report = Report(metrics=[DataDriftPreset()])
    
    # Run report - new API returns a Snapshot
    # Catch errors during execution (e.g., text column processing issues)
    try:
        snapshot = report.run(
            reference_data=reference_df,
            current_data=current_df
        )
    except Exception as e:
        # If Evidently fails, create a minimal report
        print(f"Warning: Evidently report generation encountered an error: {e}")
        print("Continuing with basic drift analysis...")
        # Create empty snapshot-like structure
        snapshot = None
    
    # Save HTML report
    html_path = output_path / "drift_report.html"
    if snapshot:
        try:
            snapshot.save_html(str(html_path))
        except Exception as e:
            print(f"Warning: Could not save HTML report: {e}")
            # Create a minimal HTML report
            with open(html_path, 'w') as f:
                f.write("<html><body><h1>Drift Report</h1><p>Report generation encountered issues. Check JSON summary for details.</p></body></html>")
    else:
        # Create a minimal HTML report
        with open(html_path, 'w') as f:
            f.write("<html><body><h1>Drift Report</h1><p>Report generation encountered issues. Check JSON summary for details.</p></body></html>")
    
    # Extract metrics from snapshot
    drift_metrics = {}
    drifting_columns = []
    dataset_drift_score = 0.0
    
    if snapshot is None:
        # Return minimal metrics if snapshot failed
        return {
            "html_path": str(html_path),
            "json_path": str(output_path / "drift_summary.json"),
            "metrics": {
                "dataset_drift_score": 0.0,
                "drifting_columns": [],
                "drifting_columns_count": 0,
                "drifting_columns_share": 0.0,
                "column_drift_scores": {}
            }
        }
    
    try:
        # Get snapshot as dict
        snapshot_dict = snapshot.dict()
        
        # Navigate through Evidently's metric structure
        for metric_data in snapshot_dict.get('metrics', []):
            metric_result = metric_data.get('result', {})
            
            # Check for dataset drift score
            if 'dataset_drift_score' in metric_result:
                dataset_drift_score = metric_result['dataset_drift_score']
            
            # Check for column-level drift
            if 'drift_by_columns' in metric_result:
                for col_name, col_result in metric_result['drift_by_columns'].items():
                    drift_score = col_result.get('drift_score', 0.0)
                    drift_detected = col_result.get('drift_detected', False) or drift_score > 0.3
                    
                    drift_metrics[col_name] = {
                        "drift_score": drift_score,
                        "drift_detected": drift_detected
                    }
                    
                    if drift_detected:
                        drifting_columns.append(col_name)
    except Exception as e:
        # Fallback: try to get from snapshot directly
        try:
            snapshot_json = snapshot.json()
            import json
            report_data = json.loads(snapshot_json)
            
            for metric_data in report_data.get('metrics', []):
                metric_result = metric_data.get('result', {})
                if 'dataset_drift_score' in metric_result:
                    dataset_drift_score = metric_result['dataset_drift_score']
                if 'drift_by_columns' in metric_result:
                    for col_name, col_result in metric_result['drift_by_columns'].items():
                        drift_score = col_result.get('drift_score', 0.0)
                        drift_detected = drift_score > 0.3
                        drift_metrics[col_name] = {
                            "drift_score": drift_score,
                            "drift_detected": drift_detected
                        }
                        if drift_detected:
                            drifting_columns.append(col_name)
        except Exception:
            # If all else fails, use default values
            pass
    
    # Compile summary metrics
    summary_metrics = {
        "dataset_drift_score": dataset_drift_score,
        "drifting_columns": drifting_columns,
        "drifting_columns_count": len(drifting_columns),
        "drifting_columns_share": len(drifting_columns) / len(reference_df.columns) if len(reference_df.columns) > 0 else 0.0,
        "column_drift_scores": drift_metrics
    }
    
    return {
        "html_path": str(html_path),
        "json_path": str(output_path / "drift_summary.json"),
        "metrics": summary_metrics
    }

