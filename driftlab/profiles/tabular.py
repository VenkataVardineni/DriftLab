"""Tabular drift profiling using Evidently."""

from typing import Dict, Any, Optional
import pandas as pd
from .base import Profile
from driftlab.reports.evidently_report import generate_evidently_report


class TabularProfile(Profile):
    """Tabular data drift profile."""
    
    def __init__(self, column_mapping: Optional[Dict[str, Any]] = None):
        """
        Initialize tabular profile.
        
        Args:
            column_mapping: Optional column mapping for Evidently
        """
        self.column_mapping = column_mapping
    
    def run(self, reference_df: pd.DataFrame, current_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Run tabular drift analysis.
        
        Returns:
            {
                "metrics": {...},
                "artifacts": {...}
            }
        """
        # Use Evidently for tabular drift detection
        # This will be called from the main runner with output directory
        # For now, return metrics structure
        return {
            "metrics": {
                "profile_type": "tabular",
                "columns_analyzed": list(reference_df.columns)
            },
            "artifacts": {}
        }

