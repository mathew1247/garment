import unittest
from backend.app import create_app
class TestDashboardAndReports(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()

        login_res = self.client.post("/api/auth/login", json={
            "email": "manager@garment.com",
            "password": "Manager@123"
        })
        self.token = login_res.get_json()["data"]["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_dashboard_metrics(self):
        """Test dashboard statistics calculation."""
        res = self.client.get("/api/dashboard", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]

        self.assertIn("totalOrders", data)
        self.assertIn("completedOrders", data)
        self.assertIn("productionStages", data)
        self.assertIn("inventory", data)
        self.assertIn("recentOrders", data)

    def test_reports(self):
        """Test production and orders reports."""
        prod_rep = self.client.get("/api/reports/production", headers=self.headers)
        self.assertEqual(prod_rep.status_code, 200)
        self.assertIn("totalProduction", prod_rep.get_json()["data"])

        ord_rep = self.client.get("/api/reports/orders", headers=self.headers)
        self.assertEqual(ord_rep.status_code, 200)
        self.assertIn("totalOrders", ord_rep.get_json()["data"])

    def test_notifications(self):
        """Test retrieving and reading notifications."""
        notifs_res = self.client.get("/api/notifications", headers=self.headers)
        self.assertEqual(notifs_res.status_code, 200)
        notifs = notifs_res.get_json()["data"]
        self.assertGreater(len(notifs), 0)

        # Mark read
        first_id = notifs[0]["notificationId"]
        read_res = self.client.put(f"/api/notifications/{first_id}/read", headers=self.headers)
        self.assertEqual(read_res.status_code, 200)
        self.assertTrue(read_res.get_json()["data"]["isRead"])

if __name__ == "__main__":
    unittest.main()
