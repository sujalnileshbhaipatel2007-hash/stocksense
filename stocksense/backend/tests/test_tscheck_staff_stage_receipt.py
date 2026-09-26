"""Warehouse Staff can stage inventory operations (receipt) as a draft."""
import uuid

import httpx

from tests.conftest import api_url

STAFF_CREDS = {"email": "staff@stocksense.demo", "password": "StockSense123!"}


def _login_staff() -> httpx.Client:
    client = httpx.Client(base_url=api_url(), timeout=30.0)
    resp = client.post("/auth/login", json=STAFF_CREDS)
    assert resp.status_code == 200, f"staff login failed: {resp.status_code} {resp.text}"
    return client


def test_staff_can_stage_receipt():
    client = _login_staff()
    try:
        products = client.get("/products").json()
        assert products, "expected seeded products"
        product_id = products[0]["id"]

        payload = {
            "kind": "receipt",
            "partner": f"tscheck-supplier-{uuid.uuid4().hex[:8]}",
            "destination_location": "WH-CEN",
            "lines": [{"product_id": product_id, "quantity": 5}],
        }
        resp = client.post("/operations", json=payload)
        assert resp.status_code == 200, f"staff staging receipt failed: {resp.status_code} {resp.text}"
        operation = resp.json()
        assert operation["status"] == "draft"
        assert operation["kind"] == "receipt"
        assert operation["number"].startswith("REC-")

        # Confirm it shows up in the receipt queue
        listing = client.get("/operations", params={"kind": "receipt"})
        assert listing.status_code == 200
        ids = [op["id"] for op in listing.json()]
        assert operation["id"] in ids
    finally:
        client.close()


def test_staff_cannot_validate_operation():
    """Staff staging + attempting to validate must be rejected with 403."""
    client = _login_staff()
    try:
        products = client.get("/products").json()
        product_id = products[0]["id"]
        payload = {
            "kind": "receipt",
            "partner": f"tscheck-supplier-{uuid.uuid4().hex[:8]}",
            "destination_location": "WH-CEN",
            "lines": [{"product_id": product_id, "quantity": 3}],
        }
        operation = client.post("/operations", json=payload).json()

        resp = client.post(f"/operations/{operation['id']}/validate")
        assert resp.status_code == 403, f"expected 403, got {resp.status_code} {resp.text}"
        assert "Inventory Manager" in resp.text
    finally:
        client.close()
