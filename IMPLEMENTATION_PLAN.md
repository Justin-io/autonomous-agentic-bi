# Implementation Plan
## Autonomous Agentic BI & Conversational Analytics Platform

### 1. Plan Overview
This implementation plan follows a bounded autonomous loop (`OBSERVE → PLAN → IMPLEMENT → TEST → RUN → EVALUATE → CRITIQUE → CORRECT → VERIFY → RECORD → REPEAT`) organized into 13 sequential epics. Every task requires automated testing and machine-checkable acceptance criteria before progressing.

---

### 2. Execution Phases

#### Phase 1: Data Warehouse, Semantic Layer & Database Connectors (Epics 1, 2, 3)
- Deliverables:
  - `warehouse/`: Enterprise generator producing 8 relational tables (`customers`, `products`, `geography`, `orders`, `order_items`, `churn_events`, `marketing_campaigns`, `calendar_dim`) calibrated for the Kerala Q2 product churn scenario.
  - `core/semantic_layer/`: Pydantic models, canonical metrics, dimensions, grain, allowable join paths, and fanout guard.
  - `core/database/`: DuckDB and PostgreSQL connectors with read-only enforcement and SHA-256 result hashing.
  - Tests: `test_warehouse.py`, `test_semantic_layer.py`.

#### Phase 2: SQL Engine, AST Validation & Cost Estimator (Epic 4)
- Deliverables:
  - `core/sql_engine/`: `sqlglot` AST validation, mutating statement rejection, alias resolution, grounded SQL generator, and EXPLAIN cost estimator.
  - Tests: `test_sql_engine.py`.

#### Phase 3: Profiling, Inferential Statistics & Shift-Share Segmentation (Epic 5)
- Deliverables:
  - `core/statistics/`: Data profiler, Welch t-test, Mann-Whitney U, Cohen's d, and multi-dimensional shift-share contribution analysis.
  - Tests: `test_statistics_and_segmentation.py`.

#### Phase 4: Counterargument Critic, Evidence-Sufficiency Gate & Citations (Epics 6, 7)
- Deliverables:
  - `core/counterargument/`: Independent Critic Agent auditing for Simpson's paradox and sample size adequacy; explicit evidence-sufficiency gate with refusal as a first-class successful state.
  - `core/evidence/`: Cryptographic SHA-256 evidence store, calibrated multi-factor confidence scoring, and deterministic regex claim verifier.
  - Tests: `test_counterargument_and_refusal.py`, `test_evidence_and_verifier.py`.

#### Phase 5: Visualizations, HITL & 16-Stage Orchestrator (Epics 8, 9)
- Deliverables:
  - `core/visuals/`: Plotly chart generator (waterfall, time-series anomaly, cohort, regional bar).
  - `core/hitl/`: Human-in-the-Loop review manager.
  - `core/orchestrator/`: 16-stage deterministic pipeline and conversational drill-down engine ("Why?" and "What should we do?").
  - Tests: `test_visuals_and_hitl.py`, `test_orchestrator_and_drilldown.py`.

#### Phase 6: Evaluation Harness & Benchmark Business Suite (Epic 10)
- Deliverables:
  - `eval/`: Automated harness running BQ-1 (Kerala Q2 product churn), BQ-2 ("Why?" drilldown), BQ-3 ("What should we do?"), and BQ-4 (Evidence-sufficiency refusal).

#### Phase 7: FastAPI Service & React + TypeScript Workspace (Epics 11, 12)
- Deliverables:
  - `api/`: REST API with real-time SSE event streaming and HITL decision endpoints.
  - `frontend/`: Interactive React 18 + TypeScript SPA with 16-stage stepper, Plotly charts, chat interface, and HITL modal. Production build in `frontend/dist`.
  - Tests: `test_api_e2e.py`.

#### Phase 8: Packaging, Docker & Cloud Deployment (Epic 13)
- Deliverables:
  - `Dockerfile`, `docker-compose.yml`, `Makefile`, `docs/AWS_DEPLOYMENT.md`, `README.md`.
  - Full test suite passing across all modules.
