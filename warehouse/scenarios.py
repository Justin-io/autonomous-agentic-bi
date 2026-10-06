"""Ground-truth verification queries for benchmark business scenarios."""

from __future__ import annotations

from typing import Any, Dict, List
import duckdb


def verify_kerala_q2_product_churn(con: duckdb.DuckDBPyConnection) -> List[Dict[str, Any]]:
    """Query verifying which products lost the most customers in Kerala during Q2."""
    sql = """
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        COUNT(DISTINCT c.customer_id) AS lost_customers_count
    FROM churn_events ce
    JOIN customers c ON ce.customer_id = c.customer_id
    JOIN geography g ON c.geo_id = g.geo_id
    JOIN products p ON ce.product_id = p.product_id
    WHERE g.state = 'Kerala'
      AND ce.quarter = 'Q2'
    GROUP BY p.product_id, p.product_name, p.category
    ORDER BY lost_customers_count DESC
    """
    df = con.execute(sql).df()
    return df.to_dict(orient="records")


def verify_kerala_delivery_latency_anomaly(con: duckdb.DuckDBPyConnection) -> List[Dict[str, Any]]:
    """Query verifying the delivery days anomaly in Kerala during Q2 vs baseline."""
    sql = """
    SELECT 
        g.state,
        o.quarter,
        ROUND(AVG(o.delivery_days), 2) AS avg_delivery_days,
        COUNT(o.order_id) AS order_volume
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN geography g ON c.geo_id = g.geo_id
    WHERE g.state = 'Kerala'
    GROUP BY g.state, o.quarter
    ORDER BY o.quarter
    """
    df = con.execute(sql).df()
    return df.to_dict(orient="records")
