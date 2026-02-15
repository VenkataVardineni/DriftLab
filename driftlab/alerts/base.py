"""Base alert rule interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class AlertRule(ABC):
    """Base interface for alert rules."""
    
    @abstractmethod
    def evaluate(self, metrics_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate metrics and return list of alerts.
        
        Args:
            metrics_dict: Dictionary of drift metrics from profiles
            
        Returns:
            List of alert dictionaries, each containing:
                - severity: str (e.g., "critical", "warning")
                - message: str
                - metric_name: str
                - value: Any
        """
        pass

