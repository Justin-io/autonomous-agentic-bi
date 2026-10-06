"""Unit tests for database connectors and safety mechanisms."""

import os
import pytest
import pandas as pd
from warehouse.generator import SyntheticWarehouseGenerator
from core.database.connector import DatabaseConnector
from core.database.duckdb_engine import DuckDBEngine


@pytest.fixture(scope="module")
def prepared_db(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("db")
    db_path = os.path.join(tmp_dir, "test_engine.duckdb")
    gen = SyntheticWarehouseGenerator(seed=42)
    gen.seed_duckdb(db_path)
    return db_path


def test_duckdb_read_only_safety(prepared_db):
    engine = DuckDBEngine(db_path=prepared_db)

    # Valid SELECT query
    df = engine.execute_query("SELECT COUNT(*) AS total_customers FROM customers")
    assert not df.empty
    assert df["total_customers"].iloc[0] == 1000

    # Attempt mutating operations should raise PermissionError
    mutating_queries = [
        "DROP TABLE customers",
        "DELETE FROM customers WHERE customer_id = 'CUST_0001'",
        "UPDATE customers SET segment = 'Enterprise'",
        "INSERT INTO customers VALUES ('CUST_9999', 'Fake', 'GEO_01', 'SMB', '2024-01-01')",
        "TRUNCATE TABLE orders",
        "ALTER TABLE products ADD COLUMN discount FLOAT",
    ]
    for bad_sql in mutating_queries:
        with pytest.raises(PermissionError):
            engine.execute_query(bad_sql)


def test_sha256_dataset_hashing():
    df1 = pd.DataFrame({"col_a": [1, 2, 3], "col_b": ["x", "y", "z"]})
    df2 = pd.DataFrame({"col_b": ["x", "y", "z"], "col_a": [1, 2, 3]})  # Column order inverted
    df3 = pd.DataFrame({"col_a": [1, 2, 4], "col_b": ["x", "y", "z"]})  # Different data

    hash1 = DatabaseConnector.compute_dataset_hash(df1)
    hash2 = DatabaseConnector.compute_dataset_hash(df2)
    hash3 = DatabaseConnector.compute_dataset_hash(df3)

    assert isinstance(hash1, str) and len(hash1) == 64
    assert hash1 == hash2, "Dataset hash should be invariant to column ordering"
    assert hash1 != hash3, "Dataset hash should change when data values change"


def test_explain_query_duckdb(prepared_db):
    engine = DuckDBEngine(db_path=prepared_db)
    explain_res = engine.explain_query("SELECT * FROM customers JOIN geography ON customers.geo_id = geography.geo_id")
    assert "plan_text" in explain_res
    assert explain_res["estimated_cost_units"] > 0
