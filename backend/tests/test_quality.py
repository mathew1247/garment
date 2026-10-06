import unittest
from backend.app import create_app
class TestQualityAndPackaging(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()

        login_res = self.client.post("/api/auth/login", json={
            "email": "manager@garment.com",
            "password": "Manager@123"
        })
        self.token = login_res.get_json()["data"]["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_packaging_rejected_before_quality_pass(self):
        """Packaging must NOT be allowed until quality is passed."""
        # ORD001 is only in Cutting stage
        res = self.client.post("/api/packaging", json={
            "orderId": "ORD001",
            "quantity": 1000
        }, headers=self.headers)
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "QC_NOT_PASSED")

    def test_quality_pass_and_full_workflow_to_dispatch(self):
        """Test Quality Pass -> Packaging -> Dispatch -> Order Completed."""
        # In mock data, ORD002 is at Quality Check stage with Finishing completed!
        qc_res = self.client.post("/api/quality-checks", json={
            "orderId": "ORD002",
            "inspectorId": "EMP004",
            "result": "Pass",
            "defectType": "None",
            "defectQuantity": 0,
            "remarks": "Passed 100% inspection"
        }, headers=self.headers)
        self.assertEqual(qc_res.status_code, 201)

        # Now Packaging should be allowed
        pkg_res = self.client.post("/api/packaging", json={
            "orderId": "ORD002",
            "quantity": 500,
            "remarks": "Carton packed"
        }, headers=self.headers)
        self.assertEqual(pkg_res.status_code, 201)

        # Now Dispatch should be allowed
        dsp_res = self.client.post("/api/dispatch", json={
            "orderId": "ORD002",
            "deliveryInformation": "Mumbai Retail Warehouse",
            "remarks": "Dispatched via road carrier"
        }, headers=self.headers)
        self.assertEqual(dsp_res.status_code, 201)

        # Check Order status is now Completed!
        order_res = self.client.get("/api/orders/ORD002", headers=self.headers)
        order_data = order_res.get_json()["data"]
        self.assertEqual(order_data["status"], "Completed")
        self.assertEqual(order_data["currentStage"], "Completed")

    def test_quality_fail_triggers_rework(self):
        """Test Quality Check Fail marks order as Rework."""
        qc_fail_res = self.client.post("/api/quality-checks", json={
            "orderId": "ORD002",
            "inspectorId": "EMP004",
            "result": "Fail",
            "defectType": "Faulty Stitching",
            "defectQuantity": 25,
            "reworkStage": "Stitching",
            "remarks": "Seams unraveling on collar"
        }, headers=self.headers)
        self.assertEqual(qc_fail_res.status_code, 201)

        # Verify order status is Rework
        order_res = self.client.get("/api/orders/ORD002", headers=self.headers)
        order_data = order_res.get_json()["data"]
        self.assertEqual(order_data["status"], "Rework")
        self.assertEqual(order_data["currentStage"], "Stitching")

if __name__ == "__main__":
    unittest.main()
