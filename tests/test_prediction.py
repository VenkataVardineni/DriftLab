"""Tests for prediction drift profile."""

import pandas as pd
from driftlab.profiles.prediction import PredictionProfile


def test_prediction_profile_numeric():
    ref = pd.DataFrame({"score": [0.1, 0.2, 0.3, 0.4, 0.5]})
    cur = pd.DataFrame({"score": [0.5, 0.6, 0.7, 0.8, 0.9]})
    p = PredictionProfile(prediction_columns=["score"])
    out = p.run(ref, cur)
    assert "score_prediction_drift" in out["metrics"]
    assert out["metrics"]["score_prediction_drift"]["prediction_drift_score"] > 0


def test_prediction_profile_categorical():
    ref = pd.DataFrame({"label": ["a", "a", "b", "b"]})
    cur = pd.DataFrame({"label": ["b", "b", "b", "b"]})
    p = PredictionProfile(prediction_columns=["label"])
    out = p.run(ref, cur)
    assert out["metrics"]["label_prediction_drift"]["prediction_drift_score"] > 0
