"""Enterprise Synthetic Warehouse Generator with calibrated Kerala Q2 product churn scenario."""

from __future__ import annotations

import datetime
import os
import random
from typing import Dict, List, Tuple
import duckdb
import pandas as pd


class SyntheticWarehouseGenerator:
    """Generates 8 relational tables calibrated for realistic business analytics."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)

    def generate_all_tables(self) -> Dict[str, pd.DataFrame]:
        # 1. Geography
        geographies = [
            # Kerala
            {"geo_id": "GEO_KL_01", "state": "Kerala", "district": "Ernakulam", "region": "South"},
            {"geo_id": "GEO_KL_02", "state": "Kerala", "district": "Thiruvananthapuram", "region": "South"},
            {"geo_id": "GEO_KL_03", "state": "Kerala", "district": "Kozhikode", "region": "South"},
            # Karnataka
            {"geo_id": "GEO_KA_01", "state": "Karnataka", "district": "Bangalore Urban", "region": "South"},
            {"geo_id": "GEO_KA_02", "state": "Karnataka", "district": "Mysore", "region": "South"},
            # Maharashtra
            {"geo_id": "GEO_MH_01", "state": "Maharashtra", "district": "Mumbai", "region": "West"},
            {"geo_id": "GEO_MH_02", "state": "Maharashtra", "district": "Pune", "region": "West"},
            # Tamil Nadu
            {"geo_id": "GEO_TN_01", "state": "Tamil Nadu", "district": "Chennai", "region": "South"},
        ]
        df_geo = pd.DataFrame(geographies)

        # 2. Products
        products = [
            {"product_id": "PRD_101", "product_name": "Cloud Storage Starter", "category": "Infrastructure", "base_price": 49.0},
            {"product_id": "PRD_102", "product_name": "Enterprise Suite Pro", "category": "Software", "base_price": 499.0},
            {"product_id": "PRD_103", "product_name": "Analytics Pro Dashboard", "category": "Analytics", "base_price": 199.0},
            {"product_id": "PRD_104", "product_name": "Developer API Access", "category": "Developer Tools", "base_price": 99.0},
            {"product_id": "PRD_105", "product_name": "Security Compliance Shield", "category": "Security", "base_price": 299.0},
        ]
        df_products = pd.DataFrame(products)

        # 3. Customers
        customers = []
        customer_count = 1000
        segments = ["Enterprise", "Mid-Market", "SMB"]
        segment_weights = [0.15, 0.35, 0.50]

        for i in range(1, customer_count + 1):
            cid = f"CUST_{i:04d}"
            geo = random.choice(geographies)
            seg = random.choices(segments, weights=segment_weights)[0]
            signup_date = datetime.date(2023, 1, 1) + datetime.timedelta(days=random.randint(0, 360))
            customers.append({
                "customer_id": cid,
                "customer_name": f"Account {i}",
                "geo_id": geo["geo_id"],
                "segment": seg,
                "signup_date": signup_date.isoformat(),
            })
        df_customers = pd.DataFrame(customers)

        # 4. Orders and Order Items
        orders = []
        order_items = []
        order_id_counter = 1
        item_id_counter = 1

        start_date = datetime.date(2024, 1, 1)
        end_date = datetime.date(2024, 9, 30)
        curr = start_date

        while curr <= end_date:
            date_str = curr.isoformat()
            quarter = f"Q{(curr.month - 1) // 3 + 1}"
            
            # Daily orders
            num_daily_orders = random.randint(15, 30)
            for _ in range(num_daily_orders):
                cust = random.choice(customers)
                oid = f"ORD_{order_id_counter:06d}"
                order_id_counter += 1

                # Calculate realistic delivery days:
                # Calibrated anomaly: In Q2 2024 in Kerala, delivery days spike to 11.5 days due to logistics bottleneck
                is_kerala = cust["geo_id"].startswith("GEO_KL")
                if quarter == "Q2" and is_kerala:
                    delivery_days = round(random.gauss(11.8, 2.0), 1)
                else:
                    delivery_days = round(random.gauss(2.8, 0.8), 1)
                delivery_days = max(1.0, delivery_days)

                order_total = 0.0
                num_items = random.randint(1, 3)
                for _ in range(num_items):
                    prod = random.choice(products)
                    qty = random.randint(1, 4)
                    unit_price = prod["base_price"]
                    net_amt = qty * unit_price
                    order_total += net_amt

                    order_items.append({
                        "item_id": f"ITEM_{item_id_counter:07d}",
                        "order_id": oid,
                        "product_id": prod["product_id"],
                        "quantity": qty,
                        "unit_price": unit_price,
                        "net_amount": net_amt,
                    })
                    item_id_counter += 1

                orders.append({
                    "order_id": oid,
                    "customer_id": cust["customer_id"],
                    "order_date": date_str,
                    "quarter": quarter,
                    "year": curr.year,
                    "status": "COMPLETED",
                    "delivery_days": delivery_days,
                    "total_amount": round(order_total, 2),
                })

            curr += datetime.timedelta(days=1)

        df_orders = pd.DataFrame(orders)
        df_order_items = pd.DataFrame(order_items)

        # 5. Churn Events (Calibrated Scenario: Kerala in Q2 product loss)
        churn_events = []
        churn_id_counter = 1

        # Customer churn across Q1, Q2, Q3
        # Baseline churn is ~10-15 per state per quarter
        # In Kerala Q2: Churn jumps to 78 customers, with Enterprise Suite Pro (PRD_102) driving 58 of them (~74%)
        for cust in customers:
            is_kerala = cust["geo_id"].startswith("GEO_KL")
            cid = cust["customer_id"]

            # Q1 Churn
            if random.random() < 0.015:
                p = random.choice(products)
                churn_events.append({
                    "churn_id": f"CHURN_{churn_id_counter:04d}",
                    "customer_id": cid,
                    "product_id": p["product_id"],
                    "churn_date": "2024-02-15",
                    "quarter": "Q1",
                    "churn_reason": "Feature Gap",
                })
                churn_id_counter += 1

            # Q2 Churn
            if is_kerala:
                # Calibrated surge in Kerala Q2: High churn probability specifically for PRD_102
                if random.random() < 0.22:
                    p = next(x for x in products if x["product_id"] == "PRD_102") if random.random() < 0.74 else random.choice(products)
                    churn_events.append({
                        "churn_id": f"CHURN_{churn_id_counter:04d}",
                        "customer_id": cid,
                        "product_id": p["product_id"],
                        "churn_date": "2024-05-18",
                        "quarter": "Q2",
                        "churn_reason": "Logistics Latency" if p["product_id"] == "PRD_102" else "Pricing Friction",
                    })
                    churn_id_counter += 1
            else:
                # Normal baseline for other states in Q2
                if random.random() < 0.018:
                    p = random.choice(products)
                    churn_events.append({
                        "churn_id": f"CHURN_{churn_id_counter:04d}",
                        "customer_id": cid,
                        "product_id": p["product_id"],
                        "churn_date": "2024-05-10",
                        "quarter": "Q2",
                        "churn_reason": "Budget Cuts",
                    })
                    churn_id_counter += 1

            # Q3 Churn
            if random.random() < 0.016:
                p = random.choice(products)
                churn_events.append({
                    "churn_id": f"CHURN_{churn_id_counter:04d}",
                    "customer_id": cid,
                    "product_id": p["product_id"],
                    "churn_date": "2024-08-20",
                    "quarter": "Q3",
                    "churn_reason": "Competitor Switch",
                })
                churn_id_counter += 1

        df_churn = pd.DataFrame(churn_events)

        # 6. Marketing Campaigns
        campaigns = [
            {"campaign_id": "MKT_01", "channel": "Google Search", "region": "South", "spend": 45000.0, "quarter": "Q2"},
            {"campaign_id": "MKT_02", "channel": "LinkedIn B2B", "region": "South", "spend": 60000.0, "quarter": "Q2"},
            {"campaign_id": "MKT_03", "channel": "Direct Sales", "region": "South", "spend": 80000.0, "quarter": "Q2"},
            {"campaign_id": "MKT_04", "channel": "Google Search", "region": "West", "spend": 50000.0, "quarter": "Q2"},
        ]
        df_mkt = pd.DataFrame(campaigns)

        # 7. Calendar Dimension
        calendar = []
        curr = start_date
        while curr <= end_date:
            calendar.append({
                "date": curr.isoformat(),
                "year": curr.year,
                "quarter": f"Q{(curr.month - 1) // 3 + 1}",
                "month": curr.month,
                "day": curr.day,
                "is_weekend": curr.weekday() >= 5,
            })
            curr += datetime.timedelta(days=1)
        df_cal = pd.DataFrame(calendar)

        return {
            "geography": df_geo,
            "products": df_products,
            "customers": df_customers,
            "orders": df_orders,
            "order_items": df_order_items,
            "churn_events": df_churn,
            "marketing_campaigns": df_mkt,
            "calendar_dim": df_cal,
        }

    def seed_duckdb(self, db_path: str = "data/warehouse.duckdb") -> duckdb.DuckDBPyConnection:
        """Saves generated data directly into a DuckDB analytical database."""
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        con = duckdb.connect(db_path)
        tables = self.generate_all_tables()
        for name, df in tables.items():
            con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM df")
        con.commit()
        return con
