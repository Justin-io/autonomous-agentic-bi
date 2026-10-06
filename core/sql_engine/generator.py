"""Grounded SQL Generator translating semantic context into mathematically safe SQL queries."""

from __future__ import annotations

from typing import Dict, List, Optional, Set
from core.semantic_layer.models import FilterOperator, ResolvedSemanticContext


class GroundedSQLGenerator:
    """Translates resolved semantic query contexts into valid, dialect-clean SQL."""

    TABLE_ALIASES: Dict[str, str] = {
        "churn_events": "ce",
        "customers": "c",
        "geography": "g",
        "products": "p",
        "orders": "o",
        "order_items": "oi",
        "marketing_campaigns": "mc",
        "calendar_dim": "cal",
    }

    COLUMN_ENTITY_OVERRIDE: Dict[str, str] = {
        "state": "geography",
        "region": "geography",
        "district": "geography",
        "product_id": "products",
        "product_name": "products",
        "category": "products",
        "segment": "customers",
        "customer_id": "customers",
        "order_date": "orders",
        "delivery_days": "orders",
        "total_amount": "orders",
        "net_amount": "order_items",
        "churn_reason": "churn_events",
        "churn_date": "churn_events",
    }

    def generate_sql(self, context: ResolvedSemanticContext) -> str:
        """Builds a deterministic, grounded SQL query from semantic context."""
        if not context.is_valid:
            raise ValueError(f"Cannot generate SQL for invalid semantic context: {context.validation_errors}")

        plan = context.plan
        all_entities: Set[str] = set(plan.target_entities)

        # Select primary base entity
        base_entity = None
        for candidate in ["churn_events", "orders", "order_items", "customers"]:
            if candidate in all_entities:
                base_entity = candidate
                break
        if not base_entity:
            base_entity = list(all_entities)[0] if all_entities else "orders"

        base_alias = self.TABLE_ALIASES.get(base_entity, base_entity)

        # 1. SELECT items
        select_items: List[str] = []
        group_by_items: List[str] = []

        # Dimensions
        for dim in context.resolved_dimensions:
            alias = self.TABLE_ALIASES.get(dim.entity_name, dim.entity_name)
            col_expr = f"{alias}.{dim.column_name}"
            select_items.append(f"{col_expr} AS {dim.name}")
            group_by_items.append(col_expr)

        # Metrics
        for metric in context.resolved_metrics:
            # Map column references in metric.sql_expression to table aliases
            expr = metric.sql_expression
            for entity, a in self.TABLE_ALIASES.items():
                expr = expr.replace(f"{entity}.", f"{a}.")
            select_items.append(f"{expr} AS {metric.name}")

        if not select_items:
            select_items.append("*")

        # 2. FROM & JOINs
        from_clause = f"FROM {base_entity} {base_alias}"
        join_clauses: List[str] = []
        joined_tables: Set[str] = {base_entity}

        for rel in context.join_chain:
            # Determine which table is new
            if rel.to_entity not in joined_tables:
                target_table = rel.to_entity
                target_alias = self.TABLE_ALIASES.get(target_table, target_table)
                from_alias = self.TABLE_ALIASES.get(rel.from_entity, rel.from_entity)
                join_clauses.append(
                    f"{rel.join_type} {target_table} {target_alias} ON {from_alias}.{rel.from_key} = {target_alias}.{rel.to_key}"
                )
                joined_tables.add(target_table)
            elif rel.from_entity not in joined_tables:
                target_table = rel.from_entity
                target_alias = self.TABLE_ALIASES.get(target_table, target_table)
                to_alias = self.TABLE_ALIASES.get(rel.to_entity, rel.to_entity)
                join_clauses.append(
                    f"{rel.join_type} {target_table} {target_alias} ON {to_alias}.{rel.to_key} = {target_alias}.{rel.from_key}"
                )
                joined_tables.add(target_table)

        # 3. WHERE clause
        where_clauses: List[str] = []
        for f in plan.filters:
            # Determine appropriate entity for dimension
            entity_name = self.COLUMN_ENTITY_OVERRIDE.get(f.dimension_name, "churn_events")
            if f.dimension_name == "quarter":
                # If churn_events in query, filter churn_events.quarter; otherwise orders.quarter
                entity_name = "churn_events" if "churn_events" in joined_tables else "orders"
            
            alias = self.TABLE_ALIASES.get(entity_name, entity_name)
            
            val = f.value
            if isinstance(val, str):
                formatted_val = f"'{val}'"
            elif isinstance(val, (list, tuple)):
                formatted_val = "(" + ", ".join(f"'{v}'" if isinstance(v, str) else str(v) for v in val) + ")"
            else:
                formatted_val = str(val)

            where_clauses.append(f"{alias}.{f.dimension_name} {f.operator.value} {formatted_val}")

        # 4. Assembly
        lines = [
            "SELECT",
            "    " + ",\n    ".join(select_items),
            from_clause,
        ]
        if join_clauses:
            lines.extend(join_clauses)
        if where_clauses:
            lines.append("WHERE " + " AND ".join(where_clauses))
        if group_by_items and context.resolved_metrics:
            lines.append("GROUP BY " + ", ".join(group_by_items))

        # 5. ORDER BY
        if plan.order_by:
            order_items = [f"{ob.field_name} {ob.direction}" for ob in plan.order_by]
            lines.append("ORDER BY " + ", ".join(order_items))

        # 6. LIMIT
        if plan.limit:
            lines.append(f"LIMIT {plan.limit}")

        return "\n".join(lines)
