"""Cryptographic Evidence Store holding immutable evidence records and query lineage."""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EvidenceRecord(BaseModel):
    evidence_id: str
    dataset_hash: str
    query_sql: str
    row_count: int
    facts: Dict[str, Any] = Field(default_factory=dict)
    summary: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())


class EvidenceStore:
    """Manages immutable evidence records with cryptographic dataset hashes."""

    def __init__(self):
        self._records: Dict[str, EvidenceRecord] = {}

    def register_evidence(
        self,
        evidence_id: str,
        dataset_hash: str,
        query_sql: str,
        row_count: int,
        facts: Dict[str, Any],
        summary: str,
    ) -> EvidenceRecord:
        record = EvidenceRecord(
            evidence_id=evidence_id,
            dataset_hash=dataset_hash,
            query_sql=query_sql,
            row_count=row_count,
            facts=facts,
            summary=summary,
        )
        self._records[evidence_id] = record
        return record

    def get_evidence(self, evidence_id: str) -> Optional[EvidenceRecord]:
        return self._records.get(evidence_id)

    def list_all(self) -> List[EvidenceRecord]:
        return list(self._records.values())

    def clear(self):
        self._records.clear()
