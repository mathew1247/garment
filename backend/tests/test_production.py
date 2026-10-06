import unittest
from backend.app import create_app
class TestProduction(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()

        login_res = self.client.post("/api/auth/login", json={
            "email": "manager@garment.com",
            "password": "Manager@123"
        })
        self.token = login_res.get_json()["data"]["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_production_workflow_sequence(self):
        """Test complete stage transition and sequence enforcement."""
        # 1. Create a fresh order
        order_res = self.client.post("/api/orders", json={
            "customerName": "Workflow Corp",
            "customerContact": "9000000000",
            "productName": "Workflow Denim Jeans",
            "productType": "Pants",
            "quantity": 200,
            "deadline": "2026-11-30"
        }, headers=self.headers)
        order_id = order_res.get_json()["data"]["orderId"]

        # Fetch stages
        prod_res = self.client.get(f"/api/production/{order_id}", headers=self.headers)
        stages = prod_res.get_json()["data"]
        cutting_stage = stages[0]
        stitching_stage = stages[1]
        finishing_stage = stages[2]

        self.assertEqual(cutting_stage["stage"], "Cutting")
        self.assertEqual(cutting_stage["status"], "In Progress")

        # 2. Try to start Finishing directly (should fail because previous stages are not completed)
        finishing_start_res = self.client.post(
            f"/api/production/{finishing_stage['productionId']}/start",
            json={},
            headers=self.headers
        )
        self.assertEqual(finishing_start_res.status_code, 400)
        self.assertEqual(finishing_start_res.get_json()["error"], "INVALID_SEQUENCE")

        # 3. Complete Cutting stage
        complete_cutting_res = self.client.post(
            f"/api/production/{cutting_stage['productionId']}/complete",
            json={"completedQuantity": 200, "remarks": "Cutting completed smoothly"},
            headers=self.headers
        )
        self.assertEqual(complete_cutting_res.status_code, 200)

        # 4. Verify Stitching is now In Progress
        stitching_check = self.client.get(f"/api/production/{stitching_stage['productionId']}", headers=self.headers)
        self.assertEqual(stitching_check.get_json()["data"]["status"], "In Progress")

if __name__ == "__main__":
    unittest.main()
