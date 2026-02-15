"""Calibrated threshold management."""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json


class ThresholdCalibrator:
    """Calibrate thresholds from historical drift metrics."""
    
    def __init__(self, history_file: Optional[str] = None):
        """
        Initialize calibrator.
        
        Args:
            history_file: Path to JSON file storing historical metrics
        """
        self.history_file = history_file
        self.history: List[Dict[str, Any]] = []
        if history_file and Path(history_file).exists():
            self._load_history()
    
    def _load_history(self) -> None:
        """Load historical metrics from file."""
        try:
            with open(self.history_file, 'r') as f:
                self.history = json.load(f)
        except Exception:
            self.history = []
    
    def _save_history(self) -> None:
        """Save historical metrics to file."""
        if self.history_file:
            Path(self.history_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2, default=str)
    
    def add_metrics(self, metrics: Dict[str, Any]) -> None:
        """Add current metrics to history."""
        self.history.append(metrics)
        self._save_history()
    
    def calibrate_threshold(
        self,
        metric_name: str,
        percentile: float = 95.0
    ) -> float:
        """
        Calibrate threshold for a metric based on historical values.
        
        Args:
            metric_name: Name of the metric (e.g., "drift_score")
            percentile: Percentile to use for threshold (default 95th)
            
        Returns:
            Calibrated threshold value
        """
        if not self.history:
            # Default threshold if no history
            return 0.3
        
        values = []
        for entry in self.history:
            if metric_name in entry:
                values.append(entry[metric_name])
        
        if not values:
            return 0.3
        
        import numpy as np
        threshold = np.percentile(values, percentile)
        return float(threshold)

