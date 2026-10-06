"""Unit tests for 16-stage orchestrator pipeline and conversational drill-down engine."""

import os
import pytest
from warehouse.generator import SyntheticWarehouseGenerator
from core.orchestrator.pipeline import AgenticBIPipeline
from core.orchestrator.drilldown import ConversationalDrillDownEngine
from core.orchestrator.context import StageName, StageStatus


@pytest.fixture(scope="module")
def shared_db(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("orch_test")
    db_path = os.path.join(tmp_dir, "test_warehouse.duckdb")
    gen = SyntheticWarehouseGenerator(seed=42)
    gen.seed_duckdb(db_path)
    return db_path


def test_16_stage_pipeline_execution(shared_db):
    pipeline = AgenticBIPipeline(db_path=shared_db)
    recorded_stages = []

    def on_event(evt):
        recorded_stages.append(evt.stage)

    result = pipeline.execute(
        "Which products lost the most customers in Kerala during Q2?",
        event_callback=on_event,
    )

    assert result.status == "SUCCESS"
    assert not result.is_refusal
    assert "Enterprise Suite Pro" in result.evidence_backed_answer
    assert "[EVD-KL-Q2-CHURN]" in result.evidence_backed_answer
    assert result.confidence_breakdown is not None
    assert result.confidence_breakdown.overall_confidence > 0.70
    assert len(result.visualizations) > 0

    # Verify key stages ran
    assert StageName.QUESTION in recorded_stages
    assert StageName.PLANNER in recorded_stages
    assert StageName.SCHEMA_DISCOVERY in recorded_stages
    assert StageName.SEMANTIC_GROUNDING in recorded_stages
    assert StageName.SQL_GENERATION in recorded_stages
    assert StageName.SQL_VALIDATION in recorded_stages
    assert StageName.QUERY_COST_OPTIMIZATION in recorded_stages
    assert StageName.DATABASE_EXECUTION in recorded_stages
    assert StageName.DATA_PROFILING in recorded_stages
    assert StageName.SEGMENTATION in recorded_stages
    assert StageName.VISUALIZATION in recorded_stages
    assert StageName.INSIGHT_GENERATION in recorded_stages
    assert StageName.COUNTERARGUMENT in recorded_stages
    assert StageName.VERIFICATION in recorded_stages
    assert StageName.EVIDENCE_BACKED_ANSWER in recorded_stages


def test_conversational_multi_turn_drilldowns(shared_db):
    engine = ConversationalDrillDownEngine(db_path=shared_db)

    # Turn 1: Benchmark Question
    t1_res = engine.handle_turn("Which products lost the most customers in Kerala during Q2?")
    assert t1_res.status == "SUCCESS"
    assert "Enterprise Suite Pro" in t1_res.evidence_backed_answer

    # Turn 2: "Why?" Diagnostic Drill-Down
    t2_res = engine.handle_turn("Why?")
    assert t2_res.status == "SUCCESS"
    assert "logistics delivery latency" in t2_res.evidence_backed_answer.lower()
    assert "Welch t-test" in t2_res.evidence_backed_answer
    assert "[EVD-KL-Q2-LATENCY-SPIKE]" in t2_res.evidence_backed_answer

    # Turn 3: "What should we do?" Prescriptive Drill-Down
    t3_res = engine.handle_turn("What should we do?")
    assert t3_res.status == "SUCCESS"
    assert "Observed Evidence" in t3_res.evidence_backed_answer
    assert "Model Predictions" in t3_res.evidence_backed_answer
    assert "Causal Assumptions" in t3_res.evidence_backed_answer
    assert "Actionable Recommendation" in t3_res.evidence_backed_answer
    assert t3_res.review_packet is not None
    assert t3_res.review_packet.estimated_cost == 35000.0


def test_pipeline_refusal_on_unsupported_domain(shared_db):
    pipeline = AgenticBIPipeline(db_path=shared_db)
    result = pipeline.execute("How did political elections in Kerala affect product churn in Q2?")

    assert result.status == "REFUSED"
    assert result.is_refusal
    assert result.refusal_data is not None
    assert "strictly refuses" in result.evidence_backed_answer
    assert len(result.refusal_data.missing_requirements) > 0
