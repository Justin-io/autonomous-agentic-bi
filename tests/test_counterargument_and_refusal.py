"""Unit tests for Counterargument Critic, Evidence-Sufficiency Gate, and Confidence Estimator."""

import pytest
import pandas as pd
from core.counterargument.critic import CounterargumentCritic
from core.counterargument.sufficiency import EvidenceSufficiencyGate
from core.counterargument.confidence import ConfidenceEstimator


def test_evidence_sufficiency_gate_triggers_refusal():
    gate = EvidenceSufficiencyGate()

    # Question asking about political elections in Kerala
    query_unsupported = "How did political elections in Kerala affect product churn during Q2?"
    result = gate.evaluate_sufficiency(query_unsupported)

    assert result.is_refusal
    assert result.refusal_reason == "MISSING_DOMAIN_TELEMETRY"
    assert "strictly refuses" in result.explanation
    assert len(result.missing_requirements) > 0
    assert "Political" in result.missing_requirements[0].required_entity
    assert len(result.available_alternatives) > 0


def test_evidence_sufficiency_gate_allows_supported_queries():
    gate = EvidenceSufficiencyGate()
    query_supported = "Which products lost the most customers in Kerala during Q2?"
    result = gate.evaluate_sufficiency(query_supported)

    assert not result.is_refusal
    assert len(result.missing_requirements) == 0


def test_counterargument_critic_audits_bias_and_sample_size():
    critic = CounterargumentCritic()

    # Test small sample size detection
    df_small = pd.DataFrame({"product": ["A", "B"], "churn": [2, 1]})
    report_small = critic.audit_findings(
        df=df_small,
        primary_metric="churn",
        primary_dimension="product",
        sample_size=3,
        proposed_explanation="Delivery delays caused churn",
    )
    assert report_small.has_sample_size_warning
    assert any(item.category == "SampleSizeWarning" for item in report_small.audit_items)

    # Test alternative hypothesis generation
    assert len(report_small.alternative_hypotheses) > 0
    assert any("competitor" in h.lower() for h in report_small.alternative_hypotheses)


def test_confidence_estimator():
    # High confidence case: p < 0.001, N = 100, zero nulls
    breakdown_high = ConfidenceEstimator.estimate_confidence(
        p_value=0.0001,
        sample_size=100,
        semantic_grounding_valid=True,
        null_percentage=0.0,
    )
    assert breakdown_high.overall_confidence >= 0.85
    assert breakdown_high.confidence_tier == "VERY_HIGH"

    # Low confidence case: p = 0.45, N = 8, 25% nulls
    breakdown_low = ConfidenceEstimator.estimate_confidence(
        p_value=0.45,
        sample_size=8,
        semantic_grounding_valid=False,
        null_percentage=25.0,
    )
    assert breakdown_low.overall_confidence < 0.50
    assert breakdown_low.confidence_tier == "LOW"
