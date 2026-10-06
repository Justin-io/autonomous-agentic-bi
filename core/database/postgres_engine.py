"""PostgreSQL-compatible warehouse connector with read-only enforcement."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
import pandas as pd
from core.database.connector import DatabaseConnector


class PostgresEngine(DatabaseConnector):
    """PostgreSQL warehouse connector enforcing read-only transactions."""

    def __init__(self, connection_url: Optional[str] = None):
        self.connection_url = connection_url or os.environ.get(
            "DATABASE_URL", "postgresql://dev:dev@localhost:5432/agentic_bi"
        )

    def execute_query(self, sql: str, timeout_sec: int = 30) -> pd.DataFrame:
        """Executes read-only SQL query against PostgreSQL."""
        self.validate_read_only(sql)
        try:
            import psycopg2  # type: ignore
            import psycopg2.extras  # type: ignore

            conn = psycopg2.connect(self.connection_url)
            conn.set_session(readonly=True, autocommit=True)
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(f"SET statement_timeout = {timeout_sec * 1000};")
            cursor.execute(sql)
            rows = cursor.fetchall()
            df = pd.DataFrame(rows)
            cursor.close()
            conn.close()
            return df
        except ImportError:
            # Fallback mock for local environments without psycopg2
            raise RuntimeError("psycopg2 is not installed or PostgreSQL connection is unavailable.")
        except Exception as e:
            raise RuntimeError(f"PostgreSQL execution error: {str(e)}") from e

    def explain_query(self, sql: str) -> Dict[str, Any]:
        """Runs EXPLAIN (ANALYZE, FORMAT JSON) on PostgreSQL."""
        self.validate_read_only(sql)
        try:
            import psycopg2  # type: ignore

            conn = psycopg2.connect(self.connection_url)
            conn.set_session(readonly=True)
            cursor = conn.cursor()
            cursor.execute(f"EXPLAIN (FORMAT JSON) {sql}")
            plan = cursor.fetchall()
            cursor.close()
            conn.close()
            return {
                "engine": "postgresql",
                "plan": plan,
                "estimated_cost_units": 100.0,
            }
        except Exception as e:
            return {
                "engine": "postgresql",
                "error": str(e),
                "estimated_cost_units": 999.0,
            }

    def get_schema_metadata(self) -> Dict[str, List[str]]:
        """Queries information_schema for tables and columns."""
        try:
            import psycopg2  # type: ignore

            conn = psycopg2.connect(self.connection_url)
            conn.set_session(readonly=True)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT table_name, column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
            """
            )
            rows = cursor.fetchall()
            schema: Dict[str, List[str]] = {}
            for table_name, column_name in rows:
                if table_name not in schema:
                    schema[table_name] = []
                schema[table_name].append(column_name)
            cursor.close()
            conn.close()
            return schema
        except Exception:
            return {}
