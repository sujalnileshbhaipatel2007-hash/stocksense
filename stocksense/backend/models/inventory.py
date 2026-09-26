from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


OperationKind = Literal["receipt", "delivery", "transfer", "adjustment"]
OperationStatus = Literal["draft", "ready", "done", "canceled"]


class ProductBase(BaseModel):
    name: str
    sku: str
    category: str
    uom: str
    reorder_threshold: int = Field(ge=0)


class ProductCreate(ProductBase):
    stock_by_location: dict[str, int] = Field(default_factory=dict)


class Product(ProductBase):
    id: str
    stock_by_location: dict[str, int] = Field(default_factory=dict)
    total_stock: int = 0
    stock_status: Literal["in_stock", "low_stock", "out_of_stock"] = "in_stock"
    created_at: datetime
    updated_at: datetime


class WarehouseCreate(BaseModel):
    name: str
    code: str
    location: str
    capacity: int = Field(default=1000, ge=0)


class Warehouse(WarehouseCreate):
    id: str
    created_at: datetime


class OperationLine(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)


class OperationCreate(BaseModel):
    kind: OperationKind
    partner: str = ""
    source_location: str = ""
    destination_location: str = ""
    lines: list[OperationLine] = Field(min_length=1)
    physical_count: int | None = Field(default=None, ge=0)
    reason: str = ""


class Operation(OperationCreate):
    id: str
    number: str
    status: OperationStatus = "draft"
    created_at: datetime
    updated_at: datetime


class LedgerEntry(BaseModel):
    id: str
    operation_id: str
    operation_number: str
    movement_type: str
    product_id: str
    product_name: str
    sku: str
    quantity_delta: int
    source_location: str = ""
    destination_location: str = ""
    user_email: str
    created_at: datetime


class DashboardKpis(BaseModel):
    total_units: int
    total_products: int
    low_stock_count: int
    pending_receipts: int
    pending_deliveries: int
    scheduled_transfers: int


class Dashboard(BaseModel):
    kpis: DashboardKpis
    low_stock_products: list[Product]
    recent_movements: list[LedgerEntry]
    pending_operations: list[Operation]