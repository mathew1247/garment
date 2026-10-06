import unittest
from backend.app import create_app
class TestInventory(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()

        login_res = self.client.post("/api/auth/login", json={
            "email": "manager@garment.com",
            "password": "Manager@123"
        })
        self.token = login_res.get_json()["data"]["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_stock_in_and_transaction(self):
        """Test increasing stock and verifying transaction creation."""
        # Initial check MAT001
        item_res = self.client.get("/api/inventory/MAT001", headers=self.headers)
        initial_qty = item_res.get_json()["data"]["quantity"]

        # Stock IN 500 units
        in_res = self.client.post("/api/inventory/MAT001/stock-in", json={
            "quantity": 500,
            "reason": "Shipment arrived"
        }, headers=self.headers)
        self.assertEqual(in_res.status_code, 200)
        self.assertEqual(in_res.get_json()["data"]["quantity"], initial_qty + 500)

        # Check transactions
        txns_res = self.client.get("/api/inventory/MAT001/transactions", headers=self.headers)
        self.assertEqual(txns_res.status_code, 200)
        latest_txn = txns_res.get_json()["data"][0]
        self.assertEqual(latest_txn["type"], "IN")
        self.assertEqual(latest_txn["quantity"], 500)

    def test_prevent_negative_inventory(self):
        """Test that stock OUT cannot exceed current quantity."""
        # MAT002 has 800 spools in mock data
        out_res = self.client.post("/api/inventory/MAT002/stock-out", json={
            "quantity": 99999,
            "reason": "Over-allocation"
        }, headers=self.headers)
        self.assertEqual(out_res.status_code, 400)
        data = out_res.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "INSUFFICIENT_STOCK")

if __name__ == "__main__":
    unittest.main()
