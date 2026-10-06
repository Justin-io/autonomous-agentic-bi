"""Unit tests for the canonical semantic layer catalog and resolver."""

import pytest
from core.semantic_layer.catalog import SemanticCatalog
from core.semantic_layer.models import FilterCondition, FilterOperator
from core.semantic_layer.resolver import SemanticResolver


def test_semantic_catalog_entities_and_metrics():
    catalog = SemanticCatalog()
    # Check entities
    assert catalog.get_entity("customers") is not None
    assert catalog.get_entity("products") is not None
    assert catalog.get_entity("geography") is not None
    assert catalog.get_entity("churn_events") is not None

    # Check metrics
    m_churn = catalog.get_metric("lost_customers_count")
    assert m_churn is not None
    assert "COUNT(DISTINCT" in m_churn.sql_expression
    assert m_churn.grain == "customer_id, quarter"

    m_latency = catalog.get_metric("avg_delivery_days")
    assert m_latency is not None
    assert "AVG" in m_latency.sql_expression


def test_join_graph_path_finding():
    catalog = SemanticCatalog()
    # Direct relationship: churn_events -> customers
    path = catalog.find_join_path("churn_events", "customers")
    assert path is not None
    assert len(path) == 1
    assert path[0].to_entity == "customers"

    # Multi-hop relationship: churn_events -> customers -> geography
    path_geo = catalog.find_join_path("churn_events", "geography")
    assert path_geo is not None
    assert len(path_geo) == 2
    entities_in_path = [r.to_entity for r in path_geo]
    assert "customers" in entities_in_path
    assert "geography" in entities_in_path


def test_resolver_kerala_q2_question():
    resolver = SemanticResolver()
    ctx = resolver.resolve_natural_language_query(
        "Which products lost the most customers in Kerala during Q2?"
    )
    assert ctx.is_valid
    assert len(ctx.resolved_metrics) == 1
    assert ctx.resolved_metrics[0].name == "lost_customers_count"
    
    # Check dimension resolution
    dim_names = [d.name for d in ctx.resolved_dimensions]
    assert "product_id" in dim_names
    assert "product_name" in dim_names

    # Check filters
    filter_map = {f.dimension_name: f.value for f in ctx.plan.filters}
    assert filter_map.get("state") == "Kerala"
    assert filter_map.get("quarter") == "Q2"

    # Check join chain contains needed entities
    joined_entities = {r.to_entity for r in ctx.join_chain} | {r.from_entity for r in ctx.join_chain}
    assert "churn_events" in joined_entities
    assert "customers" in joined_entities
    assert "geography" in joined_entities
    assert "products" in joined_entities
