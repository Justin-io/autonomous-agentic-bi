"""Automated Data Profiler computing descriptive statistics, null rates, and distribution anomalies."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field


class ColumnProfile(BaseModel):
    name: str
    dtype: str
    total_count: int
    null_count: int
    null_percentage: float
    distinct_count: int
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    mean: Optional[float] = None
    std: Optional[float] = None
    median: Optional[float] = None
    outlier_count: int = 0


class DatasetProfile(BaseModel):
    row_count: int
    column_count: int
    columns: Dict[str, ColumnProfile]
    dataset_hash: str


class DataProfiler:
    """Profiles analytical datasets to ensure data hygiene, identify anomalies, and detect outliers."""

    @staticmethod
    def profile_dataframe(df: pd.DataFrame, dataset_hash: str = "") -> DatasetProfile:
        row_count = len(df)
        column_count = len(df.columns)
        profiles: Dict[str, ColumnProfile] = {}

        for col in df.columns:
            s = df[col]
            null_count = int(s.isnull().sum())
            null_pct = round(null_count / row_count * 100.0, 2) if row_count > 0 else 0.0
            distinct_count = int(s.nunique(dropna=True))

            min_val = None
            max_val = None
            mean_val = None
            std_val = None
            median_val = None
            outlier_cnt = 0

            if pd.api.types.is_numeric_dtype(s) and not s.dropna().empty:
                valid_num = s.dropna().astype(float)
                min_val = round(float(valid_num.min()), 4)
                max_val = round(float(valid_num.max()), 4)
                mean_val = round(float(valid_num.mean()), 4)
                std_val = round(float(valid_num.std()), 4) if len(valid_num) > 1 else 0.0
                median_val = round(float(valid_num.median()), 4)

                # IQR outlier check
                q25, q75 = np.percentile(valid_num, [25, 75])
                iqr = q75 - q25
                lower_bound = q25 - 1.5 * iqr
                upper_bound = q75 + 1.5 * iqr
                outlier_cnt = int(((valid_num < lower_bound) | (valid_num > upper_bound)).sum())
            elif pd.api.types.is_string_dtype(s) or pd.api.types.is_object_dtype(s):
                valid_str = s.dropna().astype(str)
                if not valid_str.empty:
                    min_val = str(valid_str.min())
                    max_val = str(valid_str.max())

            profiles[col] = ColumnProfile(
                name=col,
                dtype=str(s.dtype),
                total_count=row_count,
                null_count=null_count,
                null_percentage=null_pct,
                distinct_count=distinct_count,
                min_value=min_val,
                max_value=max_val,
                mean=mean_val,
                std=std_val,
                median=median_val,
                outlier_count=outlier_cnt,
            )

        return DatasetProfile(
            row_count=row_count,
            column_count=column_count,
            columns=profiles,
            dataset_hash=dataset_hash,
        )
