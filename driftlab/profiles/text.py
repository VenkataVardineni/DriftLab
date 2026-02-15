"""Text drift profiling for NLP features."""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from .base import Profile

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class TextProfile(Profile):
    """Text data drift profile."""
    
    def __init__(self, text_columns: Optional[List[str]] = None, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize text profile.
        
        Args:
            text_columns: List of column names containing text data
            model_name: Sentence transformer model name
        """
        self.text_columns = text_columns
        self.model_name = model_name
        self.model = None
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
            except Exception:
                self.model = None
    
    def _compute_text_length_stats(self, texts: pd.Series) -> Dict[str, float]:
        """Compute text length statistics."""
        lengths = texts.astype(str).str.len()
        return {
            "mean_length": float(lengths.mean()),
            "std_length": float(lengths.std()),
            "min_length": float(lengths.min()),
            "max_length": float(lengths.max())
        }
    
    def _compute_vocabulary_richness(self, texts: pd.Series) -> float:
        """Compute vocabulary richness proxy (unique words / total words)."""
        all_words = set()
        total_words = 0
        for text in texts.astype(str):
            words = text.lower().split()
            all_words.update(words)
            total_words += len(words)
        
        if total_words == 0:
            return 0.0
        return len(all_words) / total_words
    
    def _compute_top_ngrams(self, texts: pd.Series, n: int = 2, top_k: int = 10) -> Dict[str, int]:
        """Compute top n-grams frequency."""
        from collections import Counter
        
        ngrams = []
        for text in texts.astype(str):
            words = text.lower().split()
            for i in range(len(words) - n + 1):
                ngram = " ".join(words[i:i+n])
                ngrams.append(ngram)
        
        counter = Counter(ngrams)
        return dict(counter.most_common(top_k))
    
    def _compute_embedding_shift(self, ref_texts: pd.Series, cur_texts: pd.Series) -> Dict[str, float]:
        """Compute embedding distribution shift."""
        if not self.model:
            return {"embedding_shift_score": 0.0, "centroid_distance": 0.0}
        
        try:
            # Sample if too large
            max_samples = 1000
            ref_sample = ref_texts.astype(str).sample(min(len(ref_texts), max_samples))
            cur_sample = cur_texts.astype(str).sample(min(len(cur_texts), max_samples))
            
            # Generate embeddings
            ref_embeddings = self.model.encode(ref_sample.tolist(), show_progress_bar=False)
            cur_embeddings = self.model.encode(cur_sample.tolist(), show_progress_bar=False)
            
            # Compute centroids
            ref_centroid = np.mean(ref_embeddings, axis=0)
            cur_centroid = np.mean(cur_embeddings, axis=0)
            
            # Compute distance
            centroid_distance = float(np.linalg.norm(ref_centroid - cur_centroid))
            
            # Compute variance shift
            ref_variance = float(np.var(ref_embeddings))
            cur_variance = float(np.var(cur_embeddings))
            variance_shift = abs(ref_variance - cur_variance) / (ref_variance + 1e-8)
            
            # Combined shift score
            shift_score = centroid_distance * (1 + variance_shift)
            
            return {
                "embedding_shift_score": shift_score,
                "centroid_distance": centroid_distance,
                "variance_shift": variance_shift
            }
        except Exception as e:
            return {"embedding_shift_score": 0.0, "error": str(e)}
    
    def run(self, reference_df: pd.DataFrame, current_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Run text drift analysis.
        
        Returns:
            {
                "metrics": {...},
                "artifacts": {...}
            }
        """
        metrics = {}
        artifacts = {}
        
        # Find text columns
        if self.text_columns is None:
            # Auto-detect text columns (string type with high cardinality)
            text_cols = []
            for col in reference_df.columns:
                if reference_df[col].dtype == 'object':
                    unique_ratio = reference_df[col].nunique() / len(reference_df)
                    if unique_ratio > 0.1:  # High cardinality suggests text
                        text_cols.append(col)
            self.text_columns = text_cols
        
        # Analyze each text column
        for col in self.text_columns:
            if col not in reference_df.columns or col not in current_df.columns:
                continue
            
            ref_texts = reference_df[col].dropna()
            cur_texts = current_df[col].dropna()
            
            if len(ref_texts) == 0 or len(cur_texts) == 0:
                continue
            
            # Length statistics
            ref_length_stats = self._compute_text_length_stats(ref_texts)
            cur_length_stats = self._compute_text_length_stats(cur_texts)
            length_shift = abs(ref_length_stats["mean_length"] - cur_length_stats["mean_length"]) / (ref_length_stats["mean_length"] + 1e-8)
            
            # Vocabulary richness
            ref_richness = self._compute_vocabulary_richness(ref_texts)
            cur_richness = self._compute_vocabulary_richness(cur_texts)
            richness_shift = abs(ref_richness - cur_richness)
            
            # Top n-grams shift
            ref_ngrams = self._compute_top_ngrams(ref_texts)
            cur_ngrams = self._compute_top_ngrams(cur_texts)
            ngram_overlap = len(set(ref_ngrams.keys()) & set(cur_ngrams.keys())) / max(len(set(ref_ngrams.keys()) | set(cur_ngrams.keys())), 1)
            ngram_shift = 1.0 - ngram_overlap
            
            # Embedding shift
            embedding_shift = self._compute_embedding_shift(ref_texts, cur_texts)
            
            # Combined text drift score
            text_drift_score = (
                length_shift * 0.2 +
                richness_shift * 0.2 +
                ngram_shift * 0.3 +
                (embedding_shift.get("embedding_shift_score", 0.0) / 10.0) * 0.3  # Normalize embedding shift
            )
            
            metrics[f"{col}_text_drift"] = {
                "text_drift_score": float(text_drift_score),
                "length_shift": float(length_shift),
                "richness_shift": float(richness_shift),
                "ngram_shift": float(ngram_shift),
                "embedding_shift": embedding_shift,
                "top_shifted_terms": list(set(cur_ngrams.keys()) - set(ref_ngrams.keys()))[:10]
            }
        
        return {
            "metrics": metrics,
            "artifacts": artifacts
        }

