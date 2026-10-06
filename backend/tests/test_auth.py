import unittest
from backend.app import create_app
class TestAuth(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()

    def test_health_check(self):
        """Test health check endpoint."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Flask server is running")

    def test_login_admin_success(self):
        """Test admin login with valid credentials."""
        res = self.client.post("/api/auth/login", json={
            "email": "admin@garment.com",
            "password": "Admin@123"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("token", data["data"])
        self.assertEqual(data["data"]["user"]["role"], "Administrator")
        self.assertNotIn("password", data["data"]["user"])

    def test_login_invalid_password(self):
        """Test login rejection on incorrect password."""
        res = self.client.post("/api/auth/login", json={
            "email": "admin@garment.com",
            "password": "WrongPassword"
        })
        self.assertEqual(res.status_code, 401)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "INVALID_CREDENTIALS")

    def test_get_me_with_valid_token(self):
        """Test retrieving currently authenticated user profile."""
        login_res = self.client.post("/api/auth/login", json={
            "email": "admin@garment.com",
            "password": "Admin@123"
        })
        token = login_res.get_json()["data"]["token"]

        me_res = self.client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        self.assertEqual(me_res.status_code, 200)
        data = me_res.get_json()
        self.assertEqual(data["data"]["email"], "admin@garment.com")

    def test_role_authorization_forbidden(self):
        """Test that Staff role cannot access Admin-only user management."""
        staff_login = self.client.post("/api/auth/login", json={
            "email": "staff@garment.com",
            "password": "Staff@123"
        })
        token = staff_login.get_json()["data"]["token"]

        users_res = self.client.get("/api/users", headers={
            "Authorization": f"Bearer {token}"
        })
        self.assertEqual(users_res.status_code, 403)
        data = users_res.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "FORBIDDEN")

if __name__ == "__main__":
    unittest.main()
