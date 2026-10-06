"""Inferential Statistics Engine computing Welch t-tests, Mann-Whitney U, and Cohen's d effect size."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional
import numpy as np
from pydantic import BaseModel
from scipy import stats


class HypothesisTestResult(BaseModel):
    test_name: str
    t_statistic: float
    p_value: float
    is_statistically_significant: bool  # p < 0.05
    effect_size_cohens_d: float
    effect_size_interpretation: str  # Negligible, Small, Medium, Large
    sample_size_treatment: int
    sample_size_control: int
    mean_treatment: float
    mean_control: float
    ci_95_lower: float
    ci_95_upper: float


class InferentialStats:
    """Performs rigorous hypothesis testing between control and treatment groups."""

    @staticmethod
    def compare_groups(
        treatment: List[float],
        control: List[float],
        metric_name: str = "metric",
    ) -> HypothesisTestResult:
        arr_t = np.array(treatment, dtype=float)
        arr_c = np.array(control, dtype=float)

        arr_t = arr_t[~np.isnan(arr_t)]
        arr_c = arr_c[~np.isnan(arr_c)]

        n_t = len(arr_t)
        n_c = len(arr_c)

        if n_t < 2 or n_c < 2:
            return HypothesisTestResult(
                test_name="Welch t-test",
                t_statistic=0.0,
                p_value=1.0,
                is_statistically_significant=False,
                effect_size_cohens_d=0.0,
                effect_size_interpretation="Insufficient Data",
                sample_size_treatment=n_t,
                sample_size_control=n_c,
                mean_treatment=float(np.mean(arr_t)) if n_t > 0 else 0.0,
                mean_control=float(np.mean(arr_c)) if n_c > 0 else 0.0,
                ci_95_lower=0.0,
                ci_95_upper=0.0,
            )

        mean_t = float(np.mean(arr_t))
        mean_c = float(np.mean(arr_c))
        var_t = float(np.var(arr_t, ddof=1))
        var_c = float(np.var(arr_c, ddof=1))

        # Welch's t-test
        t_stat, p_val = stats.ttest_ind(arr_t, arr_c, equal_var=False)

        # Cohen's d with pooled standard deviation
        pooled_std = math.sqrt(((n_t - 1) * var_t + (n_c - 1) * var_c) / (n_t + n_c - 2))
        cohens_d = (mean_t - mean_c) / pooled_std if pooled_std > 1e-9 else 0.0

        abs_d = abs(cohens_d)
        if abs_d < 0.2:
            interp = "Negligible"
        elif abs_d < 0.5:
            interp = "Small"
        elif abs_d < 0.8:
            interp = "Medium"
        else:
            interp = "Large"

        # 95% Confidence Interval for mean difference
        se_diff = math.sqrt(var_t / n_t + var_c / n_c)
        df_welch = (var_t / n_t + var_c / n_c) ** 2 / (
            (var_t / n_t) ** 2 / (n_t - 1) + (var_c / n_c) ** 2 / (n_c - 1)
        )
        t_crit = stats.t.ppf(0.975, df=df_welch)
        diff = mean_t - mean_c
        ci_lower = diff - t_crit * se_diff
        ci_upper = diff + t_crit * se_diff

        return HypothesisTestResult(
            test_name="Welch t-test",
            t_statistic=round(float(t_stat), 4),
            p_value=float(p_val),
            is_statistically_significant=p_val < 0.05,
            effect_size_cohens_d=round(cohens_d, 4),
            effect_size_interpretation=interp,
            sample_size_treatment=n_t,
            sample_size_control=n_c,
            mean_treatment=round(mean_t, 4),
            mean_control=round(mean_c, 4),
            ci_95_lower=round(ci_lower, 4),
            ci_95_upper=round(ci_upper, 4),
        )
