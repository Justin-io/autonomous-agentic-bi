"""Pydantic V2 data models for the canonical semantic layer."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CalculationType(str, Enum):
    SUM = "SUM"
    COUNT = "COUNT"
    COUNT_DISTINCT = "COUNT_DISTINCT"
    AVG = "AVG"
    RATIO = "RATIO"


class FilterOperator(str, Enum):
    EQUALS = "="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN_OR_EQUAL = "<="
    IN = "IN"
    NOT_IN = "NOT IN"
    LIKE = "LIKE"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"


class Entity(BaseModel):
    name: str
    table_name: str
    primary_key: str
    description: str


class Dimension(BaseModel):
    name: str
    display_name: str
    entity_name: str
    column_name: str
    data_type: str
    is_temporal: bool = False
    is_geographic: bool = False
    synonyms: List[str] = Field(default_factory=list)


class Metric(BaseModel):
    name: str
    display_name: str
    description: str
    sql_expression: str
    grain: str
    unit: str = "count"
    calculation_type: CalculationType = CalculationType.COUNT
    entity_name: str
    synonyms: List[str] = Field(default_factory=list)


class Relationship(BaseModel):
    from_entity: str
    to_entity: str
    join_type: str = "LEFT JOIN"
    from_key: str
    to_key: str
    cardinality: str = "many_to_one"  # many_to_one, one_to_one


class JoinGraph(BaseModel):
    relationships: List[Relationship] = Field(default_factory=list)

    def is_valid_join(self, from_entity: str, to_entity: str) -> bool:
        for r in self.relationships:
            if (r.from_entity == from_entity and r.to_entity == to_entity) or \
               (r.from_entity == to_entity and r.to_entity == from_entity):
                return True
        return False

    def get_relationship(self, from_entity: str, to_entity: str) -> Optional[Relationship]:
        for r in self.relationships:
            if (r.from_entity == from_entity and r.to_entity == to_entity) or \
               (r.from_entity == to_entity and r.to_entity == from_entity):
                return r
        return None


class FilterCondition(BaseModel):
    dimension_name: str
    operator: FilterOperator = FilterOperator.EQUALS
    value: Any


class OrderByClause(BaseModel):
    field_name: str
    direction: str = "DESC"  # ASC or DESC


class SemanticQueryPlan(BaseModel):
    metrics: List[str]
    dimensions: List[str] = Field(default_factory=list)
    filters: List[FilterCondition] = Field(default_factory=list)
    order_by: List[OrderByClause] = Field(default_factory=list)
    limit: Optional[int] = None
    target_entities: List[str] = Field(default_factory=list)


class ResolvedSemanticContext(BaseModel):
    plan: SemanticQueryPlan
    resolved_metrics: List[Metric]
    resolved_dimensions: List[Dimension]
    join_chain: List[Relationship]
    is_valid: bool = True
    validation_errors: List[str] = Field(default_factory=list)
