# Garment Production Tracking System - Flask + Cloud Firestore Backend

A Python Flask REST API backend directly connected to **Google Cloud Firestore** for managing garment manufacturing operations from order intake to dispatch.

---

## 1. Project Overview & Architecture

- **Frontend**: HTML5, CSS3, Vanilla JavaScript (communicates via standard REST `fetch()` calls to Flask).
- **Backend API**: Python 3.x, Flask, Flask-CORS, PyJWT, Werkzeug.
- **Database**: **Google Cloud Firestore** (Project: `garmentmanager-ae69f`, Location: `asia-south1` Mumbai).
- **Firebase SDK**: Firebase Admin SDK (`firebase-admin`).

```
[ Frontend (HTML/CSS/JS) ]
            │ HTTP / JSON
            ▼
    [ Flask Routes ]
  (Request parsing, HTTP status, Auth decorators)
            │
            ▼
   [ Service Layer ]
  (Business logic, validation, workflow rules, audit logs)
            │
            ▼
 [ Firestore Repository ]
  (Direct Cloud Firestore CRUD, Queries, and Batched operations)
            │
            ▼
 [ Google Cloud Firestore ]
  (asia-south1 / Mumbai)
```

---

## 2. Firebase & Service Account Configuration

The backend authenticates with Firebase using `serviceAccountKey.json`.

### Local Development
Place `serviceAccountKey.json` inside the `backend/` directory:
```
backend/serviceAccountKey.json
```
`backend/firebase/firebase_config.py` automatically resolves the credential path.

### Deployment on Render / Cloud
To deploy securely without committing `serviceAccountKey.json`:
1. Provide the JSON file content as an environment variable in Render:
   - Key: `FIREBASE_CREDENTIALS_JSON`
   - Value: Paste the full JSON string from `serviceAccountKey.json`.
2. OR upload it as a Secret File in Render and set:
   - `FIREBASE_CREDENTIALS_PATH=/etc/secrets/serviceAccountKey.json`

---

## 3. Cloud Firestore Collections

The backend operates on 13 Firestore collections:

| Collection | Primary ID | Purpose |
|---|---|---|
| `users` | `uid` | User accounts, roles (`Administrator`, `Manager`, `Staff`), profile data |
| `employees` | `employeeId` (`EMP001`) | Factory workers and departmental mapping |
| `products` | `productId` (`PRD001`) | Garment templates and design specifications |
| `orders` | `orderId` (`ORD001`) | Customer purchase orders, quantities, deadlines |
| `production` | `productionId` (`ORD001_1`) | 6 sequential production stages per order |
| `assignments` | `assignmentId` (`ASN001`) | Worker task assignments to order stages |
| `qualityChecks` | `qualityCheckId` (`QC001`) | Inspection records (`Pass` or `Fail`/`Rework`) |
| `inventory` | `materialId` (`MAT001`) | Raw materials, WIP, and finished goods stock levels |
| `inventoryTransactions` | `transactionId` (`TXN001`) | Audit log of all stock `IN` / `OUT` movements |
| `packaging` | `packagingId` (`PKG001`) | Packaging records (unlocked only upon QC Pass) |
| `dispatch` | `dispatchId` (`DSP001`) | Shipping records (completes order) |
| `notifications` | `notificationId` (`NOT001`) | System alerts for bottlenecks and milestones |
| `auditLogs` | `logId` (`LOG0001`) | Immutable compliance audit trail |

---

## 4. Setup & Running Locally

### Step 1: Install Dependencies
```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Seed Cloud Firestore (Initial Setup)
Populate realistic development records in Cloud Firestore:
```bash
python scripts/seed_data.py
```

### Step 3: Run the Flask API Server
```bash
python app.py
```
Server runs on:
```
http://localhost:5000
```
Health Check:
```
GET http://localhost:5000/api/health
```
Firestore Verification Check:
```
GET http://localhost:5000/api/firestore-test
```

---

## 5. Test Credentials

| Role | Email | Password | Access Rights |
|---|---|---|---|
| **Administrator** | `admin@garment.com` | `Admin@123` | Full access across all collections |
| **Manager** | `manager@garment.com` | `Manager@123` | Dashboard, Orders, Production, Employees, Inventory, Reports |
| **Staff** | `staff@garment.com` | `Staff@123` | View assigned tasks, update production progress, record QC |

---

## 6. Production Workflow Enforced

```
[ New Order Created ]
         │ (Auto-creates 6 production stage records in Firestore)
         ▼
    [ Cutting ] (Starts In Progress)
         │ (Complete Stage)
         ▼
   [ Stitching ]
         │ (Complete Stage)
         ▼
   [ Finishing ]
         │ (Complete Stage)
         ▼
 [ Quality Check ]
         │
    ┌────┴────┐
    ▼         ▼
 [ Pass ]  [ Fail ]
    │         │
    │         ▼
    │    [ Rework ] ──> Sends back to Stitching/Finishing
    ▼
[ Packaging ]  (STRICT: Blocked with HTTP 400 until Quality Check = Pass)
    │
    ▼
[ Dispatch ]   (STRICT: Blocked with HTTP 400 until Packaging = Completed)
    │
    ▼
[ Order Completed ] (Automatically sets Order status to Completed)
```

---

## 7. Automated Testing

Run the test suite against Cloud Firestore:
```bash
python -m unittest discover -s tests -v
```
All 20 unit, integration, and end-to-end tests verify authentication, order provisioning, stage sequence, rework routing, negative inventory guards, packaging gates, and dashboard KPI generation.

---

## 8. Deployment on Render

1. **Build Command**: `pip install -r requirements.txt`
2. **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT backend.app:app`
3. **Environment Variables**:
   - `SECRET_KEY`: `<random-secret>`
   - `JWT_SECRET_KEY`: `<random-jwt-secret>`
   - `FIREBASE_CREDENTIALS_JSON`: `<paste-contents-of-serviceAccountKey.json>`
   - `FRONTEND_URL`: `https://your-frontend.com`
