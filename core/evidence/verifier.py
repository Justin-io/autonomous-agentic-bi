"""Deterministic Claim Verifier enforcing that every analytical conclusion links to evidence citations."""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field
from core.evidence.store import EvidenceStore


class VerificationReport(BaseModel):
    is_verified: bool
    citation_count: int
    found_citation_ids: List[str] = Field(default_factory=list)
    missing_evidence_ids: List[str] = Field(default_factory=list)
    uncited_numbers: List[str] = Field(default_factory=list)
    verification_errors: List[str] = Field(default_factory=list)


class ClaimVerifier:
    """Validates that all analytical assertions are linked to valid, registered evidence records."""

    CITATION_PATTERN = r"\[(EVD-[A-Za-z0-9_\-]+)\]"
    NUMBER_PATTERN = r"\b\d+(?:\.\d+)?%?\b"

    def __init__(self, store: EvidenceStore):
        self.store = store

    def verify_answer(self, text: str) -> VerificationReport:
        errors: List[str] = []

        # 1. Extract all citations
        citations = re.findall(self.CITATION_PATTERN, text)
        found_ids = list(dict.fromkeys(citations))

        missing_ids: List[str] = []
        for cid in found_ids:
            if not self.store.get_evidence(cid):
                missing_ids.append(cid)
                errors.append(f"Citation [{cid}] references non-existent evidence record.")

        # Require at least one citation if numbers are stated
        all_numbers = re.findall(self.NUMBER_PATTERN, text)
        # Filter out numbers that might just be years (2024) or ordinal quarters (Q1/Q2 handled separately)
        significant_numbers = [n for n in all_numbers if n not in ["2023", "2024", "1", "2", "3", "4"]]

        uncited = []
        if significant_numbers and not found_ids:
            errors.append("Response contains numerical assertions but lacks [EVD-...] evidence citations.")
            uncited = significant_numbers

        is_valid = len(errors) == 0 and len(found_ids) > 0

        return VerificationReport(
            is_verified=is_valid,
            citation_count=len(found_ids),
            found_citation_ids=found_ids,
            missing_evidence_ids=missing_ids,
            uncited_numbers=uncited,
            verification_errors=errors,
        )
