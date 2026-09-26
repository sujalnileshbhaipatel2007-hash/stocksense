import hashlib
import os
import uuid
from datetime import datetime, timezone

from lib.db import db


def password_hash(password: str) -> str:
    salt = "stocksense-demo-salt"
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    return password_hash(password) == stored


def now() -> datetime:
    return datetime.now(timezone.utc)


async def seed_demo_data(force: bool = False) -> None:
    if force:
        for collection in ("users", "products", "warehouses", "operations", "ledger"):
            await db[collection].delete_many({})

    if await db.users.count_documents({}) == 0:
        await db.users.insert_many([
            {
                "id": "user-manager",
                "email": "manager@stocksense.demo",
                "name": "Maya Chen",
                "role": "Inventory Manager",
                "password_hash": password_hash("StockSense123!"),
                "verified": True,
            },
            {
                "id": "user-staff",
                "email": "staff@stocksense.demo",
                "name": "Jordan Reyes",
                "role": "Warehouse Staff",
                "password_hash": password_hash("StockSense123!"),
                "verified": True,
            },
        ])

    if await db.warehouses.count_documents({}) == 0:
        timestamp = now()
        await db.warehouses.insert_many([
            {"id": "wh-central", "name": "Central Warehouse", "code": "WH-CEN", "location": "Austin, TX · Zone A", "capacity": 2400, "created_at": timestamp},
            {"id": "wh-west", "name": "West Hub", "code": "WH-WST", "location": "Phoenix, AZ · Zone C", "capacity": 1800, "created_at": timestamp},
            {"id": "wh-retail", "name": "Retail Floor", "code": "RTL-01", "location": "Austin, TX · Front of House", "capacity": 420, "created_at": timestamp},
        ])

    if await db.products.count_documents({}) == 0:
        timestamp = now()
        await db.products.insert_many([
            {"id": "prod-cable", "name": "USB-C Braided Cable", "sku": "SKU-2048-CBL", "category": "Electronics", "uom": "pcs", "reorder_threshold": 120, "stock_by_location": {"WH-CEN": 286, "WH-WST": 94, "RTL-01": 32}, "created_at": timestamp, "updated_at": timestamp},
            {"id": "prod-lamp", "name": "Arc Desk Lamp", "sku": "SKU-7712-LMP", "category": "Workspace", "uom": "pcs", "reorder_threshold": 80, "stock_by_location": {"WH-CEN": 142, "WH-WST": 51, "RTL-01": 18}, "created_at": timestamp, "updated_at": timestamp},
            {"id": "prod-mat", "name": "Recycled Desk Mat", "sku": "SKU-3890-MAT", "category": "Workspace", "uom": "pcs", "reorder_threshold": 60, "stock_by_location": {"WH-CEN": 78, "WH-WST": 23, "RTL-01": 12}, "created_at": timestamp, "updated_at": timestamp},
            {"id": "prod-bottle", "name": "Insulated Water Bottle", "sku": "SKU-1134-BTL", "category": "Lifestyle", "uom": "pcs", "reorder_threshold": 100, "stock_by_location": {"WH-CEN": 0, "WH-WST": 46, "RTL-01": 9}, "created_at": timestamp, "updated_at": timestamp},
            {"id": "prod-notebook", "name": "Dot Grid Notebook", "sku": "SKU-9051-NBK", "category": "Stationery", "uom": "pcs", "reorder_threshold": 90, "stock_by_location": {"WH-CEN": 211, "WH-WST": 76, "RTL-01": 28}, "created_at": timestamp, "updated_at": timestamp},
        ])

    if await db.operations.count_documents({}) == 0:
        timestamp = now()
        await db.operations.insert_many([
            {"id": "op-rec-1001", "number": "REC-1001", "kind": "receipt", "partner": "Northstar Supply Co.", "source_location": "", "destination_location": "WH-CEN", "lines": [{"product_id": "prod-cable", "quantity": 240}], "physical_count": None, "reason": "", "status": "ready", "created_at": timestamp, "updated_at": timestamp},
            {"id": "op-del-2041", "number": "DEL-2041", "kind": "delivery", "partner": "Orbit Office Group", "source_location": "WH-CEN", "destination_location": "", "lines": [{"product_id": "prod-lamp", "quantity": 36}], "physical_count": None, "reason": "", "status": "draft", "created_at": timestamp, "updated_at": timestamp},
            {"id": "op-trf-3102", "number": "TRF-3102", "kind": "transfer", "partner": "", "source_location": "WH-CEN", "destination_location": "WH-WST", "lines": [{"product_id": "prod-notebook", "quantity": 40}], "physical_count": None, "reason": "Rebalance west hub", "status": "ready", "created_at": timestamp, "updated_at": timestamp},
        ])
        await db.ledger.insert_many([
            {"id": str(uuid.uuid4()), "operation_id": "seed", "operation_number": "OPEN-001", "movement_type": "RECEIPT", "product_id": "prod-cable", "product_name": "USB-C Braided Cable", "sku": "SKU-2048-CBL", "quantity_delta": 420, "source_location": "Vendor", "destination_location": "WH-CEN", "user_email": "system@stocksense.demo", "created_at": timestamp},
            {"id": str(uuid.uuid4()), "operation_id": "seed", "operation_number": "OPEN-002", "movement_type": "TRANSFER IN", "product_id": "prod-mat", "product_name": "Recycled Desk Mat", "sku": "SKU-3890-MAT", "quantity_delta": 90, "source_location": "WH-WST", "destination_location": "WH-CEN", "user_email": "system@stocksense.demo", "created_at": timestamp},
            {"id": str(uuid.uuid4()), "operation_id": "seed", "operation_number": "OPEN-003", "movement_type": "DELIVERY", "product_id": "prod-lamp", "product_name": "Arc Desk Lamp", "sku": "SKU-7712-LMP", "quantity_delta": -18, "source_location": "WH-CEN", "destination_location": "Orbit Office Group", "user_email": "system@stocksense.demo", "created_at": timestamp},
        ])