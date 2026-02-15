"""Base profile interface for drift detection."""

from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd


class Profile(ABC):
    """Base interface for drift profiling."""
    
    @abstractmethod
    def run(self, reference_df: pd.DataFrame, current_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Run drift analysis on reference and current datasets.
        
        Args:
            reference_df: Baseline/reference dataset
            current_df: Current dataset to compare against reference
            
        Returns:
            Dictionary containing:
                - metrics: Dict of drift metrics
                - artifacts: Dict of artifacts (plots, embeddings, etc.)
        """
        pass

