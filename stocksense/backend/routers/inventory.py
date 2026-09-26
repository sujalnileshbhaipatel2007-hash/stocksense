import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query

from lib.db import db
from models.auth import AuthUser
from models.inventory import (
    Dashboard, DashboardKpis, LedgerEntry, Operation, OperationCreate, Product, ProductCreate,
    Warehouse, WarehouseCreate,
)
from routers.auth import current_user, manager_user

router = APIRouter(tags=["inventory"])


def now() -> datetime:
    return datetime.now(timezone.utc)


def product_view(doc: dict) -> Product:
    stock = {key: int(value) for key, value in (doc.get("stock_by_location") or {}).items()}
    total = sum(stock.values())
    threshold = int(doc.get("reorder_threshold", 0))
    status = "out_of_stock" if total <= 0 else "low_stock" if total <= threshold else "in_stock"
    return Product(id=doc["id"], name=doc["name"], sku=doc["sku"], category=doc["category"], uom=doc["uom"], reorder_threshold=threshold, stock_by_location=stock, total_stock=total, stock_status=status, created_at=doc["created_at"], updated_at=doc["updated_at"])


def operation_view(doc: dict) -> Operation:
    return Operation(**{key: value for key, value in doc.items() if key != "_id"})


def ledger_view(doc: dict) -> LedgerEntry:
    return LedgerEntry(**{key: value for key, value in doc.items() if key != "_id"})


@router.get("/products", response_model=list[Product])
async def list_products(q: str = "", category: str = "", status: str = "", user: dict = Depends(current_user)):
    docs = await db.products.find().sort("name", 1).to_list(1000)
    products = [product_view(doc) for doc in docs]
    query = q.lower().strip()
    return [product for product in products if (not query or query in product.name.lower() or query in product.sku.lower()) and (not category or product.category == category) and (not status or product.stock_status == status)]


@router.post("/products", response_model=Product)
async def create_product(payload: ProductCreate, user: dict = Depends(manager_user)):
    if await db.products.find_one({"sku": payload.sku}):
        raise HTTPException(status_code=409, detail="SKU already exists")
    timestamp = now()
    doc = {"id": str(uuid.uuid4()), **payload.model_dump(), "created_at": timestamp, "updated_at": timestamp}
    await db.products.insert_one(doc)
    return product_view(doc)


