"""Prediction and score drift (distribution shift on model outputs)."""

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from .base import Profile


def _numeric_prediction_shift(ref: pd.Series, cur: pd.Series) -> Dict[str, float]:
    r = pd.to_numeric(ref, errors="coerce").dropna()
    c = pd.to_numeric(cur, errors="coerce").dropna()
    if len(r) < 2 or len(c) < 2:
        return {"prediction_drift_score": 0.0}
    rmean, cmean = float(r.mean()), float(c.mean())
    rstd = float(r.std()) or 1e-9
    mean_shift = min(1.0, abs(rmean - cmean) / (rstd + 1e-9))
    lo = min(float(r.min()), float(c.min()))
    hi = max(float(r.max()), float(c.max()))
    if lo >= hi:
        hi = lo + 1e-9
    ah, edges = np.histogram(r.to_numpy(), bins=20, range=(lo, hi), density=True)
    bh, _ = np.histogram(c.to_numpy(), bins=edges, density=True)
    s1, s2 = ah.sum(), bh.sum()
    ah = ah / (s1 + 1e-12)
    bh = bh / (s2 + 1e-12)
    overlap = float(np.minimum(ah, bh).sum())
    dist_tv = 1.0 - overlap
    score = float(min(1.0, 0.5 * mean_shift + 0.5 * dist_tv))
    return {
        "prediction_drift_score": score,
        "mean_shift_normalized": mean_shift,
        "distribution_tv_proxy": dist_tv,
    }


def _categorical_prediction_shift(ref: pd.Series, cur: pd.Series) -> Dict[str, float]:
    r = ref.dropna().astype(str).value_counts(normalize=True)
    c = cur.dropna().astype(str).value_counts(normalize=True)
    keys = set(r.index) | set(c.index)
    if not keys:
        return {"prediction_drift_score": 0.0}
    tv = sum(abs(float(r.get(k, 0.0)) - float(c.get(k, 0.0))) for k in keys) * 0.5
    return {
        "prediction_drift_score": float(min(1.0, tv)),
        "total_variation_distance": float(tv),
    }


class PredictionProfile(Profile):
    """Compare prediction or score columns between reference and current windows."""

    def __init__(self, prediction_columns: Optional[List[str]] = None):
        self.prediction_columns = list(prediction_columns or [])

    def run(self, reference_df: pd.DataFrame, current_df: pd.DataFrame) -> Dict[str, Any]:
        metrics: Dict[str, Any] = {}
        for col in self.prediction_columns:
            if col not in reference_df.columns or col not in current_df.columns:
                continue
            ref_s = reference_df[col]
            cur_s = current_df[col]
            if pd.api.types.is_numeric_dtype(ref_s) and pd.api.types.is_numeric_dtype(cur_s):
                sub = _numeric_prediction_shift(ref_s, cur_s)
            else:
                sub = _categorical_prediction_shift(ref_s, cur_s)
            metrics[f"{col}_prediction_drift"] = sub
        return {"metrics": metrics, "artifacts": {}}
