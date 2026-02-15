"""Tests for drift profiles."""

import pytest
import pandas as pd
from driftlab.profiles.tabular import TabularProfile
from driftlab.profiles.text import TextProfile


def test_tabular_profile():
    """Test tabular profile execution."""
    ref_df = pd.DataFrame({
        "col1": [1, 2, 3, 4, 5],
        "col2": [10, 20, 30, 40, 50]
    })
    cur_df = pd.DataFrame({
        "col1": [2, 3, 4, 5, 6],
        "col2": [15, 25, 35, 45, 55]
    })
    
    profile = TabularProfile()
    result = profile.run(ref_df, cur_df)
    
    assert "metrics" in result
    assert "artifacts" in result


def test_text_profile():
    """Test text profile execution."""
    ref_df = pd.DataFrame({
        "text_col": ["hello world", "foo bar", "baz qux"]
    })
    cur_df = pd.DataFrame({
        "text_col": ["hello world changed", "foo bar modified", "baz qux updated"]
    })
    
    profile = TextProfile(text_columns=["text_col"])
    result = profile.run(ref_df, cur_df)
    
    assert "metrics" in result
    # Text drift metrics should be present if model is available
    if result["metrics"]:
        assert any("text_drift" in key for key in result["metrics"].keys())

