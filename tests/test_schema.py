"""Tests for schema validation."""

import pytest
import pandas as pd
from driftlab.io.schema import Schema, ColumnType


def test_schema_validation():
    """Test basic schema validation."""
    df = pd.DataFrame({
        "numerical_col": [1, 2, 3, 4, 5],
        "categorical_col": ["A", "B", "A", "B", "A"],
        "text_col": ["text1", "text2", "text3", "text4", "text5"]
    })
    
    schema = Schema(
        column_types={
            "numerical_col": ColumnType.NUMERICAL,
            "categorical_col": ColumnType.CATEGORICAL,
            "text_col": ColumnType.TEXT
        },
        required_columns=["numerical_col", "categorical_col"]
    )
    
    result = schema.validate(df)
    assert result["valid"] is True
    assert "numerical_col" in result["quality_metrics"]


def test_missing_required_column():
    """Test validation with missing required column."""
    df = pd.DataFrame({
        "numerical_col": [1, 2, 3]
    })
    
    schema = Schema(required_columns=["numerical_col", "missing_col"])
    result = schema.validate(df)
    assert result["valid"] is False
    assert "Missing required columns" in str(result["errors"])

