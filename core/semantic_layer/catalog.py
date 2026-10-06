"""Canonical Semantic Catalog defining enterprise entities, metrics, dimensions, and join paths."""

from __future__ import annotations

from typing import Dict, List, Optional
from core.semantic_layer.models import (
    CalculationType,
    Dimension,
    Entity,
    JoinGraph,
    Metric,
    Relationship,
)


class SemanticCatalog:
    """Enterprise semantic layer holding metric definitions, dimensions, and allowable join graph."""

    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.dimensions: Dict[str, Dimension] = {}
        self.metrics: Dict[str, Metric] = {}
        self.join_graph: JoinGraph = JoinGraph()
        self._initialize_canonical_definitions()

    def _initialize_canonical_definitions(self):
        # 1. Entities
        entities = [
            Entity(
                name="geography",
                table_name="geography",
                primary_key="geo_id",
                description="Regional and state geographic boundaries.",
            ),
            Entity(
                name="products",
                table_name="products",
                primary_key="product_id",
                description="Product catalog, pricing, and category taxonomy.",
            ),
            Entity(
                name="customers",
                table_name="customers",
                primary_key="customer_id",
                description="Customer accounts, business segment, and signup cohort.",
            ),
            Entity(
                name="orders",
                table_name="orders",
                primary_key="order_id",
                description="Transactional order headers with delivery duration and amounts.",
            ),
            Entity(
                name="order_items",
                table_name="order_items",
                primary_key="item_id",
                description="Line-item order detail containing item quantity and net revenue.",
            ),
            Entity(
                name="churn_events",
                table_name="churn_events",
                primary_key="churn_id",
                description="Customer churn records, cancellation dates, and root reasons.",
            ),
            Entity(
                name="marketing_campaigns",
                table_name="marketing_campaigns",
                primary_key="campaign_id",
                description="Marketing ad spend across channels and regions.",
            ),
            Entity(
                name="calendar_dim",
                table_name="calendar_dim",
                primary_key="date",
                description="Enterprise date dimension with quarters, months, and weekend flags.",
            ),
        ]
        for e in entities:
            self.entities[e.name] = e

        # 2. Dimensions
        dimensions = [
            Dimension(
                name="state",
                display_name="State",
                entity_name="geography",
                column_name="state",
                data_type="VARCHAR",
                is_geographic=True,
                synonyms=["state", "province", "region name", "kerala", "karnataka", "maharashtra", "tamil nadu"],
            ),
            Dimension(
                name="region",
                display_name="Region",
                entity_name="geography",
                column_name="region",
                data_type="VARCHAR",
                is_geographic=True,
                synonyms=["region", "territory", "geographical zone"],
            ),
            Dimension(
                name="district",
                display_name="District",
                entity_name="geography",
                column_name="district",
                data_type="VARCHAR",
                is_geographic=True,
                synonyms=["district", "city", "county"],
            ),
            Dimension(
                name="product_name",
                display_name="Product Name",
                entity_name="products",
                column_name="product_name",
                data_type="VARCHAR",
                synonyms=["product", "product title", "offering", "sku name"],
            ),
            Dimension(
                name="category",
                display_name="Product Category",
                entity_name="products",
                column_name="category",
                data_type="VARCHAR",
                synonyms=["category", "product line", "vertical"],
            ),
            Dimension(
                name="product_id",
                display_name="Product ID",
                entity_name="products",
                column_name="product_id",
                data_type="VARCHAR",
                synonyms=["product code", "sku", "item id"],
            ),
            Dimension(
                name="segment",
                display_name="Customer Segment",
                entity_name="customers",
                column_name="segment",
                data_type="VARCHAR",
                synonyms=["segment", "tier", "customer tier", "account size"],
            ),
            Dimension(
                name="quarter",
                display_name="Fiscal Quarter",
                entity_name="churn_events",
                column_name="quarter",
                data_type="VARCHAR",
                is_temporal=True,
                synonyms=["quarter", "q1", "q2", "q3", "q4", "fiscal quarter"],
            ),
            Dimension(
                name="order_quarter",
                display_name="Order Quarter",
                entity_name="orders",
                column_name="quarter",
                data_type="VARCHAR",
                is_temporal=True,
                synonyms=["order quarter", "sales quarter"],
            ),
            Dimension(
                name="churn_reason",
                display_name="Churn Reason",
                entity_name="churn_events",
                column_name="churn_reason",
                data_type="VARCHAR",
                synonyms=["reason", "cancellation reason", "churn cause"],
            ),
            Dimension(
                name="order_date",
                display_name="Order Date",
                entity_name="orders",
                column_name="order_date",
                data_type="DATE",
                is_temporal=True,
                synonyms=["date", "ordered date", "purchase date"],
            ),
        ]
        for d in dimensions:
            self.dimensions[d.name] = d

        # 3. Metrics
        metrics = [
            Metric(
                name="lost_customers_count",
                display_name="Lost Customers Count",
                description="Unique count of churned customers within the specified slice.",
                sql_expression="COUNT(DISTINCT churn_events.customer_id)",
                grain="customer_id, quarter",
                unit="count",
                calculation_type=CalculationType.COUNT_DISTINCT,
                entity_name="churn_events",
                synonyms=[
                    "lost customers",
                    "churned customers",
                    "churn count",
                    "customer loss",
                    "churn volume",
                    "lost clients",
                ],
            ),
            Metric(
                name="churn_events_count",
                display_name="Total Churn Events",
                description="Total number of churn log entries recorded.",
                sql_expression="COUNT(churn_events.churn_id)",
                grain="churn_id",
                unit="count",
                calculation_type=CalculationType.COUNT,
                entity_name="churn_events",
                synonyms=["churn events", "cancellations", "churn records"],
            ),
            Metric(
                name="net_revenue",
                display_name="Net Revenue",
                description="Total net revenue generated from completed order items.",
                sql_expression="SUM(order_items.net_amount)",
                grain="order_items.item_id",
                unit="currency",
                calculation_type=CalculationType.SUM,
                entity_name="order_items",
                synonyms=["revenue", "sales", "net sales", "total revenue", "turnover"],
            ),
            Metric(
                name="order_count",
                display_name="Total Orders",
                description="Total unique order volume processed.",
                sql_expression="COUNT(DISTINCT orders.order_id)",
                grain="orders.order_id",
                unit="count",
                calculation_type=CalculationType.COUNT_DISTINCT,
                entity_name="orders",
                synonyms=["order count", "orders", "order volume", "number of orders"],
            ),
            Metric(
                name="avg_delivery_days",
                display_name="Average Delivery Days",
                description="Average duration in days from order placement to customer delivery.",
                sql_expression="AVG(orders.delivery_days)",
                grain="orders.order_id",
                unit="days",
                calculation_type=CalculationType.AVG,
                entity_name="orders",
                synonyms=[
                    "delivery days",
                    "delivery latency",
                    "shipping days",
                    "delivery duration",
                    "shipping latency",
                    "lead time",
                ],
            ),
            Metric(
                name="marketing_spend",
                display_name="Marketing Spend",
                description="Total advertising and promotional expenditure.",
                sql_expression="SUM(marketing_campaigns.spend)",
                grain="marketing_campaigns.campaign_id",
                unit="currency",
                calculation_type=CalculationType.SUM,
                entity_name="marketing_campaigns",
                synonyms=["marketing spend", "ad spend", "campaign spend", "advertising expenditure"],
            ),
        ]
        for m in metrics:
            self.metrics[m.name] = m

        # 4. Allowable Relationships & Join Graph
        relationships = [
            Relationship(
                from_entity="customers",
                to_entity="geography",
                join_type="LEFT JOIN",
                from_key="geo_id",
                to_key="geo_id",
                cardinality="many_to_one",
            ),
            Relationship(
                from_entity="churn_events",
                to_entity="customers",
                join_type="LEFT JOIN",
                from_key="customer_id",
                to_key="customer_id",
                cardinality="many_to_one",
            ),
            Relationship(
                from_entity="churn_events",
                to_entity="products",
                join_type="LEFT JOIN",
                from_key="product_id",
                to_key="product_id",
                cardinality="many_to_one",
            ),
            Relationship(
                from_entity="orders",
                to_entity="customers",
                join_type="LEFT JOIN",
                from_key="customer_id",
                to_key="customer_id",
                cardinality="many_to_one",
            ),
            Relationship(
                from_entity="order_items",
                to_entity="orders",
                join_type="LEFT JOIN",
                from_key="order_id",
                to_key="order_id",
                cardinality="many_to_one",
            ),
            Relationship(
                from_entity="order_items",
                to_entity="products",
                join_type="LEFT JOIN",
                from_key="product_id",
                to_key="product_id",
                cardinality="many_to_one",
            ),
            Relationship(
                from_entity="orders",
                to_entity="calendar_dim",
                join_type="LEFT JOIN",
                from_key="order_date",
                to_key="date",
                cardinality="many_to_one",
            ),
        ]
        self.join_graph.relationships = relationships

    def get_metric(self, name: str) -> Optional[Metric]:
        return self.metrics.get(name)

    def get_dimension(self, name: str) -> Optional[Dimension]:
        return self.dimensions.get(name)

    def get_entity(self, name: str) -> Optional[Entity]:
        return self.entities.get(name)

    def find_join_path(self, start_entity: str, end_entity: str) -> Optional[List[Relationship]]:
        """Finds shortest valid join path between two entities in the join graph."""
        if start_entity == end_entity:
            return []
        
        visited = set()
        queue = [(start_entity, [])]
        
        while queue:
            curr_entity, path = queue.pop(0)
            if curr_entity == end_entity:
                return path
            
            if curr_entity in visited:
                continue
            visited.add(curr_entity)
            
            for rel in self.join_graph.relationships:
                neighbor = None
                rel_directed = rel
                if rel.from_entity == curr_entity and rel.to_entity not in visited:
                    neighbor = rel.to_entity
                elif rel.to_entity == curr_entity and rel.from_entity not in visited:
                    neighbor = rel.from_entity
                    # Reversed relationship
                    rel_directed = Relationship(
                        from_entity=rel.to_entity,
                        to_entity=rel.from_entity,
                        join_type=rel.join_type,
                        from_key=rel.to_key,
                        to_key=rel.from_key,
                        cardinality="one_to_many" if rel.cardinality == "many_to_one" else "many_to_one",
                    )
                
                if neighbor:
                    queue.append((neighbor, path + [rel_directed]))
                    
        return None
