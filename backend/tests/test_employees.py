import unittest
from backend.app import create_app
class TestEmployees(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()

        login_res = self.client.post("/api/auth/login", json={
            "email": "admin@garment.com",
            "password": "Admin@123"
        })
        self.token = login_res.get_json()["data"]["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_get_employees_and_performance(self):
        """Test retrieving employees and calculating performance score."""
        res = self.client.get("/api/employees", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreater(data["count"], 0)

        # Performance for EMP001
        perf_res = self.client.get("/api/employees/EMP001/performance", headers=self.headers)
        self.assertEqual(perf_res.status_code, 200)
        perf_data = perf_res.get_json()["data"]
        self.assertEqual(perf_data["employeeId"], "EMP001")
        self.assertIn("completionPercentage", perf_data)
        self.assertIn("qualityScore", perf_data)
        self.assertIn("performanceStatus", perf_data)

    def test_assign_worker(self):
        """Test assigning worker to a production stage."""
        asn_res = self.client.post("/api/assignments", json={
            "employeeId": "EMP002",
            "orderId": "ORD001",
            "productionId": "ORD001_2",
            "stage": "Stitching",
            "task": "Stitch shirts for ORD001",
            "quantity": 1000
        }, headers=self.headers)
        self.assertEqual(asn_res.status_code, 201)
        asn_data = asn_res.get_json()["data"]
        self.assertEqual(asn_data["employeeId"], "EMP002")

if __name__ == "__main__":
    unittest.main()
