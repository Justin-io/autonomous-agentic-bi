"""Multi-factor calibrated confidence estimator for analytical claims and findings."""

from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel


class ConfidenceBreakdown(BaseModel):
    statistical_score: float  # weight: 0.35
    sample_size_score: float   # weight: 0.25
    semantic_score: float      # weight: 0.20
    data_quality_score: float  # weight: 0.20
    overall_confidence: float  # 0.0 to 1.0
    confidence_tier: str       # VERY_HIGH (>=0.85), HIGH (>=0.70), MEDIUM (>=0.50), LOW (<0.50)


class ConfidenceEstimator:
    """Computes a calibrated confidence score weighting inferential validity and telemetry hygiene."""

    W_STAT = 0.35
    W_SAMPLE = 0.25
    W_SEMANTIC = 0.20
    W_QUALITY = 0.20

    @classmethod
    def estimate_confidence(
        cls,
        p_value: Optional[float] = None,
        sample_size: int = 100,
        semantic_grounding_valid: bool = True,
        null_percentage: float = 0.0,
    ) -> ConfidenceBreakdown:
        # 1. Statistical significance score
        if p_value is not None:
            if p_value < 0.001:
                stat_score = 1.0
            elif p_value < 0.01:
                stat_score = 0.90
            elif p_value < 0.05:
                stat_score = 0.80
            else:
                stat_score = max(0.1, 1.0 - p_value)
        else:
            stat_score = 0.85  # Default descriptive analysis score

        # 2. Sample size score (scales towards 1.0 at N >= 50)
        sample_score = min(1.0, max(0.1, sample_size / 50.0))

        # 3. Semantic grounding score
        sem_score = 1.0 if semantic_grounding_valid else 0.2

        # 4. Data hygiene / completeness score
        quality_score = max(0.0, 1.0 - (null_percentage / 100.0))

        # Aggregate weighted score
        overall = (
            cls.W_STAT * stat_score
            + cls.W_SAMPLE * sample_score
            + cls.W_SEMANTIC * sem_score
            + cls.W_QUALITY * quality_score
        )
        overall = round(min(1.0, max(0.0, overall)), 3)

        if overall >= 0.85:
            tier = "VERY_HIGH"
        elif overall >= 0.70:
            tier = "HIGH"
        elif overall >= 0.50:
            tier = "MEDIUM"
        else:
            tier = "LOW"

        return ConfidenceBreakdown(
            statistical_score=round(stat_score, 3),
            sample_size_score=round(sample_score, 3),
            semantic_score=round(sem_score, 3),
            data_quality_score=round(quality_score, 3),
            overall_confidence=overall,
            confidence_tier=tier,
        )
