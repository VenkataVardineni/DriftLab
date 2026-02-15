"""Data schema validation and quality checks."""

from typing import Dict, List, Optional, Any
import pandas as pd
from datetime import datetime


class ColumnType:
    """Column type constants."""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TEXT = "text"
    TIMESTAMP = "timestamp"


class Schema:
    """Data schema definition and validation."""
    
    def __init__(
        self,
        column_types: Optional[Dict[str, str]] = None,
        required_columns: Optional[List[str]] = None,
        timestamp_column: Optional[str] = None
    ):
        """
        Initialize schema.
        
        Args:
            column_types: Mapping of column name to type (numerical/categorical/text/timestamp)
            required_columns: List of required column names
            timestamp_column: Name of timestamp column if present
        """
        self.column_types = column_types or {}
        self.required_columns = required_columns or []
        self.timestamp_column = timestamp_column
    
    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate DataFrame against schema and perform quality checks.
        
        Returns:
            Dictionary with validation results and quality metrics
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "quality_metrics": {}
        }
        
        # Check required columns
        missing_cols = set(self.required_columns) - set(df.columns)
        if missing_cols:
            results["valid"] = False
            results["errors"].append(f"Missing required columns: {missing_cols}")
        
        # Check for empty columns
        empty_cols = df.columns[df.isnull().all()].tolist()
        if empty_cols:
            results["warnings"].append(f"Empty columns detected: {empty_cols}")
        
        # Parse timestamp if specified
        if self.timestamp_column and self.timestamp_column in df.columns:
            try:
                df[self.timestamp_column] = pd.to_datetime(df[self.timestamp_column])
            except Exception as e:
                results["warnings"].append(f"Failed to parse timestamp column: {e}")
        
        # Quality metrics
        quality = {}
        for col in df.columns:
            col_type = self.column_types.get(col, "unknown")
            quality[col] = {
                "missing_pct": (df[col].isnull().sum() / len(df)) * 100,
                "unique_count": df[col].nunique(),
            }
            
            if col_type == ColumnType.NUMERICAL:
                quality[col]["min"] = float(df[col].min()) if not df[col].isnull().all() else None
                quality[col]["max"] = float(df[col].max()) if not df[col].isnull().all() else None
            elif col_type == ColumnType.CATEGORICAL:
                quality[col]["top_values"] = df[col].value_counts().head(5).to_dict()
        
        results["quality_metrics"] = quality
        
        return results

