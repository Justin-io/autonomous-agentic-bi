"""Unit tests for profiling, inferential stats, shift-share segmentation, and scenario forecasting."""

import os
import pytest
import pandas as pd
from warehouse.generator import SyntheticWarehouseGenerator
from core.database.duckdb_engine import DuckDBEngine
from core.statistics.profiler import DataProfiler
from core.statistics.inferential import InferentialStats
from core.statistics.segmentation import SegmentationEngine
from core.statistics.forecasting import ForecastingEngine


@pytest.fixture(scope="module")
def prepared_db(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("stats_test")
    db_path = os.path.join(tmp_dir, "test_warehouse.duckdb")
    gen = SyntheticWarehouseGenerator(seed=42)
    gen.seed_duckdb(db_path)
    return db_path


def test_data_profiler(prepared_db):
    engine = DuckDBEngine(db_path=prepared_db)
    df = engine.execute_query("SELECT * FROM customers")
    profile = DataProfiler.profile_dataframe(df, dataset_hash="dummy_hash")

    assert profile.row_count == 1000
    assert profile.column_count == 5
    assert "customer_id" in profile.columns
    assert "segment" in profile.columns
    assert profile.columns["segment"].null_percentage == 0.0


def test_inferential_stats_kerala_delivery_delay(prepared_db):
    engine = DuckDBEngine(db_path=prepared_db)
    # Get Q2 delivery days for Kerala vs Q1
    sql = """
    SELECT o.quarter, o.delivery_days
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN geography g ON c.geo_id = g.geo_id
    WHERE g.state = 'Kerala'
    """
    df = engine.execute_query(sql)

    q2_days = df[df["quarter"] == "Q2"]["delivery_days"].tolist()
    q1_days = df[df["quarter"] == "Q1"]["delivery_days"].tolist()

    res = InferentialStats.compare_groups(q2_days, q1_days, metric_name="delivery_days")

    assert res.is_statistically_significant
    assert res.p_value < 0.001
    assert res.mean_treatment > 10.0  # Q2 is ~11.8 days
    assert res.mean_control < 4.0     # Q1 is ~2.8 days
    assert res.effect_size_interpretation == "Large"
    assert res.effect_size_cohens_d > 2.0


def test_segmentation_shift_share(prepared_db):
    engine = DuckDBEngine(db_path=prepared_db)
    # Kerala churn across products
    sql = """
    SELECT p.product_name, COUNT(DISTINCT ce.customer_id) AS lost_customers_count
    FROM churn_events ce
    JOIN customers c ON ce.customer_id = c.customer_id
    JOIN geography g ON c.geo_id = g.geo_id
    JOIN products p ON ce.product_id = p.product_id
    WHERE g.state = 'Kerala' AND ce.quarter = 'Q2'
    GROUP BY p.product_name
    """
    df = engine.execute_query(sql)
    shares = SegmentationEngine.compute_distribution_share(df, "product_name", "lost_customers_count")

    assert len(shares) > 0
    top_share = shares[0]
    assert top_share.dimension_value == "Enterprise Suite Pro"
    # Enterprise Suite Pro must drive > 60% of all customer loss
    assert top_share.contribution_percentage > 60.0


def test_forecasting_and_scenarios():
    scenarios = ForecastingEngine.evaluate_interventions(
        baseline_churn_rate=0.08,
        churn_volume=67,
        arpu=499.0,
    )
    assert len(scenarios) == 3
    rec = next(s for s in scenarios if "Logistics Partner" in s.scenario_name)
    assert rec.predicted_metric_value < 20  # Dramatic drop in predicted churn
    assert len(rec.causal_assumptions) >= 2
    assert rec.estimated_roi_percentage > 0.0
