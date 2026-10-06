# Product Requirements Document (PRD)
## Autonomous Agentic BI & Conversational Analytics Platform

### 1. Vision & Core Philosophy
The Agentic BI Platform combines Power BI-grade dimensional modeling and interactive visualization with ChatGPT-grade conversational fluency and an autonomous data scientist. 

**Core Principle**: The system **must never confidently answer a business question merely because an LLM can generate a plausible explanation—it must earn every conclusion through data, computation, statistical verification, and evidence**. 

When a user asks: *"Which products lost the most customers in Kerala during Q2?"*, the system does not hallucinate SQL or generate ungrounded prose. It executes a rigorous, deterministic, machine-checkable 16-stage pipeline:
`QUESTION → PLANNER → SCHEMA DISCOVERY → SEMANTIC GROUNDING → SQL GENERATION → SQL VALIDATION → QUERY-COST OPTIMIZATION → DATABASE EXECUTION → DATA PROFILING → STATISTICAL ANALYSIS → SEGMENTATION → VISUALIZATION → INSIGHT GENERATION → COUNTERARGUMENT → VERIFICATION → EVIDENCE-BACKED ANSWER`.

It supports multi-turn conversational drill-downs:
- **"Why?"**: Autonomously decomposes contribution drivers, isolates variance across geographic/cohort/product dimensions, generates competing hypotheses, tests them with statistical rigor, and recursively investigates until a defensible root cause is reached.
- **"What should we do?"**: Evaluates candidate interventions using historical cohort behavior, forecasting, experimentation data (A/B tests), and scenario modeling, while **strictly separating observed evidence, predictions, assumptions, and recommendations**.

If the available data is insufficient to substantiate a claim, the platform hits an explicit **Evidence-Sufficiency Gate** and **refuses** to provide an ungrounded conclusion, explaining exactly what data is missing. **Refusal is treated as a first-class successful system state rather than an error.**

---

### 2. Core Personas
1. **Executive Stakeholders & Business Leaders**: Need instant, reliable answers to strategic questions (e.g., regional churn, revenue contraction) backed by verifiable evidence, clear visualizations, and actionable scenario forecasts.
2. **Analytics & BI Engineers**: Require a trustworthy semantic layer, schema governance, query cost limits, and read-only database safety with zero SQL injection or join fanout risks.
3. **Data Scientists & Decision Reviewers**: Demand transparent causal reasoning, counterargument auditing (checking for Simpson's paradox, sample size adequacy, and denominator drift), and Human-in-the-Loop review for high-impact recommendations.

---

### 3. Core Functional Requirements

#### 3.1 16-Stage Autonomous Execution Pipeline
1. `QUESTION`: Ingest and validate natural-language analytical queries.
2. `PLANNER`: Generate structured, multi-step investigation DAG.
3. `SCHEMA_DISCOVERY`: Inspect warehouse catalogs, tables, and relationships.
4. `SEMANTIC_GROUNDING`: Map business concepts to canonical entities, metrics, dimensions, grain, and allowable join paths.
5. `SQL_GENERATION`: Generate deterministic SQL targeting DuckDB, PostgreSQL, or Snowflake.
6. `SQL_VALIDATION`: AST parsing with `sqlglot`, verifying schema existence, grain consistency, aggregations, date boundaries, NULL handling, and blocking any mutating statements (`DROP`, `DELETE`, `UPDATE`, `INSERT`).
7. `QUERY_COST_OPTIMIZATION`: EXPLAIN plan cost estimation, row limits, and query caching.
8. `DATABASE_EXECUTION`: Secure, read-only query execution returning structured Arrow/Pandas datasets.
9. `DATA_PROFILING`: Summary statistics, null ratios, skewness, distribution analysis.
10. `STATISTICAL_ANALYSIS`: Inferential hypothesis testing (t-tests, Mann-Whitney U, Chi-square, Cohen's d effect sizes, 95% CIs).
11. `SEGMENTATION`: Multi-dimensional shift-share variance decomposition isolating top contributing segments (e.g., Kerala regional customers, product SKUs).
12. `VISUALIZATION`: Deterministic Plotly chart specifications (waterfall, time-series anomaly, cohort retention heatmap, regional bar).
13. `INSIGHT_GENERATION`: Synthesizing factual findings backed by evidence references.
14. `COUNTERARGUMENT`: Independent Critic Agent auditing for Simpson's paradox, selection bias, confounding, and sample size inadequacy.
15. `VERIFICATION`: Calibrated evidence-sufficiency gate checking if evidence passes confidence threshold ($\ge 0.70$) or triggers explicit refusal.
16. `EVIDENCE_BACKED_ANSWER`: Final structured response with mandatory `[EVD-...]` cryptographic citations.

#### 3.2 Conversational Recursive Drill-Down ("Why?" & "What should we do?")
- **Diagnostic "Why?" Loop**: Recursively isolates variance across dimensional hierarchies (Region → District → Product Category → SKU → Customer Tier), testing candidate hypotheses until the primary driver is pinpointed.
- **Prescriptive "What should we do?" Loop**: Evaluates candidate interventions (e.g. pricing rollback, localized customer reactivation, supply chain restocking), runs counterfactual forecasts, states underlying causal assumptions, and requires Human-in-the-Loop approval for high-impact actions.

#### 3.3 Semantic Layer & Governance
- Pydantic models for Entities, Metrics, Dimensions, Relationships, and Grain.
- Prevents join fanout via allowable join graphs and validates GROUP BY grain.
- Metric definitions, business rules, lineage tracking, and synonym resolution.

#### 3.4 Multi-Warehouse Connectors
- **DuckDB**: Fast, in-memory local columnar analytical engine.
- **PostgreSQL**: Production transactional and analytical data hub.
- **Pandas / Arrow**: In-memory dataframe profiling and statistical manipulation.

#### 3.5 Independent Counterargument & Evidence-Sufficiency Gate
- Evaluates alternative explanations and data artifacts.
- Enforces an explicit Evidence-Sufficiency Gate: when data is incomplete or ambiguous, the system must refuse with detailed diagnostic requirements.

#### 3.6 Evaluation & Benchmark Suite
- Evaluates SQL accuracy, semantic grounding, numerical correctness, analytical validity, citation completeness, hallucination rate, refusal correctness, recommendation quality, latency, and token cost.

#### 3.7 Interactive React + TypeScript Workspace
- Power BI-style dashboard combined with ChatGPT-style conversational analyst workspace, interactive Plotly visuals, trajectory viewer, and HITL approval modal.
