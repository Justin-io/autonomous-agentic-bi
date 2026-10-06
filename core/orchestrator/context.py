"""16-Stage Pipeline state, telemetry models, and execution context."""

from __future__ import annotations

import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from core.counterargument.confidence import ConfidenceBreakdown
from core.counterargument.critic import CriticAuditReport
from core.counterargument.sufficiency import RefusalResult
from core.hitl.manager import ReviewPacket
from core.visuals.generator import PlotlyChartSpec


class StageName(str, Enum):
    QUESTION = "QUESTION"
    PLANNER = "PLANNER"
    SCHEMA_DISCOVERY = "SCHEMA_DISCOVERY"
    SEMANTIC_GROUNDING = "SEMANTIC_GROUNDING"
    SQL_GENERATION = "SQL_GENERATION"
    SQL_VALIDATION = "SQL_VALIDATION"
    QUERY_COST_OPTIMIZATION = "QUERY_COST_OPTIMIZATION"
    DATABASE_EXECUTION = "DATABASE_EXECUTION"
    DATA_PROFILING = "DATA_PROFILING"
    STATISTICAL_ANALYSIS = "STATISTICAL_ANALYSIS"
    SEGMENTATION = "SEGMENTATION"
    VISUALIZATION = "VISUALIZATION"
    INSIGHT_GENERATION = "INSIGHT_GENERATION"
    COUNTERARGUMENT = "COUNTERARGUMENT"
    VERIFICATION = "VERIFICATION"
    EVIDENCE_BACKED_ANSWER = "EVIDENCE_BACKED_ANSWER"


class StageStatus(str, Enum):
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUSED = "REFUSED"


class StageTelemetryEvent(BaseModel):
    stage: StageName
    status: StageStatus
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    payload: Dict[str, Any] = Field(default_factory=dict)
    elapsed_ms: float = 0.0


class AgenticPipelineResult(BaseModel):
    query: str
    status: str  # SUCCESS, REFUSED, FAILED
    is_refusal: bool = False
    refusal_data: Optional[RefusalResult] = None
    evidence_backed_answer: str
    generated_sql: Optional[str] = None
    dataset_hash: Optional[str] = None
    row_count: int = 0
    data_table: List[Dict[str, Any]] = Field(default_factory=list)
    visualizations: List[PlotlyChartSpec] = Field(default_factory=list)
    confidence_breakdown: Optional[ConfidenceBreakdown] = None
    audit_report: Optional[CriticAuditReport] = None
    review_packet: Optional[ReviewPacket] = None
    telemetry_events: List[StageTelemetryEvent] = Field(default_factory=list)
    execution_time_ms: float = 0.0
