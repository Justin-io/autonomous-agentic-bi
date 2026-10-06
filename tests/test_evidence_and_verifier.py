"""Unit tests for Cryptographic Evidence Store and Deterministic Claim Verifier."""

import pytest
from core.evidence.store import EvidenceStore
from core.evidence.verifier import ClaimVerifier


def test_evidence_registration_and_retrieval():
    store = EvidenceStore()
    record = store.register_evidence(
        evidence_id="EVD-KL-Q2-CHURN",
        dataset_hash="a1b2c3d4e5f67890123456789012345678901234567890123456789012345678",
        query_sql="SELECT * FROM churn_events",
        row_count=67,
        facts={"top_product": "Enterprise Suite Pro", "churn_count": 67},
        summary="Kerala Q2 churn breakdown by product",
    )
    assert record.evidence_id == "EVD-KL-Q2-CHURN"
    assert record.row_count == 67
    assert store.get_evidence("EVD-KL-Q2-CHURN") is not None


def test_claim_verifier_accepts_grounded_citations():
    store = EvidenceStore()
    store.register_evidence(
        evidence_id="EVD-KL-Q2-CHURN",
        dataset_hash="dummy_hash_64_chars_long_000000000000000000000000000000000000000000",
        query_sql="SELECT * FROM churn_events",
        row_count=67,
        facts={"churn_count": 67},
        summary="Kerala churn",
    )
    verifier = ClaimVerifier(store)

    text = "In Kerala during Q2, Enterprise Suite Pro lost 67 customers [EVD-KL-Q2-CHURN]."
    report = verifier.verify_answer(text)

    assert report.is_verified
    assert report.citation_count == 1
    assert "EVD-KL-Q2-CHURN" in report.found_citation_ids
    assert len(report.verification_errors) == 0


def test_claim_verifier_rejects_hallucinated_citations():
    store = EvidenceStore()
    verifier = ClaimVerifier(store)

    text = "Revenue declined by 45% [EVD-NONEXISTENT]."
    report = verifier.verify_answer(text)

    assert not report.is_verified
    assert "EVD-NONEXISTENT" in report.missing_evidence_ids
    assert len(report.verification_errors) > 0


def test_claim_verifier_flags_uncited_claims():
    store = EvidenceStore()
    verifier = ClaimVerifier(store)

    text = "Customer churn surged to 85% in the region."
    report = verifier.verify_answer(text)

    assert not report.is_verified
    assert len(report.uncited_numbers) > 0
