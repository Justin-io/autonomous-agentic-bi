# System Architecture Document
## Autonomous Agentic BI & Conversational Analytics Platform

### 1. High-Level System Architecture

```
                                +-------------------------------------+
                                |      React + TypeScript Workspace   |
                                |  (Power BI Visuals + Chat Interface)|
                                +------------------+------------------+
                                                   | HTTP / SSE
                                                   v
                                +-------------------------------------+
                                |        FastAPI Service Hub          |
                                | (Routers, SSE Events, HITL Approvals|
                                +------------------+------------------+
                                                   |
                     +-----------------------------+-----------------------------+
                     |                                                           |
                     v                                                           v
+------------------------------------------+               +-------------------------------------------+
|    Conversational Session Orchestrator   |               |          Canonical Semantic Layer         |
|  - Multi-Turn Context (Why? / What now?) |<------------->|  - Entities, Metrics, Dimensions, Grain   |
|  - Hypothesis & Intervention State Trees |               |  - Allowable Joins & Fanout Guard         |
+--------------------+---------------------+               +-------------------------------------------+
                     |
                     v
+------------------------------------------------------------------------------------------------------+
|                                   16-Stage Autonomous Execution Pipeline                             |
|                                                                                                      |
|  [1. QUESTION]          : Natural-language input parsing & entity extraction                         |
|  [2. PLANNER]           : Structured multi-step analytical execution graph                           |
|  [3. SCHEMA_DISCOVERY]  : Catalog introspection & table schema discovery                             |
|  [4. SEMANTIC_GROUND]   : Canonical metric/dimension mapping & grain consistency                     |
|  [5. SQL_GENERATION]    : Grounded SQL query generation targeting warehouse                          |
|  [6. SQL_VALIDATION]    : sqlglot AST parsing, read-only guard, join fanout & PII checks            |
|  [7. QUERY_OPTIMIZE]    : EXPLAIN cost estimation, caching, row limit safety                         |
|  [8. DB_EXECUTION]      : Secure database query execution (DuckDB / PostgreSQL)                      |
|  [9. DATA_PROFILING]    : Column profiling, null checks, distribution & variance analysis           |
|  [10. STATS_ANALYSIS]   : Inferential hypothesis tests (t-test, Mann-Whitney, Cohen's d, 95% CI)     |
|  [11. SEGMENTATION]     : Multi-dimensional shift-share contribution decomposition                   |
|  [12. VISUALIZATION]    : Plotly chart specification synthesis (Waterfall, Anomaly, Heatmap, Bar)   |
|  [13. INSIGHT_GEN]      : Structured business insights with quantified impact metrics                |
|  [14. COUNTERARGUMENT]  : Independent Critic Agent (Simpson's paradox, bias, small N audits)        |
|  [15. VERIFICATION]     : Calibrated evidence-sufficiency gate (Score >= 0.70 or explicit Refusal)   |
|  [16. ANSWER]           : Decision-grade report with cryptographic [EVD-...] citations               |
+--------------------------------------------------+---------------------------------------------------+
                                                   |
                     +-----------------------------+-----------------------------+
                     |                                                           |
                     v                                                           v
+------------------------------------------+               +-------------------------------------------+
|       Database & Analytical Engines      |               |      Evidence Store & Audit Lineage       |
|  - DuckDB (Fast in-memory columnar engine|               |  - Cryptographic SHA-256 Dataset Hashes   |
|  - PostgreSQL (Relational data hub)      |               |  - Multi-Factor Calibrated Confidence     |
|  - Pandas / SciPy (In-memory profiling)  |               |  - OpenTelemetry Spans & MLflow Artifacts |
+------------------------------------------+               +-------------------------------------------+
```

---

### 2. Conversational Recursive Drill-Down Loops

The platform natively supports multi-turn conversational investigations:

#### 2.1 The "Why?" Diagnostic Loop
When a user asks *"Why?"* after an initial finding (e.g. *"Why did Kerala product sales drop in Q2?"*):
1. **Dimension Hierarchy Expansion**: Traverses parent-child dimension hierarchies (`State → District → Channel → Product Tier → Customer Cohort`).
2. **Competing Hypothesis Generation**: Synthesizes multiple falsifiable hypotheses (e.g., $H_1$: Supply chain out-of-stock, $H_2$: Local pricing change, $H_3$: Competitor campaign, $H_4$: Churn concentrated in Enterprise tier).
3. **Shift-Share Contribution Analysis**: Quantifies exact percentage contribution of each segment to the top-line delta:
   $$\text{Contribution}_s = \frac{\Delta \text{Metric}_s}{\sum \Delta \text{Metric}} \times 100\%$$
