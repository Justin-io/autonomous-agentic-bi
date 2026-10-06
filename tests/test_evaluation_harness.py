"""Unit test running the full benchmark evaluation suite."""

import os
import pytest
from warehouse.generator import SyntheticWarehouseGenerator
from eval.harness import EvaluationHarness


@pytest.fixture(scope="module")
def prepared_eval_db(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("eval_test")
    db_path = os.path.join(tmp_dir, "test_warehouse.duckdb")
    gen = SyntheticWarehouseGenerator(seed=42)
    gen.seed_duckdb(db_path)
    return db_path


def test_evaluation_harness_runs_all_benchmarks(prepared_eval_db):
    harness = EvaluationHarness(db_path=prepared_eval_db)
    report = harness.run_all_benchmarks()

    assert report.total_scenarios == 4
    assert report.successful_scenarios == 4
    assert report.overall_pass
    assert report.avg_sql_accuracy == 1.0
    assert report.avg_numerical_correctness == 1.0
    assert report.avg_citation_completeness == 1.0
    assert report.avg_hallucination_rate == 0.0
    assert report.avg_refusal_correctness == 1.0

    # Ensure every scorecard passed
    for s in report.scorecards:
        assert s.task_success, f"Scenario {s.scenario_id} failed: {s.notes}"
