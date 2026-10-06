"""Query Cost Optimizer and Deterministic Cache for Analytical SQL."""

from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, Optional, Tuple
import pandas as pd
from core.database.connector import DatabaseConnector


class QueryOptimizer:
    """Evaluates query complexity, estimates cost, and maintains an in-memory execution cache."""

    def __init__(self, connector: DatabaseConnector, max_cost_threshold: float = 10000.0, cache_ttl_sec: int = 300):
        self.connector = connector
        self.max_cost_threshold = max_cost_threshold
        self.cache_ttl_sec = cache_ttl_sec
        # Cache key -> (timestamp, DataFrame, dataset_hash)
        self._cache: Dict[str, Tuple[float, pd.DataFrame, str]] = {}

    def get_query_cache_key(self, sql: str) -> str:
        """Computes a normalized SHA-256 hash for SQL statement."""
        normalized = " ".join(sql.strip().lower().split())
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def estimate_cost(self, sql: str) -> Dict[str, Any]:
        """Runs EXPLAIN and evaluates execution cost against threshold."""
        plan_info = self.connector.explain_query(sql)
        estimated_cost = plan_info.get("estimated_cost_units", 10.0)
        is_safe = estimated_cost <= self.max_cost_threshold

        return {
            "estimated_cost_units": estimated_cost,
            "max_cost_threshold": self.max_cost_threshold,
            "is_safe_to_execute": is_safe,
            "plan_details": plan_info,
        }

    def execute_with_optimization(self, sql: str) -> Tuple[pd.DataFrame, str, bool]:
        """Executes query with caching and cost guards. Returns (DataFrame, dataset_hash, is_from_cache)."""
        cache_key = self.get_query_cache_key(sql)
        now = time.time()

        # Check cache
        if cache_key in self._cache:
            ts, cached_df, cached_hash = self._cache[cache_key]
            if (now - ts) < self.cache_ttl_sec:
                return cached_df.copy(), cached_hash, True

        # Pre-execution cost check
        cost_eval = self.estimate_cost(sql)
        if not cost_eval["is_safe_to_execute"]:
            raise RuntimeError(
                f"Query rejected: Estimated cost {cost_eval['estimated_cost_units']} exceeds threshold {self.max_cost_threshold}."
            )

        # Execute query
        df = self.connector.execute_query(sql)
        dataset_hash = self.connector.compute_dataset_hash(df)

        # Store in cache
        self._cache[cache_key] = (now, df.copy(), dataset_hash)

        return df, dataset_hash, False

    def clear_cache(self):
        self._cache.clear()