4. **Bayesian Posterior Update**: Evaluates empirical data against each hypothesis and prunes refuted hypotheses.
5. **Recursion**: Continues drilling down until a statistically defensible root cause is isolated.

#### 2.2 The "What should we do?" Prescriptive Loop
When a user asks *"What should we do?"*:
1. **Strict Separation of Epistemological Layers**:
   - **Observed Evidence**: Cryptographically grounded historical facts (`[EVD-...]`).
   - **Predictions**: Statistical forecasts and time-series projections with confidence bands.
   - **Causal Assumptions**: Explicit statements of unconfoundedness, stable unit treatment value (SUTVA), and external validity.
   - **Recommendations**: Candidate interventions ranked by expected ROI and risk.
2. **Intervention Scenario Modeling**: Evaluates historical counterfactuals, elasticity estimates, and experimentation (A/B testing) datasets.
3. **Human-in-the-Loop (HITL) Gate**: High-impact recommendations (e.g., pricing restructures, inventory reallocation) require explicit human sign-off before operational execution.

---

### 3. Module Directory Structure

```
agentic_bi_platform/
├── PRD.md
├── ARCHITECTURE.md
├── TASK_REGISTRY.json
├── IMPLEMENTATION_PLAN.md
├── DECISION_LOG.md
├── EVALUATION_SPEC.md
├── PROGRESS_LOG.md
├── TEST_MATRIX.md
├── Makefile
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── core/
│   ├── semantic_layer/        # Canonical entities, metrics, dimensions, grain, join graph
│   │   ├── models.py
│   │   ├── catalog.py
│   │   └── resolver.py
│   ├── database/              # Multi-engine database connectors
│   │   ├── connector.py       # Base read-only connection protocol
│   │   ├── duckdb_engine.py   # DuckDB local columnar engine
│   │   └── postgres_engine.py # PostgreSQL connector
│   ├── sql_engine/            # AST parser, SQL generation, and validation
│   │   ├── generator.py       # Semantic grounded SQL generator
│   │   ├── validator.py       # sqlglot AST validator & mutation blocker
│   │   └── optimizer.py       # EXPLAIN cost estimator & query cache
│   ├── statistics/            # Profiling, inferential statistics, and segmentation
│   │   ├── profiler.py        # Dataset profiler (nulls, distributions, summary stats)
│   │   ├── inferential.py     # Welch t-test, Mann-Whitney U, Cohen's d, 95% CIs
│   │   ├── segmentation.py    # Shift-share contribution decomposition
│   │   └── forecasting.py     # Time-series trend and counterfactual scenario modeling
│   ├── counterargument/       # Independent Critic & Verification Agent
│   │   ├── critic.py          # Simpson's paradox, sample size, confounding audits
│   │   ├── sufficiency.py     # Evidence-sufficiency gate & first-class Refusal state
│   │   └── confidence.py      # Calibrated multi-factor confidence scoring
│   ├── evidence/              # Cryptographic evidence store and claim verification
│   │   ├── store.py           # Immutable SHA-256 evidence record tracker
│   │   └── verifier.py        # Deterministic numeric claim verifier
│   ├── visuals/               # Deterministic Plotly chart generator
│   │   └── generator.py       # Waterfall, time-series anomaly, cohort, regional bar
│   ├── orchestrator/          # 16-stage pipeline & conversational drill-down loop
│   │   ├── context.py         # Session context, turn history, and trajectory events
│   │   ├── pipeline.py        # 16-stage deterministic autonomous pipeline
│   │   └── drilldown.py       # "Why?" and "What should we do?" conversation runner
│   └── hitl/                  # Human-in-the-Loop review & checkpoint manager
│       └── manager.py         # Trigger evaluation & decision approval modal
├── warehouse/                 # Realistic synthetic enterprise warehouse generator
│   ├── generator.py           # Generates 10 relational tables (orders, products, customers, geography, etc.)
│   └── scenarios.py           # Pre-calibrated scenarios (Kerala Q2 product churn, pricing shock, etc.)
├── eval/                      # Comprehensive evaluation framework
│   ├── harness.py             # Measures SQL accuracy, grounding, refusal correctness, latency
│   └── benchmarks.py          # Benchmark business questions (BQ-1, BQ-2, BQ-3, BQ-Refusal)
├── api/                       # FastAPI web service & SSE event streams
│   ├── main.py
│   └── routes/
│       ├── chat.py            # Conversational analytical endpoint & SSE stream
│       ├── semantic.py        # Catalog introspection endpoints
│       └── hitl.py            # Approval endpoints
├── frontend/                  # React 18 + TypeScript Analyst Workspace
│   ├── src/
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── package.json
└── tests/                     # Comprehensive test suites
    ├── test_warehouse.py
    ├── test_semantic_layer.py
    ├── test_sql_engine.py
    ├── test_statistics_and_segmentation.py
    ├── test_counterargument_and_refusal.py
    ├── test_evidence_and_verifier.py
    ├── test_visuals_and_hitl.py
    ├── test_orchestrator_and_drilldown.py
    └── test_api_e2e.py
```

