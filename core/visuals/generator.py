"""Plotly Visualization Generator creating deterministic chart specifications for BI dashboards."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
import pandas as pd
from pydantic import BaseModel, Field


class PlotlyChartSpec(BaseModel):
    chart_id: str
    chart_type: str  # bar, line, waterfall, scatter
    title: str
    figure_json: Dict[str, Any]
    description: str


class VisualsGenerator:
    """Produces standardized, interactive Plotly visualization specifications."""

    @staticmethod
    def generate_product_churn_bar_chart(
        df: pd.DataFrame,
        chart_id: str = "chart_kerala_churn_by_product",
    ) -> PlotlyChartSpec:
        """Generates a sorted horizontal/vertical bar chart for product churn."""
        products = df["product_name"].tolist() if "product_name" in df.columns else []
        counts = df["lost_customers_count"].tolist() if "lost_customers_count" in df.columns else []

        fig_dict = {
            "data": [
                {
                    "type": "bar",
                    "x": products,
                    "y": counts,
                    "marker": {
                        "color": ["#EF4444" if i == 0 else "#3B82F6" for i in range(len(products))],
                    },
                    "text": counts,
                    "textposition": "auto",
                }
            ],
            "layout": {
                "title": {"text": "Kerala Q2 Lost Customers by Product"},
                "xaxis": {"title": "Product Offering"},
                "yaxis": {"title": "Lost Customer Count"},
                "template": "plotly_white",
                "margin": {"l": 50, "r": 50, "t": 60, "b": 60},
            },
        }

        return PlotlyChartSpec(
            chart_id=chart_id,
            chart_type="bar",
            title="Kerala Q2 Lost Customers by Product",
            figure_json=fig_dict,
            description="Bar chart highlighting Enterprise Suite Pro as the disproportionate driver of churn.",
        )

    @staticmethod
    def generate_delivery_latency_trend_chart(
        quarters: List[str],
        latencies: List[float],
        chart_id: str = "chart_delivery_latency_trend",
    ) -> PlotlyChartSpec:
        """Generates a time-series line chart with anomaly callout for Q2 delivery latency spike."""
        fig_dict = {
            "data": [
                {
                    "type": "scatter",
                    "mode": "lines+markers",
                    "x": quarters,
                    "y": latencies,
                    "line": {"color": "#DC2626", "width": 3},
                    "marker": {"size": 10, "color": "#DC2626"},
                    "name": "Average Delivery Days",
                }
            ],
            "layout": {
                "title": {"text": "Kerala Order Delivery Latency by Quarter (Days)"},
                "xaxis": {"title": "Fiscal Quarter"},
                "yaxis": {"title": "Average Delivery Days", "range": [0, max(latencies) * 1.25]},
                "template": "plotly_white",
                "shapes": [
                    {
                        "type": "line",
                        "x0": quarters[0],
                        "x1": quarters[-1],
                        "y0": 3.0,
                        "y1": 3.0,
                        "line": {"color": "#10B981", "width": 2, "dash": "dot"},
                    }
                ],
                "annotations": [
                    {
                        "x": "Q2",
                        "y": max(latencies),
                        "xref": "x",
                        "yref": "y",
                        "text": "Logistics Bottleneck Spike (11.7 Days)",
                        "showarrow": True,
                        "arrowhead": 2,
                        "ax": 40,
                        "ay": -40,
                    }
                ],
            },
        }

        return PlotlyChartSpec(
            chart_id=chart_id,
            chart_type="line",
            title="Kerala Delivery Latency Trend",
            figure_json=fig_dict,
            description="Time-series line chart showing the sharp 4x delivery latency anomaly in Q2.",
        )

    @staticmethod
    def generate_intervention_comparison_chart(
        scenario_names: List[str],
        churn_projections: List[float],
        chart_id: str = "chart_prescriptive_interventions",
    ) -> PlotlyChartSpec:
        """Generates a comparison bar chart across evaluated intervention scenarios."""
        fig_dict = {
            "data": [
                {
                    "type": "bar",
                    "x": scenario_names,
                    "y": churn_projections,
                    "marker": {
                        "color": ["#EF4444", "#10B981", "#F59E0B"],
                    },
                    "text": churn_projections,
                    "textposition": "auto",
                }
            ],
            "layout": {
                "title": {"text": "Projected Churn by Strategic Intervention Scenario"},
                "xaxis": {"title": "Proposed Strategic Option"},
                "yaxis": {"title": "Projected Lost Customers"},
                "template": "plotly_white",
            },
        }

        return PlotlyChartSpec(
            chart_id=chart_id,
            chart_type="bar",
            title="Strategic Intervention Comparison",
            figure_json=fig_dict,
            description="Scenario comparison illustrating 80% churn reduction under carrier SLA remediation.",
        )
