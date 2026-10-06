"""Shift-Share Contribution Analysis and Multi-Dimensional Segmentation Engine."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import pandas as pd
from pydantic import BaseModel, Field


class SegmentContribution(BaseModel):
    dimension_name: str
    dimension_value: str
    baseline_value: float
    current_value: float
    delta_value: float
    contribution_percentage: float
    rank: int


class ShiftShareAnalysisResult(BaseModel):
    dimension_name: str
    total_baseline: float
    total_current: float
    total_delta: float
    segments: List[SegmentContribution]
    primary_driver_value: str
    primary_driver_share: float


class SegmentationEngine:
    """Performs mathematical shift-share variance decomposition across dimensional hierarchies."""

    @staticmethod
    def compute_shift_share(
        df_baseline: pd.DataFrame,
        df_current: pd.DataFrame,
        dimension_col: str,
        metric_col: str,
    ) -> ShiftShareAnalysisResult:
        """Decomposes the delta in a metric between baseline and current periods across dimension slices."""
        # Aggregate by dimension
        agg_base = df_baseline.groupby(dimension_col)[metric_col].sum().to_dict()
        agg_curr = df_current.groupby(dimension_col)[metric_col].sum().to_dict()

        all_keys = set(agg_base.keys()) | set(agg_curr.keys())

        total_base = float(sum(agg_base.values()))
        total_curr = float(sum(agg_curr.values()))
        total_delta = total_curr - total_base

        items = []
        for k in all_keys:
            v_base = float(agg_base.get(k, 0.0))
            v_curr = float(agg_curr.get(k, 0.0))
            delta = v_curr - v_base
            items.append({
                "dim_val": str(k),
                "v_base": v_base,
                "v_curr": v_curr,
                "delta": delta,
            })

        # Sort by absolute or positive delta descending
        items.sort(key=lambda x: x["delta"], reverse=True)

        segments: List[SegmentContribution] = []
        for rank, item in enumerate(items, 1):
            if abs(total_delta) > 1e-6:
                share_pct = round((item["delta"] / total_delta) * 100.0, 2)
            else:
                share_pct = round((item["v_curr"] / total_curr) * 100.0, 2) if total_curr > 0 else 0.0

            segments.append(
                SegmentContribution(
                    dimension_name=dimension_col,
                    dimension_value=item["dim_val"],
                    baseline_value=round(item["v_base"], 2),
                    current_value=round(item["v_curr"], 2),
                    delta_value=round(item["delta"], 2),
                    contribution_percentage=share_pct,
                    rank=rank,
                )
            )

        primary_driver = segments[0].dimension_value if segments else "None"
        primary_share = segments[0].contribution_percentage if segments else 0.0

        return ShiftShareAnalysisResult(
            dimension_name=dimension_col,
            total_baseline=round(total_base, 2),
            total_current=round(total_curr, 2),
            total_delta=round(total_delta, 2),
            segments=segments,
            primary_driver_value=primary_driver,
            primary_driver_share=primary_share,
        )

    @staticmethod
    def compute_distribution_share(
        df: pd.DataFrame,
        dimension_col: str,
        metric_col: str,
    ) -> List[SegmentContribution]:
        """Calculates share percentage of total for a single dataset (e.g. churn per product)."""
        agg = df.groupby(dimension_col)[metric_col].sum().reset_index()
        total_val = float(agg[metric_col].sum())

        agg = agg.sort_values(by=metric_col, ascending=False)
        results: List[SegmentContribution] = []

        for rank, row in enumerate(agg.itertuples(), 1):
            val = float(getattr(row, metric_col))
            pct = round((val / total_val) * 100.0, 2) if total_val > 0 else 0.0
            results.append(
                SegmentContribution(
                    dimension_name=dimension_col,
                    dimension_value=str(getattr(row, dimension_col)),
                    baseline_value=0.0,
                    current_value=val,
                    delta_value=val,
                    contribution_percentage=pct,
                    rank=rank,
                )
            )

        return results
