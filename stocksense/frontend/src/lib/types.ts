export interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: string;
}

export interface AuthResponse {
  user: AuthUser;
  message?: string | null;
  verification_required: boolean;
  demo_code?: string | null;
}

export type StockStatus = "in_stock" | "low_stock" | "out_of_stock";
export type OperationKind = "receipt" | "delivery" | "transfer" | "adjustment";
export type OperationStatus = "draft" | "ready" | "done" | "canceled";

export interface Product {
  id: string;
  name: string;
  sku: string;
  category: string;
  uom: string;
  reorder_threshold: number;
  stock_by_location: Record<string, number>;
  total_stock: number;
  stock_status: StockStatus;
  created_at: string;
  updated_at: string;
}

export interface Warehouse {
  id: string;
  name: string;
  code: string;
  location: string;
  capacity: number;
  created_at: string;
}

export interface OperationLine {
  product_id: string;
  quantity: number;
}

export interface Operation {
  id: string;
  number: string;
  kind: OperationKind;
  partner: string;
  source_location: string;
  destination_location: string;
  lines: OperationLine[];
  physical_count?: number | null;
  reason: string;
  status: OperationStatus;
  created_at: string;
  updated_at: string;
}

export interface LedgerEntry {
  id: string;
  operation_id: string;
  operation_number: string;
  movement_type: string;
  product_id: string;
  product_name: string;
  sku: string;
  quantity_delta: number;
  source_location: string;
  destination_location: string;
  user_email: string;
  created_at: string;
}

export interface DashboardKpis {
  total_units: number;
  total_products: number;
  low_stock_count: number;
  pending_receipts: number;
  pending_deliveries: number;
  scheduled_transfers: number;
}

export interface Dashboard {
  kpis: DashboardKpis;
  low_stock_products: Product[];
  recent_movements: LedgerEntry[];
  pending_operations: Operation[];
}