"""FastAPI Web Service for Autonomous Agentic BI Platform with real-time SSE telemetry."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from core.hitl.manager import HITLStatus
from core.orchestrator.context import AgenticPipelineResult, StageTelemetryEvent
from core.orchestrator.drilldown import ConversationalDrillDownEngine
from eval.harness import BenchmarkSummaryReport, EvaluationHarness
from warehouse.generator import SyntheticWarehouseGenerator

app = FastAPI(
    title="Autonomous Agentic BI & Analytics Platform",
    description="Scientific Agentic BI combining semantic grounding, SQL AST validation, shift-share decomposition, and cryptographic evidence verification.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global singleton engine initialized with DuckDB warehouse
DB_PATH = "data/warehouse.duckdb"

# Seed data if not already present
generator = SyntheticWarehouseGenerator(seed=42)
generator.seed_duckdb(DB_PATH)

drilldown_engine = ConversationalDrillDownEngine(db_path=DB_PATH)
eval_harness = EvaluationHarness(db_path=DB_PATH)


class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default_session"


class HITLDecisionRequest(BaseModel):
    packet_id: str
    decision: HITLStatus
    comments: Optional[str] = None


@app.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": "agentic_bi_platform",
        "warehouse_connected": True,
        "engine": "duckdb",
    }


@app.post("/api/chat", response_model=AgenticPipelineResult)
def chat_endpoint(req: ChatRequest):
    """Executes a business query through the 16-stage pipeline."""
    try:
        result = drilldown_engine.handle_turn(req.query)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Execution error: {str(e)}",
        )


@app.get("/api/chat/stream")
async def chat_stream_endpoint(query: str = Query(..., description="Business question")):
    """Server-Sent Events (SSE) streaming real-time stage execution telemetry."""

    async def event_generator():
        queue: asyncio.Queue = asyncio.Queue()

        def on_event(evt: StageTelemetryEvent):
            queue.put_nowait(evt)

        # Run pipeline in a background thread
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, drilldown_engine.handle_turn, query, on_event)

        while not future.done() or not queue.empty():
            try:
                evt = await asyncio.wait_for(queue.get(), timeout=0.1)
                yield f"data: {evt.model_dump_json()}\n\n"
            except asyncio.TimeoutError:
                await asyncio.sleep(0.01)

        final_result = await future
        yield f"data: {json.dumps({'stage': 'DONE', 'result': final_result.model_dump()})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/catalog")
def get_semantic_catalog():
    """Returns the canonical semantic layer definitions and allowable join graph."""
    catalog = drilldown_engine.catalog
    return {
        "entities": [e.model_dump() for e in catalog.entities.values()],
        "metrics": [m.model_dump() for m in catalog.metrics.values()],
        "dimensions": [d.model_dump() for d in catalog.dimensions.values()],
        "relationships": [r.model_dump() for r in catalog.join_graph.relationships],
    }


@app.get("/api/hitl/packets")
def list_hitl_packets():
    """Lists all HITL review packets."""
    return drilldown_engine.hitl_manager.list_all()


@app.post("/api/hitl/decision")
def submit_hitl_decision(req: HITLDecisionRequest):
    """Submits human approval or rejection on a pending review packet."""
    try:
        updated = drilldown_engine.hitl_manager.submit_decision(
            packet_id=req.packet_id,
            decision=req.decision,
            comments=req.comments,
        )
        return updated
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.get("/api/eval/benchmark", response_model=BenchmarkSummaryReport)
def run_benchmark_suite():
    """Runs the canonical evaluation harness across all benchmark scenarios."""
    report = eval_harness.run_all_benchmarks()
    return report


import os
from fastapi.staticfiles import StaticFiles

if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

