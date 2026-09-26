# StockSense MVP

## Product
StockSense is a dark, high-density inventory operations command center for Inventory Managers and Warehouse Staff. It uses realistic seeded data and supports a demo single-workspace experience.

## Data model
- Users: email, hashed password, name, role, verified flag. Demo sessions use an httpOnly `stocksense_session` cookie.
- Products: SKU, name, category, unit of measure, reorder threshold, stock by location, computed total and stock status.
- Warehouses: name, code, descriptive location, capacity.
- Operations: receipt, delivery, transfer, adjustment; lines, locations, partner/reason, status, timestamps.
- Ledger: immutable movement entries with operation number, SKU, quantity delta, route, operator, timestamp.

## Key flows
1. Sign in with a seeded demo account, land on the command center dashboard.
2. Navigate the left operational rail to products, receipts, deliveries, transfers, adjustments, ledger, warehouses, or settings.
3. Staff and managers can stage operations. Only Inventory Managers can approve/validate them; approval mutates stock and appends ledger entries.
4. Inventory Managers can add products and warehouse locations through inline forms; Warehouse Staff have read-only catalog and network views.
5. Managers can reset demo data from Settings for a clean walkthrough; the staff navigation does not expose Settings.

## Auth
Email/password login, signup with OTP verification, and demo password reset code flow. Demo OTP is `123456`. Logout clears the server cookie and the TanStack Query cache.

## Roles
- Inventory Manager: all read access; create/update products; create warehouses; stage and approve operations; reset demo data.
- Warehouse Staff: all read access; stage receipts, deliveries, transfers, and adjustments; cannot mutate catalog/configuration or approve stock-changing operations.
- Manager-only authorization is enforced server-side with HTTP 403 responses, not only hidden in the UI.