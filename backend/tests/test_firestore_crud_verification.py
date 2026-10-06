import unittest
from backend.app import create_app
from backend.firebase.firebase_config import db

class TestFirestoreCrudVerification(unittest.TestCase):
    """
    Dedicated test suite for validating all CRUD operations directly against
    real Google Cloud Firestore (project: garmentmanager-ae69f).
    """

    @classmethod
    def cleanup_test_data(cls):
        collections = ['orders', 'employees', 'products', 'inventory', 'assignments', 'qualityChecks', 'packaging', 'dispatch', 'production']
        for col in collections:
            try:
                for doc in db.collection(col).stream():
                    if doc.id.startswith("CRUD_TEST"):
                        doc.reference.delete()
            except Exception:
                pass

    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()
        cls.cleanup_test_data()

        # Admin login to get JWT bearer token
        login_res = cls.client.post("/api/auth/login", json={
            "email": "admin@garment.com",
            "password": "Admin@123"
        })
        assert login_res.status_code == 200, f"Login failed: {login_res.get_json()}"
        cls.token = login_res.get_json()["data"]["token"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}

    @classmethod
    def tearDownClass(cls):
        cls.cleanup_test_data()

    def test_01_health_and_firestore_connection(self):
        """1. Verify health check and real Cloud Firestore read/write connection test."""
        # /api/health
        h_res = self.client.get("/api/health")
        self.assertEqual(h_res.status_code, 200)
        h_data = h_res.get_json()
        self.assertTrue(h_data.get("success"))
        self.assertEqual(h_data.get("message"), "Flask server is running")

        # /api/firestore-test
        fs_res = self.client.get("/api/firestore-test")
        self.assertEqual(fs_res.status_code, 200)
        fs_data = fs_res.get_json()
        self.assertTrue(fs_data.get("success"))
        self.assertIn("connected", fs_data.get("message").lower())

        # Verify doc directly in Firestore
        test_doc = db.collection("system").document("firestore_test").get()
        self.assertTrue(test_doc.exists)
        self.assertEqual(test_doc.to_dict().get("status"), "connected")

    def test_02_orders_crud_full_lifecycle(self):
        """
        2. Verify Orders CRUD:
        - CREATE CRUD_TEST_ORDER_001
        - Verify in Cloud Firestore directly
        - READ ALL /api/orders
        - READ ONE /api/orders/CRUD_TEST_ORDER_001
        - DUPLICATE CREATE check (409)
        - UPDATE quantity=250, status="In Progress"
        - Verify partial update safety (customerName, productType, deadline preserved)
        - DELETE CRUD_TEST_ORDER_001
        - Verify 404 response and Firestore deletion
        """
        order_id = "CRUD_TEST_ORDER_001"
        order_payload = {
            "orderId": order_id,
            "customerName": "CRUD Test Customer",
            "productType": "T-Shirt",
            "quantity": 100,
            "deadline": "2026-12-31",
            "status": "Pending"
        }

        # 1. CREATE via Flask API
        create_res = self.client.post("/api/orders", json=order_payload, headers=self.headers)
        self.assertEqual(create_res.status_code, 201)
        create_data = create_res.get_json()["data"]
        self.assertEqual(create_data["orderId"], order_id)
        self.assertEqual(create_data["quantity"], 100)

        # Verify document actually appears in Cloud Firestore: orders/CRUD_TEST_ORDER_001
        fs_doc = db.collection("orders").document(order_id).get()
        self.assertTrue(fs_doc.exists, "Document not found in Cloud Firestore orders collection!")
        fs_dict = fs_doc.to_dict()
        self.assertEqual(fs_dict["customerName"], "CRUD Test Customer")
        self.assertEqual(fs_dict["quantity"], 100)

        # 2. READ ALL via Flask API
        list_res = self.client.get("/api/orders", headers=self.headers)
        self.assertEqual(list_res.status_code, 200)
        orders_list = list_res.get_json()["data"]
        found_in_list = any(o["orderId"] == order_id for o in orders_list)
        self.assertTrue(found_in_list, "Created order not found in GET /api/orders list")

        # 3. READ ONE via Flask API
        get_res = self.client.get(f"/api/orders/{order_id}", headers=self.headers)
        self.assertEqual(get_res.status_code, 200)
        retrieved_order = get_res.get_json()["data"]
        self.assertEqual(retrieved_order["orderId"], order_id)
        self.assertEqual(retrieved_order["customerName"], fs_dict["customerName"])
        self.assertEqual(retrieved_order["quantity"], fs_dict["quantity"])

        # 4. DUPLICATE CREATE CHECK: Attempt creating duplicate orderId
        dup_res = self.client.post("/api/orders", json=order_payload, headers=self.headers)
        self.assertEqual(dup_res.status_code, 409, "Duplicate order ID should return HTTP 409 Conflict")

        # 5. UPDATE OPERATION: Update quantity=250, status="In Progress"
        update_payload = {
            "quantity": 250,
            "status": "In Progress"
        }
        put_res = self.client.put(f"/api/orders/{order_id}", json=update_payload, headers=self.headers)
        self.assertEqual(put_res.status_code, 200)

        # Read back document and verify fields
        get_updated_res = self.client.get(f"/api/orders/{order_id}", headers=self.headers)
        self.assertEqual(get_updated_res.status_code, 200)
        updated_data = get_updated_res.get_json()["data"]

        # Check updated fields
        self.assertEqual(updated_data["quantity"], 250)
        self.assertEqual(updated_data["status"], "In Progress")

        # Check UPDATE SAFETY: existing fields were NOT deleted
        self.assertEqual(updated_data["customerName"], "CRUD Test Customer")
        self.assertEqual(updated_data["productType"], "T-Shirt")
        self.assertEqual(updated_data["deadline"], "2026-12-31")

        # Check directly in Firestore
        fs_updated = db.collection("orders").document(order_id).get().to_dict()
        self.assertEqual(fs_updated["quantity"], 250)
        self.assertEqual(fs_updated["status"], "In Progress")
        self.assertEqual(fs_updated["customerName"], "CRUD Test Customer")

        # 6. DELETE OPERATION
        del_res = self.client.delete(f"/api/orders/{order_id}", headers=self.headers)
        self.assertEqual(del_res.status_code, 200)

        # Verify GET returns 404
        get_del_res = self.client.get(f"/api/orders/{order_id}", headers=self.headers)
        self.assertEqual(get_del_res.status_code, 404)

        # Verify Firestore document no longer exists
        fs_del_doc = db.collection("orders").document(order_id).get()
        self.assertFalse(fs_del_doc.exists, "Document still exists in Firestore after deletion!")

    def test_03_employees_crud(self):
        """3. Test Employees CRUD with CRUD_TEST_EMPLOYEE_001."""
        emp_id = "CRUD_TEST_EMPLOYEE_001"
        payload = {
            "employeeId": emp_id,
            "name": "CRUD Test Worker",
            "department": "Cutting",
            "role": "Fabric Cutter",
            "phone": "9998887771",
            "email": "crud.worker@garment.com"
        }

        # CREATE
        c_res = self.client.post("/api/employees", json=payload, headers=self.headers)
        self.assertEqual(c_res.status_code, 201)
        self.assertEqual(c_res.get_json()["data"]["employeeId"], emp_id)
        self.assertTrue(db.collection("employees").document(emp_id).get().exists)

        # READ ALL
        l_res = self.client.get("/api/employees", headers=self.headers)
        self.assertEqual(l_res.status_code, 200)
        self.assertTrue(any(e["employeeId"] == emp_id for e in l_res.get_json()["data"]))

        # READ ONE
        r_res = self.client.get(f"/api/employees/{emp_id}", headers=self.headers)
        self.assertEqual(r_res.status_code, 200)
        self.assertEqual(r_res.get_json()["data"]["name"], "CRUD Test Worker")

        # UPDATE
        u_res = self.client.put(f"/api/employees/{emp_id}", json={"role": "Senior Cutter"}, headers=self.headers)
        self.assertEqual(u_res.status_code, 200)
        self.assertEqual(u_res.get_json()["data"]["role"], "Senior Cutter")
        # Check safety: name intact
        self.assertEqual(u_res.get_json()["data"]["name"], "CRUD Test Worker")

        # DELETE & CLEANUP
        d_res = self.client.delete(f"/api/employees/{emp_id}", headers=self.headers)
        self.assertEqual(d_res.status_code, 200)
        self.assertFalse(db.collection("employees").document(emp_id).get().exists)

    def test_04_products_crud(self):
        """4. Test Products CRUD with CRUD_TEST_PRODUCT_001."""
        prod_id = "CRUD_TEST_PRODUCT_001"
        payload = {
            "productId": prod_id,
            "productCode": "CRUD-TSHIRT-01",
            "productName": "CRUD Test Cotton Crew",
            "productType": "T-Shirt",
            "description": "Combed cotton crew neck t-shirt",
            "fabricType": "180 GSM Single Jersey",
            "availableSizes": ["S", "M", "L"],
            "colors": ["Navy", "White"]
        }

        # CREATE
        c_res = self.client.post("/api/products", json=payload, headers=self.headers)
        self.assertEqual(c_res.status_code, 201)
        self.assertTrue(db.collection("products").document(prod_id).get().exists)

        # READ ALL
        l_res = self.client.get("/api/products", headers=self.headers)
        self.assertEqual(l_res.status_code, 200)
        self.assertTrue(any(p["productId"] == prod_id for p in l_res.get_json()["data"]))

        # READ ONE
        r_res = self.client.get(f"/api/products/{prod_id}", headers=self.headers)
        self.assertEqual(r_res.status_code, 200)
        self.assertEqual(r_res.get_json()["data"]["productName"], "CRUD Test Cotton Crew")

        # UPDATE
        u_res = self.client.put(f"/api/products/{prod_id}", json={"description": "Updated combed cotton"}, headers=self.headers)
        self.assertEqual(u_res.status_code, 200)
        self.assertEqual(u_res.get_json()["data"]["description"], "Updated combed cotton")
        self.assertEqual(u_res.get_json()["data"]["productName"], "CRUD Test Cotton Crew")

        # DELETE & CLEANUP
        d_res = self.client.delete(f"/api/products/{prod_id}", headers=self.headers)
        self.assertEqual(d_res.status_code, 200)
        self.assertFalse(db.collection("products").document(prod_id).get().exists)

    def test_05_inventory_crud_and_transactions(self):
        """5. Test Inventory CRUD with CRUD_TEST_INVENTORY_001 and atomic Stock In/Out."""
        mat_id = "CRUD_TEST_INVENTORY_001"
        payload = {
            "materialId": mat_id,
            "materialName": "CRUD Test Combed Cotton",
            "category": "Raw Materials",
            "quantity": 500,
            "unit": "meters",
            "minimumStock": 100,
            "supplier": "CRUD Mill Supplies"
        }

        # CREATE
        c_res = self.client.post("/api/inventory", json=payload, headers=self.headers)
        self.assertEqual(c_res.status_code, 201)
        self.assertTrue(db.collection("inventory").document(mat_id).get().exists)

        # READ ALL
        l_res = self.client.get("/api/inventory", headers=self.headers)
        self.assertEqual(l_res.status_code, 200)
        self.assertTrue(any(m["materialId"] == mat_id for m in l_res.get_json()["data"]))

        # READ ONE
        r_res = self.client.get(f"/api/inventory/{mat_id}", headers=self.headers)
        self.assertEqual(r_res.status_code, 200)
        self.assertEqual(r_res.get_json()["data"]["quantity"], 500)

        # STOCK IN (Atomicity / Transaction)
        in_res = self.client.post(f"/api/inventory/{mat_id}/stock-in", json={"quantity": 150, "reason": "Restock roll"}, headers=self.headers)
        self.assertEqual(in_res.status_code, 200)
        self.assertEqual(in_res.get_json()["data"]["quantity"], 650)

        # STOCK OUT
        out_res = self.client.post(f"/api/inventory/{mat_id}/stock-out", json={"quantity": 50, "reason": "Sample cut"}, headers=self.headers)
        self.assertEqual(out_res.status_code, 200)
        self.assertEqual(out_res.get_json()["data"]["quantity"], 600)

        # READ TRANSACTIONS
        t_res = self.client.get(f"/api/inventory/{mat_id}/transactions", headers=self.headers)
        self.assertEqual(t_res.status_code, 200)
        txns = t_res.get_json()["data"]
        self.assertGreaterEqual(len(txns), 2)

        # UPDATE
        u_res = self.client.put(f"/api/inventory/{mat_id}", json={"minimumStock": 120}, headers=self.headers)
        self.assertEqual(u_res.status_code, 200)
        self.assertEqual(u_res.get_json()["data"]["minimumStock"], 120)

        # DELETE & CLEANUP
        d_res = self.client.delete(f"/api/inventory/{mat_id}", headers=self.headers)
        self.assertEqual(d_res.status_code, 200)
        self.assertFalse(db.collection("inventory").document(mat_id).get().exists)

        # Clean up transactions created for this test material
        for txn in txns:
            db.collection("inventoryTransactions").document(txn["transactionId"]).delete()

    def test_06_production_and_assignments_crud(self):
        """6. Test Production Stages and Worker Assignments CRUD."""
        # Create a temporary order to generate production stages
        temp_order_id = "CRUD_TEST_PROD_ORDER"
        self.client.post("/api/orders", json={
            "orderId": temp_order_id,
            "customerName": "Prod Flow Customer",
            "productType": "Jacket",
            "quantity": 50,
            "deadline": "2026-12-31",
            "status": "In Production"
        }, headers=self.headers)

        prod_id = f"{temp_order_id}_1"  # Cutting stage

        # Production READ ONE
        stage_res = self.client.get(f"/api/production/{prod_id}", headers=self.headers)
        self.assertEqual(stage_res.status_code, 200)
        self.assertEqual(stage_res.get_json()["data"]["stage"], "Cutting")

        # Assignments CREATE
        asn_id = "CRUD_TEST_ASSIGNMENT_001"
        asn_res = self.client.post("/api/assignments", json={
            "assignmentId": asn_id,
            "orderId": temp_order_id,
            "productionId": prod_id,
            "employeeId": "EMP001",
            "stage": "Cutting"
        }, headers=self.headers)
        self.assertEqual(asn_res.status_code, 201)

        # Assignments READ ALL
        asn_list = self.client.get("/api/assignments", headers=self.headers)
        self.assertEqual(asn_list.status_code, 200)
        self.assertTrue(any(a["assignmentId"] == asn_id for a in asn_list.get_json()["data"]))

        # Assignments READ ONE
        asn_one = self.client.get(f"/api/assignments/{asn_id}", headers=self.headers)
        self.assertEqual(asn_one.status_code, 200)
        self.assertEqual(asn_one.get_json()["data"]["employeeId"], "EMP001")

        # Assignments UPDATE
        asn_up = self.client.put(f"/api/assignments/{asn_id}", json={"status": "In Progress"}, headers=self.headers)
        self.assertEqual(asn_up.status_code, 200)
        self.assertEqual(asn_up.get_json()["data"]["status"], "In Progress")

        # Production Stage Start & Complete
        start_res = self.client.post(f"/api/production/{prod_id}/start", headers=self.headers)
        self.assertEqual(start_res.status_code, 200)

        comp_res = self.client.post(f"/api/production/{prod_id}/complete", json={"completedQuantity": 50}, headers=self.headers)
        self.assertEqual(comp_res.status_code, 200)

        # Assignments DELETE & CLEANUP
        asn_del = self.client.delete(f"/api/assignments/{asn_id}", headers=self.headers)
        self.assertEqual(asn_del.status_code, 200)
        self.assertFalse(db.collection("assignments").document(asn_id).get().exists)

        # Clean up temporary order and its stages
        self.client.delete(f"/api/orders/{temp_order_id}", headers=self.headers)

    def test_07_quality_packaging_dispatch_crud(self):
        """7. Test Quality Checks, Packaging, and Dispatch CRUD."""
        # Create prerequisite order and complete manufacturing stages to reach QC
        order_id = "CRUD_TEST_QC_ORDER"
        self.client.post("/api/orders", json={
            "orderId": order_id,
            "customerName": "Full Flow Client",
            "productType": "Shirt",
            "quantity": 30,
            "deadline": "2026-12-31",
            "status": "In Production"
        }, headers=self.headers)

        # Complete Cutting, Stitching, Finishing
        for idx in [1, 2, 3]:
            self.client.post(f"/api/production/{order_id}_{idx}/complete", json={"completedQuantity": 30}, headers=self.headers)

        # Quality Check CREATE
        qc_id = "CRUD_TEST_QUALITY_001"
        qc_res = self.client.post("/api/quality-checks", json={
            "qualityCheckId": qc_id,
            "orderId": order_id,
            "result": "Pass",
            "defectRate": 0.0,
            "passedQuantity": 30,
            "failedQuantity": 0,
            "remarks": "Flawless batch"
        }, headers=self.headers)
        self.assertEqual(qc_res.status_code, 201)

        # Quality Check READ ALL
        qc_list = self.client.get("/api/quality-checks", headers=self.headers)
        self.assertEqual(qc_list.status_code, 200)
        self.assertTrue(any(q["qualityCheckId"] == qc_id for q in qc_list.get_json()["data"]))

        # Quality Check READ ONE
        qc_one = self.client.get(f"/api/quality-checks/{qc_id}", headers=self.headers)
        self.assertEqual(qc_one.status_code, 200)
        self.assertEqual(qc_one.get_json()["data"]["result"], "Pass")

        # Quality Check UPDATE
        qc_up = self.client.put(f"/api/quality-checks/{qc_id}", json={"remarks": "Verified flawless"}, headers=self.headers)
        self.assertEqual(qc_up.status_code, 200)
        self.assertEqual(qc_up.get_json()["data"]["remarks"], "Verified flawless")

        # Packaging CREATE
        pkg_id = "CRUD_TEST_PACKAGING_001"
        pkg_res = self.client.post("/api/packaging", json={
            "packagingId": pkg_id,
            "orderId": order_id,
            "quantity": 30,
            "remarks": "Carton packed"
        }, headers=self.headers)
        self.assertEqual(pkg_res.status_code, 201)

        # Packaging READ ALL & READ ONE
        pkg_list = self.client.get("/api/packaging", headers=self.headers)
        self.assertEqual(pkg_list.status_code, 200)
        self.assertTrue(any(p["packagingId"] == pkg_id for p in pkg_list.get_json()["data"]))

        pkg_one = self.client.get(f"/api/packaging/{pkg_id}", headers=self.headers)
        self.assertEqual(pkg_one.status_code, 200)

        # Packaging UPDATE
        pkg_up = self.client.put(f"/api/packaging/{pkg_id}", json={"remarks": "Updated carton packed"}, headers=self.headers)
        self.assertEqual(pkg_up.status_code, 200)

        # Dispatch CREATE
        dsp_id = "CRUD_TEST_DISPATCH_001"
        dsp_res = self.client.post("/api/dispatch", json={
            "dispatchId": dsp_id,
            "orderId": order_id,
            "deliveryInformation": "BlueDart Express tracking #BD123456",
            "remarks": "Courier dispatched"
        }, headers=self.headers)
        self.assertEqual(dsp_res.status_code, 201)

        # Dispatch READ ALL & READ ONE
        dsp_list = self.client.get("/api/dispatch", headers=self.headers)
        self.assertEqual(dsp_list.status_code, 200)
        self.assertTrue(any(d["dispatchId"] == dsp_id for d in dsp_list.get_json()["data"]))

        dsp_one = self.client.get(f"/api/dispatch/{dsp_id}", headers=self.headers)
        self.assertEqual(dsp_one.status_code, 200)

        # Dispatch UPDATE
        dsp_up = self.client.put(f"/api/dispatch/{dsp_id}", json={"remarks": "Courier confirmed in transit"}, headers=self.headers)
        self.assertEqual(dsp_up.status_code, 200)

        # CLEANUP: Delete temporary test records from Firestore
        db.collection("qualityChecks").document(qc_id).delete()
        db.collection("packaging").document(pkg_id).delete()
        db.collection("dispatch").document(dsp_id).delete()
        self.client.delete(f"/api/orders/{order_id}", headers=self.headers)

    def test_08_api_validations(self):
        """8. Test input validations and error handling."""
        # Missing required customerName & productName/type
        res1 = self.client.post("/api/orders", json={"quantity": 100}, headers=self.headers)
        self.assertEqual(res1.status_code, 400)
        self.assertFalse(res1.get_json()["success"])

        # Negative quantity
        res2 = self.client.post("/api/orders", json={
            "customerName": "Test",
            "productType": "Shirt",
            "quantity": -10,
            "deadline": "2026-12-31"
        }, headers=self.headers)
        self.assertEqual(res2.status_code, 400)

        # Invalid status
        res3 = self.client.post("/api/orders", json={
            "customerName": "Test",
            "productType": "Shirt",
            "quantity": 10,
            "deadline": "2026-12-31",
            "status": "NonExistentStatus"
        }, headers=self.headers)
        self.assertEqual(res3.status_code, 400)

        # Non-existent order retrieval
        res4 = self.client.get("/api/orders/NON_EXISTENT_ID_999", headers=self.headers)
        self.assertEqual(res4.status_code, 404)
        self.assertFalse(res4.get_json()["success"])

        # Updating non-existent order
        res5 = self.client.put("/api/orders/NON_EXISTENT_ID_999", json={"quantity": 50}, headers=self.headers)
        self.assertEqual(res5.status_code, 404)

        # Deleting non-existent order
        res6 = self.client.delete("/api/orders/NON_EXISTENT_ID_999", headers=self.headers)
        self.assertEqual(res6.status_code, 404)

        # Empty body
        res7 = self.client.post("/api/orders", json={}, headers=self.headers)
        self.assertEqual(res7.status_code, 400)

    def test_09_security_and_credentials(self):
        """9. Verify security: credentials are never exposed in API responses."""
        res = self.client.get("/api/auth/me", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        self.assertNotIn("password", data)
        self.assertNotIn("private_key", data)
        self.assertNotIn("serviceAccountKey", str(data))
