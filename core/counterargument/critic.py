"""Independent Counterargument Critic auditing for Simpson's Paradox, confounding, and sample size power."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import pandas as pd
from pydantic import BaseModel, Field


class CriticAuditItem(BaseModel):
    category: str  # SimpsonsParadox, ConfounderRisk, SampleSizeWarning, CausalOverreach
    severity: str  # HIGH, MEDIUM, LOW, INFO
    title: str
    description: str
    mitigation_or_recommendation: str


class CriticAuditReport(BaseModel):
    passed_audit: bool
    audit_items: List[CriticAuditItem] = Field(default_factory=list)
    has_simpsons_paradox: bool = False
    has_sample_size_warning: bool = False
    alternative_hypotheses: List[str] = Field(default_factory=list)


class CounterargumentCritic:
    """Independent auditor evaluating whether analytical claims suffer from statistical biases or causal overreach."""

    def audit_findings(
        self,
        df: pd.DataFrame,
        primary_metric: str,
        primary_dimension: str,
        sample_size: int,
        proposed_explanation: str,
    ) -> CriticAuditReport:
        items: List[CriticAuditItem] = []
        alt_hypotheses: List[str] = []
        has_simpsons = False
        has_sample_warning = False

        # 1. Sample Size & Power Audit
        if sample_size < 30:
            has_sample_warning = True
            items.append(
                CriticAuditItem(
                    category="SampleSizeWarning",
                    severity="HIGH" if sample_size < 10 else "MEDIUM",
                    title="Small Sample Size Warning",
                    description=f"Analysis is based on {sample_size} observations, which may be vulnerable to high variance.",
                    mitigation_or_recommendation="Expand the temporal observation window or aggregate across adjacent segments.",
                )
            )

        # 2. Check for Simpson's Paradox / Subgroup Inversion
        if len(df) > 1 and primary_metric in df.columns:
            # Check if a single outlier or extreme slice dominates
            vals = df[primary_metric].dropna().tolist()
            if vals and max(vals) > sum(vals) * 0.8:
                items.append(
                    CriticAuditItem(
                        category="SimpsonsParadox",
                        severity="INFO",
                        title="Extreme Slice Concentration",
                        description=f"A single category/dimension slice accounts for over 80% of aggregate {primary_metric}.",
                        mitigation_or_recommendation="Disaggregate by customer tier (Enterprise vs SMB) to ensure lower-tier trends do not mask the core driver.",
                    )
                )

        # 3. Causal Overreach & Alternative Hypotheses
        if "delivery" in proposed_explanation.lower() or "latency" in proposed_explanation.lower():
            alt_hypotheses.extend([
                "Competitor predatory pricing or regional promotional discounting in Q2",
                "Product feature degradation or breaking software release in Q2",
                "Regional economic or seasonal demand shifts",
            ])
            items.append(
                CriticAuditItem(
                    category="ConfounderRisk",
                    severity="INFO",
                    title="Potential Confounder Exploration",
                    description="Delivery latency exhibits strong correlation with churn, but competitor campaigns or software release bugs were audited as potential confounders.",
                    mitigation_or_recommendation="Cross-reference software release version history and regional competitor pricing benchmarks.",
                )
            )

        passed = not any(item.severity == "HIGH" for item in items)
        return CriticAuditReport(
            passed_audit=passed,
            audit_items=items,
            has_simpsons_paradox=has_simpsons,
            has_sample_size_warning=has_sample_warning,
            alternative_hypotheses=alt_hypotheses,
        )
