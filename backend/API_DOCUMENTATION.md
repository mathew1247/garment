# Garment Production Tracking System - API Documentation

The Garment Production Tracking System provides a RESTful API backend built with Python Flask directly connected to **Google Cloud Firestore**.

## Base URL
```
http://localhost:5000/api
```

## Global Authentication & Headers
Protected endpoints accept either:
1. **Firebase Authentication ID Token** (issued by Firebase client SDK):
   ```http
   Authorization: Bearer <Firebase_ID_Token>
   Content-Type: application/json
   ```
2. **Backend Session JWT Token** (issued upon `/api/auth/login`):
   ```http
   Authorization: Bearer <Session_JWT_Token>
   Content-Type: application/json
   ```

## Standard Response Formats

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

### List / Collection Response
```json
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": [ ... ],
  "count": 5
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description message",
  "error": "ERROR_CODE"
}
```

---

## 1. System Health & Cloud Verification

### GET `/api/health`
Checks whether the Flask API server is alive.
- **Authentication**: None
- **Response `200`**:
```json
{
  "success": true,
  "message": "Garment Production Tracking API is running",
  "version": "1.0.0"
}
```

### GET `/api/firestore-test`
Writes a verification document to `system/firestore_test` in Cloud Firestore and reads it back.
- **Authentication**: None
- **Response `200`**:
```json
{
  "success": true,
  "message": "Flask successfully connected and verified with Cloud Firestore",
  "data": {
    "status": "connected",
    "message": "Flask connected to Cloud Firestore",
    "timestamp": "2026-10-05T06:54:38.211000Z"
  }
}
```

---

## 2. Authentication

### POST `/api/auth/login`
Authenticates a user via either Firebase ID Token or email/password.
- **Request Body (Firebase ID Token)**:
```json
{
  "idToken": "<FIREBASE_ID_TOKEN>"
}
```
- **Request Body (Email & Password)**:
```json
{
  "email": "admin@garment.com",
  "password": "Admin@123"
}
```
- **Response `200`**:
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "uid": "USR001",
      "name": "Admin User",
      "email": "admin@garment.com",
      "role": "Administrator",
      "status": "Active"
    }
  }
}
```

### GET `/api/auth/me`
Retrieves currently authenticated user from `users/{uid}` in Firestore.
- **Authentication**: Required
- **Response `200`**:
```json
{
  "success": true,
  "message": "Authenticated user profile retrieved",
  "data": {
    "uid": "USR001",
    "name": "Admin User",
    "email": "admin@garment.com",
    "role": "Administrator",
    "status": "Active"
  }
}
```

### POST `/api/auth/logout`
Terminates the session.
- **Authentication**: Required

---

## 3. User Management

### GET `/api/users`
List all users from Firestore.
- **Authentication**: Required
- **Role**: `Administrator`

### POST `/api/users`
Create user profile in Firestore `users/{uid}`.
- **Authentication**: Required
- **Role**: `Administrator`
- **Request Body**:
```json
{
  "name": "John Doe",
  "email": "john@garment.com",
  "password": "Password@123",
  "role": "Staff",
  "status": "Active"
}
```

### PUT `/api/users/<user_id>`
Update user profile or role.
- **Role**: `Administrator`

### DELETE `/api/users/<user_id>`
Delete user profile.
- **Role**: `Administrator`

---

## 4. Products

### GET `/api/products`
List all product templates.
- **Authentication**: Required

### POST `/api/products`
Create a product template.
- **Roles**: `Administrator`, `Manager`
- **Request Body**:
```json
{
  "productCode": "SHIRT-CTN-01",
  "productName": "Cotton Shirt",
  "productType": "Shirt",
  "description": "Full sleeve combed cotton shirt",
  "fabricType": "100% Combed Cotton",
  "availableSizes": ["S", "M", "L", "XL"],
  "colors": ["Sky Blue", "White"]
}
```

---

## 5. Orders

### GET `/api/orders`
Retrieve orders with Firestore queries.
- **Query Parameters**: `status`, `priority`, `customer`

### POST `/api/orders`
Creates order and automatically provisions all 6 production stages in Firestore (`Cutting`, `Stitching`, `Finishing`, `Quality Check`, `Packaging`, `Dispatch`).
- **Roles**: `Administrator`, `Manager`
- **Request Body**:
```json
{
  "customerName": "ABC Fashion Inc",
  "customerContact": "9876543210",
  "productName": "Cotton Shirt",
  "productType": "Shirt",
  "quantity": 1000,
  "deadline": "2026-11-20",
  "priority": "High"
}
```

### GET `/api/orders/<order_id>`
Returns order details and all 6 sequential production stages.

### PUT `/api/orders/<order_id>`
Update order metadata.
- **Roles**: `Administrator`, `Manager`

### DELETE `/api/orders/<order_id>`
Cascade deletes order and all associated production stages from Firestore.
- **Role**: `Administrator`

---

## 6. Production Workflow

### GET `/api/production`
Query production records from Firestore.
- **Query Parameters**: `orderId`, `stage`, `status`, `employeeId`

### POST `/api/production/<production_id>/start`
Start stage execution. Enforces strict linear progression (preceding stage must be `Completed`).

### POST `/api/production/<production_id>/complete`
Complete stage. Automatically advances the subsequent stage and updates order status.

---

## 7. Quality Checks

### POST `/api/quality-checks`
Record inspection outcome.
- **Request Body (Pass)**:
```json
{
  "orderId": "ORD001",
  "inspectorId": "EMP004",
  "result": "Pass",
  "defectType": "None",
  "defectQuantity": 0,
  "remarks": "Passed 100% inspection"
}
```
*Business Rule*: Unlocks `Packaging = In Progress`.

- **Request Body (Fail)**:
```json
{
  "orderId": "ORD001",
  "inspectorId": "EMP004",
  "result": "Fail",
  "defectType": "Stitching Defect",
  "defectQuantity": 15,
  "reworkStage": "Stitching",
  "remarks": "Seams unraveling on collar"
}
```
*Business Rule*: Marks order as `Rework` and returns it to `Stitching`. Blocks packaging until passed.

---

## 8. Packaging & Dispatch

### POST `/api/packaging`
Record order packaging.
- **Rule**: Packaging is strictly rejected with `HTTP 400 QC_NOT_PASSED` if Quality Check is not `Pass`.

### POST `/api/dispatch`
Record shipment dispatch.
- **Rule**: Dispatch is strictly rejected until Packaging is completed. Once dispatched, Order status & currentStage are set to `Completed`.

---

## 9. Inventory & Transactions

### GET `/api/inventory`
List inventory items.

### POST `/api/inventory`
Create a new raw material or WIP item.

### POST `/api/inventory/<material_id>/stock-in`
Add stock. Generates an `inventoryTransactions` document in Firestore.

### POST `/api/inventory/<material_id>/stock-out`
Deduct stock. Prevents negative inventory. Generates an `inventoryTransactions` document and low/out-of-stock notifications.

### GET `/api/inventory/<material_id>/transactions`
Get audit trail of stock movements.

---

## 10. Dashboard & Analytics

### GET `/api/dashboard`
Returns total orders, stage breakdowns, inventory health, delayed orders list, and recent audit activity stream.
- **Roles**: `Administrator`, `Manager`

### Reports:
- `GET /api/reports/production`
- `GET /api/reports/orders`
- `GET /api/reports/employees`
- `GET /api/reports/inventory`

---

## 11. Notifications

### GET `/api/notifications`
Retrieve alerts.

### GET `/api/notifications/unread`
Retrieve unread alerts.

### PUT `/api/notifications/<id>/read`
Mark notification as read.
