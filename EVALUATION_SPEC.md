# Evaluation Specification
## Autonomous Agentic BI & Conversational Analytics Platform

### 1. Mathematical Formulas & Definitions

#### 1.1 Shift-Share Contribution Decomposition
For a metric $M$ observed across baseline period $T_1$ and observation period $T_2$, partitioned into mutually exclusive segments $s \in S$:
$$\Delta M = M(T_2) - M(T_1)$$
$$\Delta M_s = M_s(T_2) - M_s(T_1)$$
$$\text{Contribution Percentage}_s = \frac{\Delta M_s}{\Delta M} \times 100\%$$
Where:
$$\sum_{s \in S} \text{Contribution Percentage}_s = 100\%$$

---

#### 1.2 Inferential Statistics & Effect Size
1. **Welch's Two-Sample t-test** (unequal sample variances):
   $$t = \frac{\bar{X}_1 - \bar{X}_2}{\sqrt{\frac{s_1^2}{N_1} + \frac{s_2^2}{N_2}}}$$
2. **Cohen's d Effect Size**:
   $$d = \frac{\bar{X}_1 - \bar{X}_2}{s_{\text{pooled}}}$$
   Categorization: Negligible ($|d| < 0.2$), Small ($0.2 \le |d| < 0.5$), Medium ($0.5 \le |d| < 0.8$), Large ($|d| \ge 0.8$).

---

#### 1.3 Multi-Factor Calibrated Confidence Score
Confidence score $C \in [0.0, 1.0]$ is computed as a weighted combination:
$$C = w_1 \cdot C_{\text{data}} + w_2 \cdot C_{\text{stat}} + w_3 \cdot C_{\text{semantic}} + w_4 \cdot C_{\text{critic}}$$
Where:
- $C_{\text{data}}$: Sample size adequacy, absence of NULL anomalies ($w_1 = 0.25$)
- $C_{\text{stat}}$: Statistical significance ($p < 0.05$) and effect size ($w_2 = 0.30$)
- $C_{\text{semantic}}$: Grounding in canonical metric models and valid joins ($w_3 = 0.25$)
- $C_{\text{critic}}$: Penalty for counterarguments, Simpson's paradox, or confounding ($w_4 = 0.20$)

**Gate Rule**: If $C < 0.70$ or evidence is strictly absent, system transitions to `REFUSAL_SUFFICIENT_DATA_MISSING`.

---

#### 1.4 Benchmark Scenarios (Canonical Suite)
- **BQ-1 (Initial Diagnostic)**: *"Which products lost the most customers in Kerala during Q2?"*
  - Ground truth: Kerala customer churn spiked in Q2 2024, overwhelmingly driven by "Product Pro Suite" (SKU-102) due to regional logistics delays and pricing friction.
- **BQ-2 (Conversational "Why?")**: *"Why did this happen?"*
  - Ground truth: Multi-dimensional shift-share decomposes the Kerala churn: 72% explained by SKU-102, correlated with 4.5x higher delivery latency in Ernakulam and Thiruvananthapuram districts.
- **BQ-3 (Conversational "What should we do?")**: *"What should we do?"*
  - Ground truth: Evaluates regional fulfillment SLA guarantees, targeted retention discounts; states causal assumptions and triggers HITL approval.
- **BQ-4 (Evidence-Sufficiency Refusal)**: *"Did the local election influence customer purchasing behavior in Kerala?"*
  - Ground truth: No political or election tracking data exists in warehouse. System strictly refuses and outputs missing data requirements.
