"""Evidently-based drift report generation."""

from typing import Dict, Any, Optional
import pandas as pd
from pathlib import Path
import json

try:
    from evidently.report import Report
    from evidently.metric_preset import DataDriftPreset
    from evidently.pipeline.column_mapping import ColumnMapping
    EVIDENTLY_AVAILABLE = True
except ImportError:
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
    
    # Create column mapping if provided
    col_mapping = None
    if column_mapping:
        col_mapping = ColumnMapping(**column_mapping)
    
    # Create and run Evidently report
    report = Report(metrics=[DataDriftPreset()])
    report.run(
        reference_data=reference_df,
        current_data=current_df,
        column_mapping=col_mapping
    )
    
    # Save HTML report
    html_path = output_path / "drift_report.html"
    report.save_html(str(html_path))
    
    # Extract metrics from report
    metrics_dict = {}
    try:
        if hasattr(report, 'as_dict'):
            report_dict = report.as_dict()
            metrics_dict = report_dict.get('metrics', {})
    except Exception:
        pass
    
    # Extract drift scores from report
    drift_metrics = {}
    drifting_columns = []
    dataset_drift_score = 0.0
    
    # Try to extract from report JSON
    try:
        report_json = report.json()
        import json
        report_data = json.loads(report_json)
        
        # Navigate through Evidently's metric structure
        for metric_data in report_data.get('metrics', []):
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
        # Fallback: try to access directly from report object
        try:
            # Evidently 0.4+ structure
            if hasattr(report, '_inner_suite') and hasattr(report._inner_suite, 'context'):
                for metric in report._inner_suite.context.metrics:
                    if hasattr(metric, 'result'):
                        result = metric.result
                        if hasattr(result, 'dataset_drift_score'):
                            dataset_drift_score = result.dataset_drift_score
                        if hasattr(result, 'drift_by_columns'):
                            for col_name, col_result in result.drift_by_columns.items():
                                if hasattr(col_result, 'drift_score'):
                                    drift_score = col_result.drift_score
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

