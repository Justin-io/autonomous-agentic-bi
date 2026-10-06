"""DuckDB analytical engine connector with read-only guarantees."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
import duckdb
import pandas as pd
from core.database.connector import DatabaseConnector


class DuckDBEngine(DatabaseConnector):
    """High-performance columnar DuckDB connector for fast analytical queries."""

    def __init__(self, db_path: str = "data/warehouse.duckdb", read_only: bool = True):
        self.db_path = db_path
        self.read_only = read_only
        self._con: Optional[duckdb.DuckDBPyConnection] = None

    def _get_connection(self) -> duckdb.DuckDBPyConnection:
        if self._con is None:
            if os.path.exists(self.db_path):
                self._con = duckdb.connect(self.db_path, read_only=self.read_only)
            else:
                # In-memory connection if file doesn't exist yet
                self._con = duckdb.connect(":memory:")
        return self._con

    def execute_query(self, sql: str, timeout_sec: int = 30) -> pd.DataFrame:
        """Executes read-only SQL query against DuckDB."""
        self.validate_read_only(sql)
        con = self._get_connection()
        try:
            rel = con.execute(sql)
            return rel.df()
        except Exception as e:
            raise RuntimeError(f"DuckDB execution error: {str(e)}") from e

    def explain_query(self, sql: str) -> Dict[str, Any]:
        """Inspects query plan and estimated cost via DuckDB EXPLAIN."""
        self.validate_read_only(sql)
        con = self._get_connection()
        try:
            explain_df = con.execute(f"EXPLAIN {sql}").df()
            plan_str = "\n".join(explain_df.iloc[:, 1].astype(str).tolist())
            # Basic cost heuristic from number of joins and scan nodes
            estimated_cost = len(plan_str.splitlines()) * 10.0
            return {
                "engine": "duckdb",
                "plan_text": plan_str,
                "estimated_cost_units": estimated_cost,
                "is_cached": False,
            }
        except Exception as e:
            return {
                "engine": "duckdb",
                "error": str(e),
                "estimated_cost_units": 999.0,
            }

    def get_schema_metadata(self) -> Dict[str, List[str]]:
        """Returns dictionary of table names and list of column names."""
        con = self._get_connection()
        tables = [r[0] for r in con.execute("SHOW TABLES").fetchall()]
        schema = {}
        for t in tables:
            cols = [r[1] for r in con.execute(f"PRAGMA table_info('{t}')").fetchall()]
            schema[t] = cols
        return schema

    def close(self):
        if self._con is not None:
            self._con.close()
            self._con = None
