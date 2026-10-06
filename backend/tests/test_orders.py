import unittest
from backend.app import create_app
class TestOrders(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()

        # Login admin to obtain token
        login_res = self.client.post("/api/auth/login", json={
            "email": "admin@garment.com",
            "password": "Admin@123"
        })
        self.token = login_res.get_json()["data"]["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_get_orders(self):
        """Test getting orders list."""
        res = self.client.get("/api/orders", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertGreater(data["count"], 0)

    def test_create_order_auto_initializes_production(self):
        """Test creating an order automatically creates all 6 production stages."""
        payload = {
            "customerName": "Test Customer",
            "customerContact": "1234567890",
            "productName": "Oxford Formal Shirt",
            "productType": "Shirt",
            "quantity": 500,
            "deadline": "2026-12-31",
            "priority": "High"
        }
        res = self.client.post("/api/orders", json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data["success"])
        order_id = data["data"]["orderId"]

        # Check order details and stages
        detail_res = self.client.get(f"/api/orders/{order_id}", headers=self.headers)
        self.assertEqual(detail_res.status_code, 200)
        detail_data = detail_res.get_json()["data"]
        self.assertEqual(detail_data["customerName"], "Test Customer")
        self.assertEqual(len(detail_data["stages"]), 6)
        
        # Verify Cutting is In Progress and others are Pending
        stages = detail_data["stages"]
        self.assertEqual(stages[0]["stage"], "Cutting")
        self.assertEqual(stages[0]["status"], "In Progress")
        self.assertEqual(stages[1]["stage"], "Stitching")
        self.assertEqual(stages[1]["status"], "Pending")

    def test_create_order_validation_error(self):
        """Test validation error when required fields are missing or quantity is invalid."""
        res = self.client.post("/api/orders", json={
            "customerName": "",
            "productName": "Shirt",
            "quantity": -5
        }, headers=self.headers)
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "VALIDATION_ERROR")

if __name__ == "__main__":
    unittest.main()
