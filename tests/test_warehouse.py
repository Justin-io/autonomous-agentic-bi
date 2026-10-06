"""Unit tests for synthetic enterprise warehouse generator and scenario ground truth."""

import os
import duckdb
import pytest
from warehouse.generator import SyntheticWarehouseGenerator
from warehouse.scenarios import (
    verify_kerala_q2_product_churn,
    verify_kerala_delivery_latency_anomaly,
)


@pytest.fixture(scope="module")
def duckdb_con(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("db")
    db_path = os.path.join(tmp_dir, "test_warehouse.duckdb")
    gen = SyntheticWarehouseGenerator(seed=42)
    con = gen.seed_duckdb(db_path)
    yield con
    con.close()


def test_warehouse_tables_exist(duckdb_con):
    tables = [
        "geography",
        "products",
        "customers",
        "orders",
        "order_items",
        "churn_events",
        "marketing_campaigns",
        "calendar_dim",
    ]
    existing = [r[0] for r in duckdb_con.execute("SHOW TABLES").fetchall()]
    for t in tables:
        assert t in existing, f"Table {t} missing from generated warehouse."


def test_kerala_q2_churn_calibrated_ground_truth(duckdb_con):
    results = verify_kerala_q2_product_churn(duckdb_con)
    assert len(results) > 0
    # Top churned product must be PRD_102 Enterprise Suite Pro
    top_product = results[0]
    assert top_product["product_id"] == "PRD_102"
    assert top_product["product_name"] == "Enterprise Suite Pro"
    assert top_product["lost_customers_count"] > 50

    # Ensure other products have significantly lower churn
    for prod in results[1:]:
        assert prod["lost_customers_count"] < 15


def test_kerala_delivery_latency_anomaly(duckdb_con):
    results = verify_kerala_delivery_latency_anomaly(duckdb_con)
    q_map = {r["quarter"]: r for r in results}
    assert "Q1" in q_map and "Q2" in q_map and "Q3" in q_map
    assert q_map["Q2"]["avg_delivery_days"] > 10.0
    assert q_map["Q1"]["avg_delivery_days"] < 4.0
    assert q_map["Q3"]["avg_delivery_days"] < 4.0
