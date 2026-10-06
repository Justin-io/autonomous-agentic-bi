"""Human-In-The-Loop (HITL) Review Manager for high-impact recommendations and strategic decisions."""

from __future__ import annotations

import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HITLStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"


class ReviewPacket(BaseModel):
    packet_id: str
    created_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    question: str
    proposed_recommendation: str
    estimated_cost: float
    estimated_roi_percentage: float
    causal_assumptions: List[str]
    evidence_ids: List[str]
    status: HITLStatus = HITLStatus.PENDING
    reviewer_comments: Optional[str] = None
    decided_at: Optional[str] = None


class HITLManager:
    """Manages executive human-in-the-loop sign-offs on high-impact interventions."""

    COST_THRESHOLD = 25000.0

    def __init__(self):
        self._packets: Dict[str, ReviewPacket] = {}

    def should_trigger_review(self, estimated_cost: float, is_strategic_contract: bool = True) -> bool:
        """Determines whether a recommendation exceeds automated sign-off bounds."""
        return estimated_cost >= self.COST_THRESHOLD or is_strategic_contract

    def create_review_packet(
        self,
        packet_id: str,
        question: str,
        proposed_recommendation: str,
        estimated_cost: float,
        estimated_roi_percentage: float,
        causal_assumptions: List[str],
        evidence_ids: List[str],
    ) -> ReviewPacket:
        packet = ReviewPacket(
            packet_id=packet_id,
            question=question,
            proposed_recommendation=proposed_recommendation,
            estimated_cost=estimated_cost,
            estimated_roi_percentage=estimated_roi_percentage,
            causal_assumptions=causal_assumptions,
            evidence_ids=evidence_ids,
            status=HITLStatus.PENDING,
        )
        self._packets[packet_id] = packet
        return packet

    def submit_decision(
        self,
        packet_id: str,
        decision: HITLStatus,
        comments: Optional[str] = None,
    ) -> ReviewPacket:
        packet = self._packets.get(packet_id)
        if not packet:
            raise KeyError(f"Review packet '{packet_id}' not found.")
        
        packet.status = decision
        packet.reviewer_comments = comments
        packet.decided_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return packet

    def get_packet(self, packet_id: str) -> Optional[ReviewPacket]:
        return self._packets.get(packet_id)

    def list_all(self) -> List[ReviewPacket]:
        return list(self._packets.values())
