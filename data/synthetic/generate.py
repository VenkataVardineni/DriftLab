"""Synthetic drift data generator for reproducible demos."""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional


def generate_baseline_dataset(
    n_samples: int = 1000,
    numerical_cols: Optional[Dict[str, Dict[str, float]]] = None,
    categorical_cols: Optional[Dict[str, list]] = None,
    text_cols: Optional[Dict[str, int]] = None,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generate baseline/reference dataset.
    
    Args:
        n_samples: Number of samples
        numerical_cols: Dict of {col_name: {mean: X, std: Y}}
        categorical_cols: Dict of {col_name: [list of categories]}
        text_cols: Dict of {col_name: avg_length}
        seed: Random seed
        
    Returns:
        Generated DataFrame
    """
    np.random.seed(seed)
    
    if numerical_cols is None:
        numerical_cols = {
            "payload_bytes": {"mean": 1000.0, "std": 200.0},
            "run_duration_ms": {"mean": 500.0, "std": 100.0},
            "cpu_usage": {"mean": 0.5, "std": 0.1}
        }
    
    if categorical_cols is None:
        categorical_cols = {
            "status": ["success", "error", "timeout"],
            "region": ["us-east", "us-west", "eu-west"]
        }
    
    if text_cols is None:
        text_cols = {
            "log_message": 50
        }
    
    data = {}
    
    # Generate numerical columns
    for col_name, params in numerical_cols.items():
        data[col_name] = np.random.normal(
            params["mean"],
            params["std"],
            n_samples
        )
    
    # Generate categorical columns
    for col_name, categories in categorical_cols.items():
        probs = np.random.dirichlet(np.ones(len(categories)))
        data[col_name] = np.random.choice(categories, size=n_samples, p=probs)
    
    # Generate text columns
    words = ["error", "success", "warning", "info", "debug", "critical", "request", "response", "timeout", "retry"]
    for col_name, avg_length in text_cols.items():
        texts = []
        for _ in range(n_samples):
            n_words = int(np.random.normal(avg_length, avg_length * 0.3))
            n_words = max(1, n_words)
            text = " ".join(np.random.choice(words, size=n_words))
            texts.append(text)
        data[col_name] = texts
    
    return pd.DataFrame(data)


def generate_drifted_dataset(
    baseline_df: pd.DataFrame,
    drift_config: Optional[Dict[str, Any]] = None,
    seed: int = 43
) -> pd.DataFrame:
    """
    Generate current dataset with controlled drift.
    
    Args:
        baseline_df: Baseline dataset
        drift_config: Drift configuration
        seed: Random seed
        
    Returns:
        DataFrame with drift applied
    """
    np.random.seed(seed)
    
    if drift_config is None:
        drift_config = {
            "numerical_mean_shift": {
                "payload_bytes": 1.2,  # 20% increase
                "run_duration_ms": 1.15  # 15% increase
            },
            "numerical_variance_shift": {
                "cpu_usage": 1.5  # 50% increase in variance
            },
            "categorical_shift": {
                "status": {"error": 0.4, "success": 0.5, "timeout": 0.1}  # More errors
            },
            "text_length_shift": {
                "log_message": 1.3  # 30% longer texts
            }
        }
    
    drifted_df = baseline_df.copy()
    
    # Apply numerical mean shifts
    for col, multiplier in drift_config.get("numerical_mean_shift", {}).items():
        if col in drifted_df.columns:
            drifted_df[col] = drifted_df[col] * multiplier
    
    # Apply numerical variance shifts
    for col, multiplier in drift_config.get("numerical_variance_shift", {}).items():
        if col in drifted_df.columns:
            mean_val = drifted_df[col].mean()
            drifted_df[col] = mean_val + (drifted_df[col] - mean_val) * multiplier
    
    # Apply categorical shifts
    for col, new_probs in drift_config.get("categorical_shift", {}).items():
        if col in drifted_df.columns:
            categories = list(new_probs.keys())
            probs = list(new_probs.values())
            drifted_df[col] = np.random.choice(categories, size=len(drifted_df), p=probs)
    
    # Apply text length shifts
    for col, multiplier in drift_config.get("text_length_shift", {}).items():
        if col in drifted_df.columns:
            texts = drifted_df[col].astype(str)
            words = ["error", "success", "warning", "info", "debug", "critical", "request", "response", "timeout", "retry"]
            new_texts = []
            for text in texts:
                words_list = text.split()
                new_length = int(len(words_list) * multiplier)
                new_length = max(1, new_length)
                # Add some new words to simulate vocabulary shift
                new_text = " ".join(np.random.choice(words, size=new_length))
                new_texts.append(new_text)
            drifted_df[col] = new_texts
    
    return drifted_df


def generate_demo_data(
    output_dir: str = "data",
    n_samples: int = 1000,
    seed: int = 42
) -> None:
    """
    Generate demo reference and current datasets with drift.
    
    Args:
        output_dir: Output directory
        n_samples: Number of samples
        seed: Random seed
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate baseline
    ref_df = generate_baseline_dataset(n_samples=n_samples, seed=seed)
    
    # Generate drifted current dataset
    cur_df = generate_drifted_dataset(ref_df, seed=seed + 1)
    
    # Save
    ref_path = output_path / "reference" / "ref.csv"
    cur_path = output_path / "current" / "cur.csv"
    
    ref_path.parent.mkdir(parents=True, exist_ok=True)
    cur_path.parent.mkdir(parents=True, exist_ok=True)
    
    ref_df.to_csv(ref_path, index=False)
    cur_df.to_csv(cur_path, index=False)
    
    print(f"Generated reference dataset: {ref_path}")
    print(f"Generated current dataset: {cur_path}")
    print(f"Reference shape: {ref_df.shape}")
    print(f"Current shape: {cur_df.shape}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate synthetic drift data")
    parser.add_argument("--output-dir", default="data", help="Output directory")
    parser.add_argument("--n-samples", type=int, default=1000, help="Number of samples")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    
    args = parser.parse_args()
    generate_demo_data(args.output_dir, args.n_samples, args.seed)

