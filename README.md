# 📦 StockSense

> A modern inventory operations and warehouse management platform built with React, FastAPI, and MongoDB.

StockSense provides a centralized workspace for managing inventory, warehouses, stock movements, operational queues, and audit history.

It is designed to give warehouse teams a clear view of their inventory while providing managers with approval and administrative controls.

---

## ✨ Features

### 📊 Command Center Dashboard

- Total inventory units
- Total products
- Low-stock monitoring
- Pending receipts
- Pending deliveries
- Scheduled transfers
- Recent inventory movements
- Operational overview

### 📦 Product & Inventory Management

- Product catalog
- SKU-based product identification
- Category management
- Stock quantity tracking
- Stock status monitoring
- Product creation and updates
- Low-stock identification

### 🚚 Inventory Operations

StockSense supports multiple inventory operations:

- 📥 Incoming Receipts
- 📤 Outgoing Deliveries
- 🔄 Internal Transfers
- 🛠️ Stock Adjustments

Operations can be staged and validated according to user permissions.

### 🏭 Warehouse Management

- Create warehouse locations
- Warehouse codes
- Physical location tracking
- Capacity tracking
- Warehouse overview
- Role-based management permissions

### 📒 Stock Ledger

The stock ledger provides an audit trail of validated inventory movements.

It records:

- Timestamp
- Movement type
- Product
- SKU
- Quantity change
- Source location
- Destination location
- Operation number
- Operator

### 🔐 Authentication & Authorization

StockSense includes:

- User registration
- Login
- Logout
- Session-based authentication
- OTP verification flow
- Forgot password
- Reset password
- Role-based access control

Supported roles include:

- `Inventory Manager`
- `Warehouse Staff`

Managers have additional permissions for:

- Product management
- Warehouse creation
- Operation approval
- Workspace reset
- Administrative settings

### 🔄 Demo Data

The application automatically supports seeded demo data for:

- Products
- Warehouses
- Operations
- Stock movements
- Ledger entries

Managers can reset the demo workspace from the Settings section.

---

# 🛠️ Tech Stack

## Frontend

- React 19
- TypeScript
- Vite
- Tailwind CSS v4
- React Router
- TanStack Query
- Recharts
- Lucide React
- shadcn/ui
- Motion

## Backend

- Python
- FastAPI
- Pydantic
- Uvicorn
- Python-dotenv
- PyMongo / Motor

## Database

- MongoDB

## Testing

- Pytest
- Playwright

---

# 📁 Project Structure

```text
StockSense/
│
├── backend/
│   ├── lib/
│   │   ├── db.py
│   │   ├── dates.py
│   │   └── demo_data.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   └── inventory.py
│   │
│   ├── tests/
│   ├── .env.example
│   ├── requirements.txt
│   ├── server.py
│   └── pytest.ini
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── lib/
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Login.tsx
│   │   │   └── Workspace.tsx
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   │
│   ├── .env.example
│   ├── package.json
│   ├── vite.config.ts
│   └── yarn.lock
│
├── tests/
│   ├── e2e/
│   ├── fixtures/
│   └── playwright.config.ts
│
├── .gitignore
└── README.md
