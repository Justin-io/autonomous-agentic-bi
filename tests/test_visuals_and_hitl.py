"""Unit tests for Plotly visualization generation and Human-in-the-Loop review manager."""

import pytest
import pandas as pd
from core.visuals.generator import VisualsGenerator
from core.hitl.manager import HITLManager, HITLStatus


def test_visuals_generator_bar_and_line_charts():
    df = pd.DataFrame({
        "product_name": ["Enterprise Suite Pro", "Cloud Storage Starter"],
        "lost_customers_count": [67, 3],
    })

    bar_chart = VisualsGenerator.generate_product_churn_bar_chart(df)
    assert bar_chart.chart_type == "bar"
    assert "Enterprise Suite Pro" in bar_chart.figure_json["data"][0]["x"]
    assert bar_chart.figure_json["data"][0]["y"] == [67, 3]

    line_chart = VisualsGenerator.generate_delivery_latency_trend_chart(
        quarters=["Q1", "Q2", "Q3"],
        latencies=[2.81, 11.73, 2.81],
    )
    assert line_chart.chart_type == "line"
    assert line_chart.figure_json["data"][0]["x"] == ["Q1", "Q2", "Q3"]


def test_hitl_manager_workflow():
    manager = HITLManager()

    # Cost below threshold: no trigger
    assert not manager.should_trigger_review(10000.0, is_strategic_contract=False)

    # Cost >= $25,000: triggers review
    assert manager.should_trigger_review(35000.0, is_strategic_contract=False)

    packet = manager.create_review_packet(
        packet_id="PKT-TEST-001",
        question="What should we do?",
        proposed_recommendation="Renegotiate carrier SLA",
        estimated_cost=35000.0,
        estimated_roi_percentage=680.0,
        causal_assumptions=["Logistics caused churn"],
        evidence_ids=["EVD-01"],
    )
    assert packet.status == HITLStatus.PENDING

    # Submit human decision
    updated = manager.submit_decision(
        packet_id="PKT-TEST-001",
        decision=HITLStatus.APPROVED,
        comments="Approved by VP Operations",
    )
    assert updated.status == HITLStatus.APPROVED
    assert updated.reviewer_comments == "Approved by VP Operations"
    assert updated.decided_at is not None
