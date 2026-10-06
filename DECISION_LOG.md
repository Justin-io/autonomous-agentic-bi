# Decision Log (Architectural Decision Records)

## ADR-001: 16-Stage Explicit Workflow Over Unconstrained ReAct Loops
- **Status**: ACCEPTED
- **Context**: Unconstrained LLM agent loops frequently enter infinite cycles, generate hallucinated SQL, or skip verification.
- **Decision**: Enforce a strict 16-stage pipeline:
  `QUESTION → PLANNER → SCHEMA DISCOVERY → SEMANTIC GROUNDING → SQL GENERATION → SQL VALIDATION → QUERY-COST OPTIMIZATION → DATABASE EXECUTION → DATA PROFILING → STATISTICAL ANALYSIS → SEGMENTATION → VISUALIZATION → INSIGHT GENERATION → COUNTERARGUMENT → VERIFICATION → EVIDENCE-BACKED ANSWER`.
- **Consequences**: Guarantees deterministic progress, auditability, and machine-checkable guards at every step.

## ADR-002: Evidence-Sufficiency Gate & Refusal as a First-Class Success State
- **Status**: ACCEPTED
- **Context**: Standard AI BI chatbots fabricate plausible justifications when requested business data is missing or ambiguous.
- **Decision**: When evidence is insufficient (sample size too small, confounding cannot be controlled, tracking data missing), the system must halt and transition to `REFUSAL_SUFFICIENT_DATA_MISSING`. It outputs an objective diagnostic report specifying what data was examined, why it is insufficient, and what additional data is required.
- **Consequences**: Zero hallucinated answers; refusal is evaluated as a successful system behavior.

## ADR-003: Shift-Share Variance Decomposition for "Why?" Drill-Downs
- **Status**: ACCEPTED
- **Context**: Explaining "why" top-line metrics shifted requires mathematical decomposition rather than speculative narrative.
- **Decision**: Implement multi-dimensional shift-share contribution analysis:
  $$\text{Contribution}_s = \frac{\Delta \text{Metric}_s}{\sum \Delta \text{Metric}} \times 100\%$$
- **Consequences**: Exactly identifies which products or regions drove top-line changes.

## ADR-004: Strict Separation in Prescriptive Answers ("What should we do?")
- **Status**: ACCEPTED
- **Context**: Prescriptive recommendations often conflate historical facts with speculative forecasts.
- **Decision**: The system enforces a strict 4-section taxonomy: (1) Observed Evidence (`[EVD-...]`), (2) Statistical Predictions, (3) Explicit Causal Assumptions, and (4) Actionable Recommendations with Human-in-the-Loop review.
- **Consequences**: Transparent, decision-grade prescriptive insights.

## ADR-005: AST Validation with sqlglot and Read-Only Execution
- **Status**: ACCEPTED
- **Context**: Autonomous SQL execution risks accidental mutations or join fanout bugs.
- **Decision**: Every query is parsed into an AST using `sqlglot`, checked against the semantic layer join graph, validated for table existence, and executed exclusively through read-only connections.
- **Consequences**: Complete security against SQL injection, data mutations, and join duplication.
