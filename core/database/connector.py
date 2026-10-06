"""Abstract Database Connector with read-only enforcement and cryptographic dataset hashing."""

from __future__ import annotations

import abc
import hashlib
import json
import re
from typing import Any, Dict, List, Optional
import pandas as pd


class DatabaseConnector(abc.ABC):
    """Abstract base connector for read-only analytical query execution."""

    MUTATING_KEYWORDS = [
        r"\bDROP\b",
        r"\bDELETE\b",
        r"\bUPDATE\b",
        r"\bINSERT\b",
        r"\bALTER\b",
        r"\bTRUNCATE\b",
        r"\bCREATE\b",
        r"\bREPLACE\b",
        r"\bGRANT\b",
        r"\bREVOKE\b",
    ]

    def validate_read_only(self, sql: str) -> None:
        """Enforces that SQL contains strictly non-mutating statements."""
        cleaned_sql = re.sub(r"--.*$", "", sql, flags=re.MULTILINE)
        cleaned_sql = re.sub(r"/\*.*?\*/", "", cleaned_sql, flags=re.DOTALL).strip()

        for pattern in self.MUTATING_KEYWORDS:
            if re.search(pattern, cleaned_sql, re.IGNORECASE):
                matched = re.search(pattern, cleaned_sql, re.IGNORECASE).group(0)
                raise PermissionError(
                    f"Mutating SQL keyword '{matched}' is strictly forbidden in read-only analytical mode."
                )

    @staticmethod
    def compute_dataset_hash(df: pd.DataFrame) -> str:
        """Computes a deterministic SHA-256 hash of the dataframe contents for evidence lineage."""
        if df.empty:
            return hashlib.sha256(b"EMPTY_DATAFRAME").hexdigest()

        # Sort columns to maintain deterministic column ordering
        sorted_cols = sorted(df.columns.tolist())
        normalized_df = df[sorted_cols].copy()
        
        # Serialize values into consistent JSON-like byte representation
        data_bytes = normalized_df.to_json(orient="records", date_format="iso").encode("utf-8")
        return hashlib.sha256(data_bytes).hexdigest()

    @abc.abstractmethod
    def execute_query(self, sql: str, timeout_sec: int = 30) -> pd.DataFrame:
        """Executes a validated read-only SQL query and returns a pandas DataFrame."""
        pass

    @abc.abstractmethod
    def explain_query(self, sql: str) -> Dict[str, Any]:
        """Runs EXPLAIN query to inspect cost and execution plan."""
        pass

    @abc.abstractmethod
    def get_schema_metadata(self) -> Dict[str, List[str]]:
        """Returns mapping of table names to column names."""
        pass
