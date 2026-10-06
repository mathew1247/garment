import unittest
from backend.app import create_app

class TestFirestoreE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()

    def test_complete_scenario_on_cloud_firestore(self):
        """
        Execute Section 49 complete scenario on Cloud Firestore:
        1. Login/authenticate
        2. Create employee
        3. Create product
        4. Create inventory
        5. Create order (auto-creates 6 stages)
        6. Worker assignment to Cutting
        7. Start Cutting -> Complete Cutting
        8. Start Stitching -> Complete Stitching
        9. Start Finishing -> Complete Finishing
        10. Perform Quality Check (FAIL -> Rework scenario)
        11. Re-inspect Quality Check (PASS scenario)
        12. Packaging (gated by QC Pass)
        13. Dispatch (gated by Packaging Complete)
        14. Order Completed
        15. Verify dashboard, reports, notifications, audit logs
        """
        client = self.client

        # 1. Login / Authenticate
        login_res = client.post("/api/auth/login", json={
            "email": "admin@garment.com",
            "password": "Admin@123"
        })
        self.assertEqual(login_res.status_code, 200)
        token = login_res.get_json()["data"]["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Verify /api/auth/me
        me_res = client.get("/api/auth/me", headers=headers)
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.get_json()["data"]["role"], "Administrator")

        # 2. Create employee
        emp_res = client.post("/api/employees", json={
            "name": "Arun Kumar",
            "department": "Cutting",
            "role": "Laser Cutter Specialist",
            "phone": "9876500001",
            "email": "arun.cutter@garment.com"
        }, headers=headers)
        self.assertEqual(emp_res.status_code, 201)
        emp_id = emp_res.get_json()["data"]["employeeId"]
        self.assertTrue(emp_id.startswith("EMP"))

        # 3. Create product
        prod_res = client.post("/api/products", json={
            "productCode": "E2E-HOODIE-01",
            "productName": "Fleece Zip Hoodie",
            "productType": "Hoodie",
            "description": "Heavyweight organic cotton fleece hoodie",
            "fabricType": "350 GSM Organic Fleece",
            "availableSizes": ["M", "L", "XL"],
            "colors": ["Heather Grey", "Black"]
        }, headers=headers)
        self.assertEqual(prod_res.status_code, 201)
        product_id = prod_res.get_json()["data"]["productId"]
        self.assertTrue(product_id.startswith("PRD"))

        # 4. Create inventory material
        mat_res = client.post("/api/inventory", json={
            "materialName": "Heavy Organic Fleece (Heather Grey)",
            "category": "Raw Materials",
            "quantity": 1500,
            "unit": "meters",
            "minimumStock": 300,
            "supplier": "Eco Knits Global"
        }, headers=headers)
        self.assertEqual(mat_res.status_code, 201)
        mat_id = mat_res.get_json()["data"]["materialId"]
        self.assertTrue(mat_id.startswith("MAT"))

        # Stock IN and Stock OUT test
        stock_in_res = client.post(f"/api/inventory/{mat_id}/stock-in", json={
            "quantity": 200,
            "reason": "Replenishment roll received"
        }, headers=headers)
        self.assertEqual(stock_in_res.status_code, 200)

        stock_out_res = client.post(f"/api/inventory/{mat_id}/stock-out", json={
            "quantity": 100,
            "reason": "Test sample cutting"
        }, headers=headers)
        self.assertEqual(stock_out_res.status_code, 200)

        # 5. Create order (auto-provisions 6 sequential stages)
        order_res = client.post("/api/orders", json={
            "customerName": "Nordic Apparel Co",
            "customerContact": "9123456780",
            "productId": product_id,
            "productName": "Fleece Zip Hoodie",
            "productType": "Hoodie",
            "quantity": 300,
            "deadline": "2026-12-10",
            "priority": "High"
        }, headers=headers)
        self.assertEqual(order_res.status_code, 201)
        order_id = order_res.get_json()["data"]["orderId"]

        # Fetch stages
        stages_res = client.get(f"/api/production/{order_id}", headers=headers)
        self.assertEqual(stages_res.status_code, 200)
        stages = stages_res.get_json()["data"]
        self.assertEqual(len(stages), 6)
        c_stage = stages[0]  # Cutting
        s_stage = stages[1]  # Stitching
        f_stage = stages[2]  # Finishing
        q_stage = stages[3]  # Quality Check
        p_stage = stages[4]  # Packaging
        d_stage = stages[5]  # Dispatch

        # 6. Assign worker to Cutting
        asn_res = client.post("/api/assignments", json={
            "employeeId": emp_id,
            "orderId": order_id,
            "productionId": c_stage["productionId"],
            "stage": "Cutting",
            "task": "Cut hoodie body patterns",
            "quantity": 300
        }, headers=headers)
        self.assertEqual(asn_res.status_code, 201)

        # 7. Start Cutting -> Complete Cutting
        start_c = client.post(f"/api/production/{c_stage['productionId']}/start", json={}, headers=headers)
        self.assertEqual(start_c.status_code, 200)

        comp_c = client.post(f"/api/production/{c_stage['productionId']}/complete", json={
            "completedQuantity": 300,
            "remarks": "Cutting 100% finished"
        }, headers=headers)
        self.assertEqual(comp_c.status_code, 200)

        # 8. Stitching is now In Progress -> Complete Stitching
        comp_s = client.post(f"/api/production/{s_stage['productionId']}/complete", json={
            "completedQuantity": 300,
            "remarks": "Zippers and hood stitched"
        }, headers=headers)
        self.assertEqual(comp_s.status_code, 200)

        # 9. Finishing is now In Progress -> Complete Finishing
        comp_f = client.post(f"/api/production/{f_stage['productionId']}/complete", json={
            "completedQuantity": 300,
            "remarks": "Trimmed & pressed"
        }, headers=headers)
        self.assertEqual(comp_f.status_code, 200)

        # 10. Perform Quality Check -> Test FAIL (Rework cycle)
        qc_fail_res = client.post("/api/quality-checks", json={
            "orderId": order_id,
            "inspectorId": "EMP004",
            "result": "Fail",
            "defectType": "Pocket Seam Misalignment",
            "defectQuantity": 8,
            "reworkStage": "Stitching",
            "remarks": "Re-align pocket seams on 8 units"
        }, headers=headers)
        self.assertEqual(qc_fail_res.status_code, 201)

        # Verify Packaging is rejected during Rework/Fail
        pkg_blocked_res = client.post("/api/packaging", json={
            "orderId": order_id,
            "quantity": 300
        }, headers=headers)
        self.assertEqual(pkg_blocked_res.status_code, 400)
        self.assertEqual(pkg_blocked_res.get_json()["error"], "QC_NOT_PASSED")

        # 11. Re-work and re-inspect -> Test PASS
        qc_pass_res = client.post("/api/quality-checks", json={
            "orderId": order_id,
            "inspectorId": "EMP004",
            "result": "Pass",
            "defectType": "None",
            "defectQuantity": 0,
            "remarks": "All 300 units passed re-inspection"
        }, headers=headers)
        self.assertEqual(qc_pass_res.status_code, 201)

        # 12. Packaging is now allowed
        pkg_res = client.post("/api/packaging", json={
            "orderId": order_id,
            "quantity": 300,
            "remarks": "Individually polybagged and boxed"
        }, headers=headers)
        self.assertEqual(pkg_res.status_code, 201)

        # 13. Dispatch
        dsp_res = client.post("/api/dispatch", json={
            "orderId": order_id,
            "deliveryInformation": "Nordic Logistics Terminal, Bengaluru Airport",
            "remarks": "Air freight flight #AI182"
        }, headers=headers)
        self.assertEqual(dsp_res.status_code, 201)

        # 14. Verify order is now Completed
        ord_check = client.get(f"/api/orders/{order_id}", headers=headers)
        self.assertEqual(ord_check.status_code, 200)
        self.assertEqual(ord_check.get_json()["data"]["status"], "Completed")
        self.assertEqual(ord_check.get_json()["data"]["currentStage"], "Completed")

        # 15. Verify Dashboard
        dash_res = client.get("/api/dashboard", headers=headers)
        self.assertEqual(dash_res.status_code, 200)
        dash_data = dash_res.get_json()["data"]
        self.assertIn("totalOrders", dash_data)
        self.assertIn("productionStages", dash_data)
        self.assertIn("recentActivities", dash_data)
        self.assertGreater(len(dash_data["recentActivities"]), 0)

        # 16. Verify Reports
        rep_p = client.get("/api/reports/production", headers=headers)
        self.assertEqual(rep_p.status_code, 200)
        rep_o = client.get("/api/reports/orders", headers=headers)
        self.assertEqual(rep_o.status_code, 200)
        rep_e = client.get("/api/reports/employees", headers=headers)
        self.assertEqual(rep_e.status_code, 200)
        rep_i = client.get("/api/reports/inventory", headers=headers)
        self.assertEqual(rep_i.status_code, 200)

        # 17. Verify Notifications
        notifs_res = client.get("/api/notifications", headers=headers)
        self.assertEqual(notifs_res.status_code, 200)
        self.assertGreater(len(notifs_res.get_json()["data"]), 0)

if __name__ == "__main__":
    unittest.main()