---

### 4. The 16-Stage Pipeline Specification

| Stage | Name | Input | Output | Verification Guard |
|---|---|---|---|---|
| 1 | `QUESTION` | Natural language string | Normalized query & tokens | Non-empty input validation |
| 2 | `PLANNER` | Query & intent | Execution DAG & phases | Feasibility & step limit guard |
| 3 | `SCHEMA_DISCOVERY` | Execution plan | Required tables & columns | Catalog schema existence |
| 4 | `SEMANTIC_GROUNDING` | Entity references | Canonical metrics, grain, joins | Join path graph validity |
| 5 | `SQL_GENERATION` | Semantic query plan | SQL string | Grounded dialect formatting |
| 6 | `SQL_VALIDATION` | Raw SQL string | AST & safety validation | `sqlglot` mutation rejection & fanout guard |
| 7 | `QUERY_COST_OPTIMIZE`| Validated SQL | Execution plan & estimated cost | Cost threshold (< 100,000 units) |
| 8 | `DATABASE_EXECUTION` | Safe SQL query | Raw tabular dataset | Read-only enforcement, row limits |
| 9 | `DATA_PROFILING` | Dataset | Column profiles, null rates | Minimum row count ($N \ge 1$) |
| 10 | `STATISTICAL_ANALYSIS`| Profiling data | Inferential test results, effect sizes | Statistical power ($N \ge 10$) |
| 11 | `SEGMENTATION` | Tabular metrics | Shift-share variance contributions | Total contribution sum = 100% |
| 12 | `VISUALIZATION` | Aggregated data | Plotly chart specification | Schema-valid chart JSON |
| 13 | `INSIGHT_GENERATION` | Stats & segments | Factual findings & deltas | Quantified numbers present |
| 14 | `COUNTERARGUMENT` | Generated insights | Critic audit report & biases | Simpson's paradox & small sample checks |
| 15 | `VERIFICATION` | Critic findings & evidence | Calibrated confidence score | $\ge 0.70$ or transition to `REFUSAL` |
| 16 | `EVIDENCE_BACKED_ANSWER` | Verified findings | Final markdown report | 100% numeric claims cited with `[EVD-...]` |

---

### 5. Explicit Evidence-Sufficiency Gate & Refusal as First-Class State

When a user asks an ungrounded or speculative question (e.g. *"What caused customer churn in a region where no tracking data exists?"*):
1. **Sufficiency Check**: System detects insufficient sample size ($N < 10$), missing causal counterfactuals, or omitted dimensions.
2. **Transition to `REFUSAL_SUFFICIENT_DATA_MISSING`**:
   - The system **refuses** to produce a misleading definitive answer.
   - It outputs an objective diagnostic explanation stating:
     - Exactly what question was asked.
     - What data was examined.
     - Why the evidence is insufficient (e.g., confounding variables cannot be controlled, sample size too small for statistical power).
     - Exactly what additional tracking, dataset, or telemetry is required to answer the question reliably.
3. Refusal is logged as a **successful evaluation outcome**, not an error.
