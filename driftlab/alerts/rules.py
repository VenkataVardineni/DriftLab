"""Alert rule implementations."""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from .base import AlertRule
from .thresholds import ThresholdCalibrator


class DatasetDriftRule(AlertRule):
    """Alert if dataset drift exceeds threshold."""
    
    def __init__(
        self,
        threshold: Optional[float] = None,
        calibrator: Optional[ThresholdCalibrator] = None,
        metric_name: str = "drifting_columns_share"
    ):
        """
        Initialize dataset drift rule.
        
        Args:
            threshold: Fixed threshold (if None, uses calibrator)
            calibrator: Threshold calibrator for dynamic thresholds
            metric_name: Name of metric to check
        """
        self.threshold = threshold
        self.calibrator = calibrator
        self.metric_name = metric_name
    
    def evaluate(self, metrics_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate dataset drift threshold."""
        alerts = []
        
        # Get threshold
        threshold = self.threshold
        if threshold is None and self.calibrator:
            threshold = self.calibrator.calibrate_threshold(self.metric_name)
        if threshold is None:
            threshold = 0.5  # Default
        
        # Check metric
        metric_value = metrics_dict.get(self.metric_name, 0.0)
        
        if metric_value >= threshold:
            alerts.append({
                "severity": "critical",
                "message": f"Dataset drift: {self.metric_name} = {metric_value:.3f} exceeded threshold {threshold:.3f}",
                "metric_name": self.metric_name,
                "value": metric_value,
                "threshold": threshold
            })
        
        return alerts


class FeatureDriftPersistenceRule(AlertRule):
    """Alert if feature drift persists across consecutive runs."""
    
    def __init__(
        self,
        threshold: Optional[float] = None,
        consecutive_runs: int = 3,
        calibrator: Optional[ThresholdCalibrator] = None,
        history_file: Optional[str] = None
    ):
        """
        Initialize persistence rule.
        
        Args:
            threshold: Fixed threshold for feature drift
            consecutive_runs: Number of consecutive runs required
            calibrator: Threshold calibrator
            history_file: Path to history file for persistence tracking
        """
        self.threshold = threshold
        self.consecutive_runs = consecutive_runs
        self.calibrator = calibrator
        self.history_file = history_file or ".driftlab_history.json"
    
    def _load_persistence_history(self) -> Dict[str, List[bool]]:
        """Load persistence history for features."""
        if not Path(self.history_file).exists():
            return {}
        
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_persistence_history(self, history: Dict[str, List[bool]]) -> None:
        """Save persistence history."""
        Path(self.history_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def evaluate(self, metrics_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate feature drift persistence."""
        alerts = []
        
        # Get threshold
        threshold = self.threshold
        if threshold is None and self.calibrator:
            threshold = self.calibrator.calibrate_threshold("feature_drift_score")
        if threshold is None:
            threshold = 0.3  # Default
        
        # Load persistence history
        persistence_history = self._load_persistence_history()
        
        # Check column drift scores
        column_drift_scores = metrics_dict.get("column_drift_scores", {})
        
        for col_name, col_metrics in column_drift_scores.items():
            drift_score = col_metrics.get("drift_score", 0.0)
            drift_detected = drift_score >= threshold
            
            # Update history
            if col_name not in persistence_history:
                persistence_history[col_name] = []
            
            persistence_history[col_name].append(drift_detected)
            
            # Keep only last N runs
            if len(persistence_history[col_name]) > self.consecutive_runs:
                persistence_history[col_name] = persistence_history[col_name][-self.consecutive_runs:]
            
            # Check if persistent
            if len(persistence_history[col_name]) >= self.consecutive_runs:
                if all(persistence_history[col_name][-self.consecutive_runs:]):
                    alerts.append({
                        "severity": "critical",
                        "message": f"Feature {col_name} has drifted above threshold for {self.consecutive_runs} consecutive runs",
                        "metric_name": f"{col_name}_drift_score",
                        "value": drift_score,
                        "threshold": threshold,
                        "consecutive_runs": self.consecutive_runs
                    })
        
        # Save updated history
        self._save_persistence_history(persistence_history)
        
        return alerts

