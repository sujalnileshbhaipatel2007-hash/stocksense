"""Inventory Manager can approve (validate) a staged operation, mutating stock/ledger."""
import uuid

import httpx

from tests.conftest import api_url

MANAGER_CREDS = {"email": "manager@stocksense.demo", "password": "StockSense123!"}


def _login_manager() -> httpx.Client:
    client = httpx.Client(base_url=api_url(), timeout=30.0)
    resp = client.post("/auth/login", json=MANAGER_CREDS)
    assert resp.status_code == 200, f"manager login failed: {resp.status_code} {resp.text}"
    return client


def test_manager_can_approve_staged_receipt():
    client = _login_manager()
    try:
        products = client.get("/products").json()
        product = products[0]
        product_id = product["id"]
        before_stock = int(product["stock_by_location"].get("WH-CEN", 0))

        payload = {
            "kind": "receipt",
            "partner": f"tscheck-approve-{uuid.uuid4().hex[:8]}",
            "destination_location": "WH-CEN",
            "lines": [{"product_id": product_id, "quantity": 7}],
        }
        create_resp = client.post("/operations", json=payload)
        assert create_resp.status_code == 200
        operation = create_resp.json()
        assert operation["status"] == "draft"

        validate_resp = client.post(f"/operations/{operation['id']}/validate")
        assert validate_resp.status_code == 200, f"manager validate failed: {validate_resp.status_code} {validate_resp.text}"
        validated = validate_resp.json()
        assert validated["status"] == "done"

        # Stock updated
        updated_product = client.get("/products").json()
        updated = next(p for p in updated_product if p["id"] == product_id)
        after_stock = int(updated["stock_by_location"].get("WH-CEN", 0))
        assert after_stock == before_stock + 7, f"expected stock {before_stock + 7}, got {after_stock}"

        # Ledger entry appended
        ledger = client.get("/ledger").json()
        matches = [entry for entry in ledger if entry["operation_id"] == operation["id"]]
        assert matches, "expected ledger entry for validated operation"
        assert matches[0]["quantity_delta"] == 7
    finally:
        client.close()
