"""Semantic Resolver mapping natural language and structured intents into grounded semantic query plans."""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Set, Tuple
from core.semantic_layer.catalog import SemanticCatalog
from core.semantic_layer.models import (
    FilterCondition,
    FilterOperator,
    Metric,
    Dimension,
    OrderByClause,
    Relationship,
    ResolvedSemanticContext,
    SemanticQueryPlan,
)


class SemanticResolver:
    """Grounds user questions into safe, verified semantic layer concepts and join paths."""

    def __init__(self, catalog: Optional[SemanticCatalog] = None):
        self.catalog = catalog or SemanticCatalog()

    def resolve_from_intent(
        self,
        metric_names: List[str],
        dimension_names: List[str],
        filters: Optional[List[FilterCondition]] = None,
        order_by: Optional[List[OrderByClause]] = None,
        limit: Optional[int] = None,
    ) -> ResolvedSemanticContext:
        """Grounds explicit metric and dimension names, building allowable join paths."""
        errors: List[str] = []
        resolved_metrics: List[Metric] = []
        resolved_dimensions: List[Dimension] = []
        needed_entities: Set[str] = set()

        for m_name in metric_names:
            m = self.catalog.get_metric(m_name)
            if not m:
                errors.append(f"Metric '{m_name}' not found in semantic catalog.")
            else:
                resolved_metrics.append(m)
                needed_entities.add(m.entity_name)

        for d_name in dimension_names:
            d = self.catalog.get_dimension(d_name)
            if not d:
                errors.append(f"Dimension '{d_name}' not found in semantic catalog.")
            else:
                resolved_dimensions.append(d)
                needed_entities.add(d.entity_name)

        clean_filters = filters or []
        for f in clean_filters:
            d = self.catalog.get_dimension(f.dimension_name)
            if not d:
                errors.append(f"Filter dimension '{f.dimension_name}' not found in catalog.")
            else:
                needed_entities.add(d.entity_name)

        if errors:
            plan = SemanticQueryPlan(
                metrics=metric_names,
                dimensions=dimension_names,
                filters=clean_filters,
                order_by=order_by or [],
                limit=limit,
                target_entities=list(needed_entities),
            )
            return ResolvedSemanticContext(
                plan=plan,
                resolved_metrics=resolved_metrics,
                resolved_dimensions=resolved_dimensions,
                join_chain=[],
                is_valid=False,
                validation_errors=errors,
            )

        # Build join graph paths across required entities
        join_chain, join_errors = self._build_join_chain(needed_entities)
        errors.extend(join_errors)

        plan = SemanticQueryPlan(
            metrics=metric_names,
            dimensions=dimension_names,
            filters=clean_filters,
            order_by=order_by or [],
            limit=limit,
            target_entities=list(needed_entities),
        )

        return ResolvedSemanticContext(
            plan=plan,
            resolved_metrics=resolved_metrics,
            resolved_dimensions=resolved_dimensions,
            join_chain=join_chain,
            is_valid=len(errors) == 0,
            validation_errors=errors,
        )

    def resolve_natural_language_query(self, query: str) -> ResolvedSemanticContext:
        """Parses a user question into metrics, dimensions, filters, and safe join paths."""
        q_lower = query.lower()

        # 1. Metric detection
        detected_metrics: List[str] = []
        if any(term in q_lower for term in ["lost the most customers", "lost customers", "churn", "churned"]):
            detected_metrics.append("lost_customers_count")
        elif any(term in q_lower for term in ["delivery", "latency", "shipping", "transit days"]):
            detected_metrics.append("avg_delivery_days")
        elif any(term in q_lower for term in ["revenue", "sales", "turnover"]):
            detected_metrics.append("net_revenue")
        elif any(term in q_lower for term in ["orders", "order count", "volume"]):
            detected_metrics.append("order_count")
        else:
            # Default to lost_customers_count if customer loss mentioned
            detected_metrics.append("lost_customers_count")

        # 2. Dimension detection
        detected_dimensions: List[str] = []
        if "product" in q_lower:
            detected_dimensions.extend(["product_id", "product_name", "category"])
        if "state" in q_lower or "kerala" in q_lower or "region" in q_lower:
            # If asking by state explicitly
            if "by state" in q_lower or "per state" in q_lower:
                detected_dimensions.append("state")
        if "quarter" in q_lower or "quarterly" in q_lower or "over time" in q_lower:
            detected_dimensions.append("quarter")
        if "reason" in q_lower or "why" in q_lower:
            detected_dimensions.append("churn_reason")

        # Deduplicate dimensions preserving order
        seen_dims = set()
        dedup_dims = []
        for d in detected_dimensions:
            if d not in seen_dims:
                seen_dims.add(d)
                dedup_dims.append(d)
        detected_dimensions = dedup_dims

        # 3. Filters detection
        filters: List[FilterCondition] = []
        # State filter
        for state in ["Kerala", "Karnataka", "Maharashtra", "Tamil Nadu"]:
            if state.lower() in q_lower:
                filters.append(FilterCondition(dimension_name="state", operator=FilterOperator.EQUALS, value=state))
                break

        # Quarter filter
        quarter_match = re.search(r"\b(q[1-4])\b", q_lower)
        if quarter_match:
            q_val = quarter_match.group(1).upper()
            filters.append(FilterCondition(dimension_name="quarter", operator=FilterOperator.EQUALS, value=q_val))

        # 4. Order and limit
        order_by: List[OrderByClause] = []
        if detected_metrics:
            order_by.append(OrderByClause(field_name=detected_metrics[0], direction="DESC"))

        limit = 10 if "top" in q_lower or "most" in q_lower else None

        return self.resolve_from_intent(
            metric_names=detected_metrics,
            dimension_names=detected_dimensions,
            filters=filters,
            order_by=order_by,
            limit=limit,
        )

    def _build_join_chain(self, entities: Set[str]) -> Tuple[List[Relationship], List[str]]:
        """Finds a minimal spanning tree of join paths connecting all required entities."""
        if len(entities) <= 1:
            return [], []

        entities_list = list(entities)
        # Select base table: prefer fact tables like churn_events, orders, order_items
        root = None
        for candidate in ["churn_events", "orders", "order_items", "customers"]:
            if candidate in entities:
                root = candidate
                break
        if not root:
            root = entities_list[0]

        all_rels: List[Relationship] = []
        errors: List[str] = []
        visited_nodes = {root}

        target_nodes = set(entities) - {root}
        while target_nodes:
            found_step = False
            for target in list(target_nodes):
                path = self.catalog.find_join_path(root, target)
                if path is not None:
                    for rel in path:
                        # Avoid duplicates
                        if not any(
                            r.from_entity == rel.from_entity and r.to_entity == rel.to_entity
                            for r in all_rels
                        ):
                            all_rels.append(rel)
                        visited_nodes.add(rel.to_entity)
                        visited_nodes.add(rel.from_entity)
                    target_nodes.discard(target)
                    found_step = True
                    break
            if not found_step:
                errors.append(f"Cannot form valid join path between entities: {target_nodes} and root {root}")
                break

        return all_rels, errors
