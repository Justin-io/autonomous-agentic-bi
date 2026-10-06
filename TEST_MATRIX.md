# Test Matrix

| Category | Suite | File | Tests / Targets | Status |
|---|---|---|---|---|
| Warehouse & Scenarios | Synthetic Warehouse & Kerala Churn | `tests/test_warehouse.py` | 8 relational tables, foreign key constraints, Kerala Q2 product churn scenario | PENDING |
| Semantic Layer | Catalog, Models & Join Graph | `tests/test_semantic_layer.py` | Metric definitions, entity grain, allowable join validation, fanout guard | PENDING |
| SQL Engine | AST Validator & Grounded Generator | `tests/test_sql_engine.py` | Mutation rejection, alias resolution, dialect formatting, cost estimator | PENDING |
| Statistics & Segmentation | Profiler & Shift-Share | `tests/test_statistics_and_segmentation.py` | Welch t-test, Cohen's d, shift-share variance contribution decomposition | PENDING |
| Counterargument & Refusal | Critic & Evidence-Sufficiency Gate | `tests/test_counterargument_and_refusal.py` | Simpson's paradox audit, sample size check, first-class refusal state | PENDING |
| Evidence & Lineage | Evidence Store & Claim Verifier | `tests/test_evidence_and_verifier.py` | SHA-256 data hashing, calibrated confidence, regex numeric claim verifier | PENDING |
| Visuals & HITL | Plotly Generator & HITL Review | `tests/test_visuals_and_hitl.py` | Waterfall/anomaly chart specs, HITL review triggers and approval workflow | PENDING |
| Orchestrator & Drill-Down | 16-Stage Pipeline & Multi-Turn | `tests/test_orchestrator_and_drilldown.py` | 16-stage pipeline, "Why?" diagnostic loop, "What should we do?" prescriptive loop | PENDING |
| API & E2E | FastAPI REST & SSE Stream | `tests/test_api_e2e.py` | Endpoints, SSE event streaming, BQ-1 Kerala evaluation, refusal test | PENDING |