@router.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, payload: ProductCreate, user: dict = Depends(manager_user)):
    existing = await db.products.find_one({"id": product_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")
    await db.products.update_one({"id": product_id}, {"$set": {**payload.model_dump(), "updated_at": now()}})
    return product_view(await db.products.find_one({"id": product_id}))


@router.get("/warehouses", response_model=list[Warehouse])
async def list_warehouses(user: dict = Depends(current_user)):
    return [Warehouse(**{key: value for key, value in doc.items() if key != "_id"}) for doc in await db.warehouses.find().sort("name", 1).to_list(100)]


@router.post("/warehouses", response_model=Warehouse)
async def create_warehouse(payload: WarehouseCreate, user: dict = Depends(manager_user)):
    doc = {"id": str(uuid.uuid4()), **payload.model_dump(), "created_at": now()}
    await db.warehouses.insert_one(doc)
    return Warehouse(**doc)


@router.get("/operations", response_model=list[Operation])
async def list_operations(kind: str = Query(default=""), user: dict = Depends(current_user)):
    query = {"kind": kind} if kind else {}
    docs = await db.operations.find(query).sort("created_at", -1).to_list(500)
    return [operation_view(doc) for doc in docs]


@router.post("/operations", response_model=Operation)
async def create_operation(payload: OperationCreate, user: dict = Depends(current_user)):
    prefix = {"receipt": "REC", "delivery": "DEL", "transfer": "TRF", "adjustment": "ADJ"}[payload.kind]
    count = await db.operations.count_documents({"kind": payload.kind}) + 1001
    timestamp = now()
    doc = {"id": str(uuid.uuid4()), "number": f"{prefix}-{count}", **payload.model_dump(), "status": "draft", "created_at": timestamp, "updated_at": timestamp}
    await db.operations.insert_one(doc)
    return operation_view(doc)


@router.post("/operations/{operation_id}/validate", response_model=Operation)
async def validate_operation(operation_id: str, user: dict = Depends(manager_user)):
    operation = await db.operations.find_one({"id": operation_id})
    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")
    if operation["status"] == "done":
        return operation_view(operation)
    for line in operation["lines"]:
        product = await db.products.find_one({"id": line["product_id"]})
        if not product:
            raise HTTPException(status_code=404, detail="Product in operation not found")
        stock = {key: int(value) for key, value in (product.get("stock_by_location") or {}).items()}
        qty = int(line["quantity"])
        source = operation.get("source_location", "")
        destination = operation.get("destination_location", "")
        movement_type = operation["kind"].upper()
        delta = qty
        if operation["kind"] == "receipt":
            destination = destination or "WH-CEN"
            stock[destination] = stock.get(destination, 0) + qty
        elif operation["kind"] == "delivery":
            source = source or "WH-CEN"
            if stock.get(source, 0) < qty:
                raise HTTPException(status_code=400, detail=f"Not enough stock in {source} for {product['sku']}")
            stock[source] = stock.get(source, 0) - qty
            delta = -qty
        elif operation["kind"] == "transfer":
            if stock.get(source, 0) < qty:
                raise HTTPException(status_code=400, detail=f"Not enough stock in {source} for {product['sku']}")
            stock[source] = stock.get(source, 0) - qty
            stock[destination] = stock.get(destination, 0) + qty
            await db.ledger.insert_one({"id": str(uuid.uuid4()), "operation_id": operation["id"], "operation_number": operation["number"], "movement_type": "TRANSFER OUT", "product_id": product["id"], "product_name": product["name"], "sku": product["sku"], "quantity_delta": -qty, "source_location": source, "destination_location": destination, "user_email": user["email"], "created_at": now()})
            movement_type = "TRANSFER IN"
        elif operation["kind"] == "adjustment":
            destination = destination or source or "WH-CEN"
            previous = stock.get(destination, 0)
            target = int(operation.get("physical_count") if operation.get("physical_count") is not None else qty)
            delta = target - previous
            stock[destination] = target
        await db.products.update_one({"id": product["id"]}, {"$set": {"stock_by_location": stock, "updated_at": now()}})
        await db.ledger.insert_one({"id": str(uuid.uuid4()), "operation_id": operation["id"], "operation_number": operation["number"], "movement_type": movement_type, "product_id": product["id"], "product_name": product["name"], "sku": product["sku"], "quantity_delta": delta, "source_location": source, "destination_location": destination, "user_email": user["email"], "created_at": now()})
    await db.operations.update_one({"id": operation_id}, {"$set": {"status": "done", "updated_at": now()}})
    return operation_view(await db.operations.find_one({"id": operation_id}))


@router.get("/ledger", response_model=list[LedgerEntry])
async def list_ledger(user: dict = Depends(current_user)):
    docs = await db.ledger.find().sort("created_at", -1).to_list(500)
    return [ledger_view(doc) for doc in docs]


@router.get("/dashboard", response_model=Dashboard)
async def dashboard(user: dict = Depends(current_user)):
    products = [product_view(doc) for doc in await db.products.find().sort("name", 1).to_list(1000)]
    operations = [operation_view(doc) for doc in await db.operations.find().sort("created_at", -1).to_list(500)]
    ledger = [ledger_view(doc) for doc in await db.ledger.find().sort("created_at", -1).to_list(10)]
    pending = [op for op in operations if op.status in ("draft", "ready")]
    return Dashboard(kpis=DashboardKpis(total_units=sum(item.total_stock for item in products), total_products=len(products), low_stock_count=sum(item.stock_status != "in_stock" for item in products), pending_receipts=sum(op.kind == "receipt" for op in pending), pending_deliveries=sum(op.kind == "delivery" for op in pending), scheduled_transfers=sum(op.kind == "transfer" for op in pending)), low_stock_products=[item for item in products if item.stock_status != "in_stock"], recent_movements=ledger, pending_operations=pending[:6])


@router.post("/demo/reset")
async def reset_demo(user: dict = Depends(manager_user)):
    from lib.demo_data import seed_demo_data
    await seed_demo_data(force=True)
    return {"message": "Demo workspace reset"}