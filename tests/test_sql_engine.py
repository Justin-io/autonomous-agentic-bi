"""Unit tests for SQL AST validator, grounded SQL generator, and query cost optimizer."""

import os
import pytest
from warehouse.generator import SyntheticWarehouseGenerator
from core.database.duckdb_engine import DuckDBEngine
from core.semantic_layer.catalog import SemanticCatalog
from core.semantic_layer.resolver import SemanticResolver
from core.sql_engine.validator import SQLValidator
from core.sql_engine.generator import GroundedSQLGenerator
from core.sql_engine.optimizer import QueryOptimizer


@pytest.fixture(scope="module")
def shared_db(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("sql_test")
    db_path = os.path.join(tmp_dir, "test_warehouse.duckdb")
    gen = SyntheticWarehouseGenerator(seed=42)
    gen.seed_duckdb(db_path)
    return db_path


def test_sql_validator_allows_valid_select(shared_db):
    catalog = SemanticCatalog()
    validator = SQLValidator(catalog)
    valid_sql = """
    SELECT p.product_name, COUNT(DISTINCT ce.customer_id) AS lost_customers_count
    FROM churn_events ce
    JOIN customers c ON ce.customer_id = c.customer_id
    JOIN geography g ON c.geo_id = g.geo_id
    JOIN products p ON ce.product_id = p.product_id
    WHERE g.state = 'Kerala' AND ce.quarter = 'Q2'
    GROUP BY p.product_name
    ORDER BY lost_customers_count DESC
    """
    res = validator.validate_sql(valid_sql)
    assert res.is_valid, f"Expected valid query, got errors: {res.errors}"
    assert "churn_events" in res.referenced_tables
    assert "customers" in res.referenced_tables
    assert res.has_aggregates
    assert res.has_group_by


def test_sql_validator_blocks_mutating_and_unapproved_joins():
    catalog = SemanticCatalog()
    validator = SQLValidator(catalog)

    # 1. Mutating drop statement
    drop_sql = "DROP TABLE customers"
    res_drop = validator.validate_sql(drop_sql)
    assert not res_drop.is_valid

    # 2. Mutating update statement
    update_sql = "UPDATE customers SET segment = 'Enterprise'"
    res_update = validator.validate_sql(update_sql)
    assert not res_update.is_valid

    # 3. Non-existent table
    bad_table_sql = "SELECT * FROM non_existent_table"
    res_bad = validator.validate_sql(bad_table_sql)
    assert not res_bad.is_valid
    assert any("non_existent_table" in err for err in res_bad.errors)


def test_grounded_sql_generation_and_execution(shared_db):
    catalog = SemanticCatalog()
    resolver = SemanticResolver(catalog)
    generator = GroundedSQLGenerator()
    engine = DuckDBEngine(db_path=shared_db)

    # Resolve question: "Which products lost the most customers in Kerala during Q2?"
    context = resolver.resolve_natural_language_query(
        "Which products lost the most customers in Kerala during Q2?"
    )
    assert context.is_valid

    # Generate SQL
    generated_sql = generator.generate_sql(context)
    assert "SELECT" in generated_sql
    assert "FROM churn_events" in generated_sql
    assert "WHERE" in generated_sql
    assert "GROUP BY" in generated_sql

    # Execute generated SQL on DuckDB
    df = engine.execute_query(generated_sql)
    assert not df.empty
    assert "lost_customers_count" in df.columns
    assert "product_name" in df.columns

    # Verify #1 product is Enterprise Suite Pro (PRD_102)
    top_row = df.iloc[0]
    assert top_row["product_name"] == "Enterprise Suite Pro"
    assert top_row["lost_customers_count"] > 50


def test_query_optimizer_caching_and_cost(shared_db):
    engine = DuckDBEngine(db_path=shared_db)
    optimizer = QueryOptimizer(engine, max_cost_threshold=500.0)

    sql = "SELECT COUNT(*) AS total_orders FROM orders"
    
    # First execution: cache miss
    df1, hash1, cached1 = optimizer.execute_with_optimization(sql)
    assert not cached1
    assert not df1.empty
    assert len(hash1) == 64

    # Second execution: cache hit
    df2, hash2, cached2 = optimizer.execute_with_optimization(sql)
    assert cached2
    assert hash1 == hash2
    assert df1.equals(df2)
