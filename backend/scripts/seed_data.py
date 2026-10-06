import os
import sys
from pathlib import Path
from werkzeug.security import generate_password_hash

# Ensure project and backend directories are in sys.path
script_dir = Path(__file__).resolve().parent
backend_dir = script_dir.parent
project_root = backend_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.firebase.firebase_config import db

ADMIN_HASH = generate_password_hash("Admin@123")
MANAGER_HASH = generate_password_hash("Manager@123")
STAFF_HASH = generate_password_hash("Staff@123")

SEED_USERS = [
    {
        "uid": "USR001",
        "id": "USR001",
        "name": "Admin User",
        "email": "admin@garment.com",
        "password": ADMIN_HASH,
        "role": "Administrator",
        "phone": "9876543200",
        "status": "Active",
        "profileImage": "",
        "createdAt": "2026-01-01T08:00:00Z",
        "updatedAt": "2026-01-01T08:00:00Z",
        "lastLogin": None
    },
    {
        "uid": "USR002",
        "id": "USR002",
        "name": "Production Manager",
        "email": "manager@garment.com",
        "password": MANAGER_HASH,
        "role": "Manager",
        "phone": "9876543201",
        "status": "Active",
        "profileImage": "",
        "createdAt": "2026-01-02T08:00:00Z",
        "updatedAt": "2026-01-02T08:00:00Z",
        "lastLogin": None
    },
    {
        "uid": "USR003",
        "id": "USR003",
        "name": "Staff Worker One",
        "email": "staff@garment.com",
        "password": STAFF_HASH,
        "role": "Staff",
        "phone": "9876543202",
        "status": "Active",
        "profileImage": "",
        "createdAt": "2026-01-03T08:00:00Z",
        "updatedAt": "2026-01-03T08:00:00Z",
        "lastLogin": None
    }
]

SEED_EMPLOYEES = [
    {
        "employeeId": "EMP001",
        "id": "EMP001",
        "name": "Ramesh Kumar",
        "department": "Cutting",
        "role": "Master Cutter",
        "phone": "9876543210",
        "email": "ramesh@garment.com",
        "profileImage": "",
        "status": "Active",
        "createdAt": "2026-01-01T09:00:00Z",
        "updatedAt": "2026-01-01T09:00:00Z"
    },
    {
        "employeeId": "EMP002",
        "id": "EMP002",
        "name": "Suresh Babu",
        "department": "Stitching",
        "role": "Tailor Specialist",
        "phone": "9876543211",
        "email": "suresh@garment.com",
        "profileImage": "",
        "status": "Active",
        "createdAt": "2026-01-01T09:00:00Z",
        "updatedAt": "2026-01-01T09:00:00Z"
    },
    {
        "employeeId": "EMP003",
        "id": "EMP003",
        "name": "Priya Sharma",
        "department": "Finishing",
        "role": "Finishing Tech",
        "phone": "9876543212",
        "email": "priya@garment.com",
        "profileImage": "",
        "status": "Active",
        "createdAt": "2026-01-01T09:00:00Z",
        "updatedAt": "2026-01-01T09:00:00Z"
    },
    {
        "employeeId": "EMP004",
        "id": "EMP004",
        "name": "Deepak Verma",
        "department": "Quality",
        "role": "Chief Quality Inspector",
        "phone": "9876543213",
        "email": "deepak@garment.com",
        "profileImage": "",
        "status": "Active",
        "createdAt": "2026-01-01T09:00:00Z",
        "updatedAt": "2026-01-01T09:00:00Z"
    },
    {
        "employeeId": "EMP005",
        "id": "EMP005",
        "name": "Anitha Raj",
        "department": "Packaging",
        "role": "Packaging Lead",
        "phone": "9876543214",
        "email": "anitha@garment.com",
        "profileImage": "",
        "status": "Active",
        "createdAt": "2026-01-01T09:00:00Z",
        "updatedAt": "2026-01-01T09:00:00Z"
    },
    {
        "employeeId": "EMP006",
        "id": "EMP006",
        "name": "Karthik Raja",
        "department": "Dispatch",
        "role": "Logistics Officer",
        "phone": "9876543215",
        "email": "karthik@garment.com",
        "profileImage": "",
        "status": "Active",
        "createdAt": "2026-01-01T09:00:00Z",
        "updatedAt": "2026-01-01T09:00:00Z"
    }
]

SEED_PRODUCTS = [
    {
        "productId": "PRD001",
        "id": "PRD001",
        "productCode": "SHIRT-CTN-01",
        "productName": "Cotton Shirt",
        "productType": "Shirt",
        "description": "Full sleeve combed cotton formal shirt with reinforced collar",
        "fabricType": "100% Combed Cotton",
        "availableSizes": ["S", "M", "L", "XL"],
        "colors": ["Sky Blue", "White", "Navy"],
        "createdAt": "2026-01-01T10:00:00Z",
        "updatedAt": "2026-01-01T10:00:00Z"
    },
    {
        "productId": "PRD002",
        "id": "PRD002",
        "productCode": "POLO-PQ-02",
        "productName": "Polo Shirt",
        "productType": "Polo",
        "description": "Pique knit collar polo shirt with 2 buttons",
        "fabricType": "Pique Cotton Blend",
        "availableSizes": ["M", "L", "XL"],
        "colors": ["Navy Blue", "Black", "Maroon"],
        "createdAt": "2026-01-01T10:00:00Z",
        "updatedAt": "2026-01-01T10:00:00Z"
    },
    {
        "productId": "PRD003",
        "id": "PRD003",
        "productCode": "TSHIRT-JS-03",
        "productName": "T-Shirt",
        "productType": "T-Shirt",
        "description": "Round neck bio-wash printed summer tees",
        "fabricType": "Single Jersey 180 GSM",
        "availableSizes": ["S", "M", "L", "XL"],
        "colors": ["Charcoal Black", "White", "Olive"],
        "createdAt": "2026-01-01T10:00:00Z",
        "updatedAt": "2026-01-01T10:00:00Z"
    }
]

SEED_ORDERS = [
    {
        "orderId": "ORD001",
        "id": "ORD001",
        "customerName": "ABC Fashion",
        "customerContact": "9876543210",
        "productId": "PRD003",
        "productName": "T-Shirt",
        "productType": "T-Shirt",
        "quantity": 500,
        "deadline": "2026-10-12",
        "specifications": "Double needle stitch on hem and sleeve cuffs. Strict color fastness requirement.",
        "fabricType": "100% Combed Cotton Single Jersey (180 GSM)",
        "color": "Navy Blue / Heather Grey",
        "sizes": ["S", "M", "L", "XL"],
        "priority": "High",
        "status": "In Progress",
        "currentStage": "Stitching",
        "createdBy": "USR001",
        "createdAt": "2026-09-28T10:00:00Z",
        "updatedAt": "2026-10-04T11:00:00Z"
    },
    {
        "orderId": "ORD002",
        "id": "ORD002",
        "customerName": "XYZ Garments",
        "customerContact": "9812345678",
        "productId": "PRD001",
        "productName": "Shirt",
        "productType": "Shirt",
        "quantity": 800,
        "deadline": "2026-10-15",
        "specifications": "Buttonholing and collar stiffener pressing required.",
        "fabricType": "Oxford Cotton Weave (120 GSM)",
        "color": "Classic White & Sky Blue",
        "sizes": ["38", "40", "42", "44"],
        "priority": "Medium",
        "status": "Pending",
        "currentStage": "Finishing",
        "createdBy": "USR002",
        "createdAt": "2026-09-25T09:00:00Z",
        "updatedAt": "2026-10-02T14:00:00Z"
    },
    {
        "orderId": "ORD003",
        "id": "ORD003",
        "customerName": "PQR Exports",
        "customerContact": "9833445566",
        "productId": "PRD002",
        "productName": "Jacket",
        "productType": "Jacket",
        "quantity": 300,
        "deadline": "2026-10-10",
        "specifications": "Heavy duty YKK zippers. Waterproof seam sealing test.",
        "fabricType": "Water-resistant Taslan Nylon with Polyester Quilted Lining",
        "color": "Charcoal Black",
        "sizes": ["M", "L", "XL"],
        "priority": "Urgent",
        "status": "In Progress",
        "currentStage": "Quality Check",
        "createdBy": "USR002",
        "createdAt": "2026-09-20T09:00:00Z",
        "updatedAt": "2026-10-03T16:00:00Z"
    },
    {
        "orderId": "ORD004",
        "id": "ORD004",
        "customerName": "Fashion World",
        "customerContact": "9844556677",
        "productId": "PRD001",
        "productName": "Pants",
        "productType": "Pants",
        "quantity": 600,
        "deadline": "2026-10-18",
        "specifications": "Pocket bag printing with wash instructions.",
        "fabricType": "Stretch Cotton Twill (240 GSM)",
        "color": "Khaki & Olive Green",
        "sizes": ["30", "32", "34", "36"],
        "priority": "Medium",
        "status": "In Progress",
        "currentStage": "Cutting",
        "createdBy": "USR001",
        "createdAt": "2026-10-02T09:00:00Z",
        "updatedAt": "2026-10-04T12:00:00Z"
    },
    {
        "orderId": "ORD005",
        "id": "ORD005",
        "customerName": "Style Hub",
        "customerContact": "9855667788",
        "productId": "PRD003",
        "productName": "T-Shirt",
        "productType": "T-Shirt",
        "quantity": 1000,
        "deadline": "2026-10-20",
        "specifications": "Individual biodegradable polybag packing with barcodes.",
        "fabricType": "Organic Combed Cotton (160 GSM)",
        "color": "Pastel Mint & Pure White",
        "sizes": ["XS", "S", "M", "L"],
        "priority": "Low",
        "status": "In Progress",
        "currentStage": "Packaging",
        "createdBy": "USR002",
        "createdAt": "2026-09-18T09:00:00Z",
        "updatedAt": "2026-10-05T10:00:00Z"
    },
    {
        "orderId": "ORD006",
        "id": "ORD006",
        "customerName": "Urban Vogue",
        "customerContact": "9866778899",
        "productId": "PRD002",
        "productName": "Hoodie",
        "productType": "Hoodie",
        "quantity": 450,
        "deadline": "2026-10-06",
        "specifications": "Kangaroo pocket with tonal drawstrings.",
        "fabricType": "Fleece Brushed Back (320 GSM)",
        "color": "Ash Melange",
        "sizes": ["S", "M", "L", "XL"],
        "priority": "High",
        "status": "Completed",
        "currentStage": "Dispatch",
        "createdBy": "USR001",
        "createdAt": "2026-09-10T09:00:00Z",
        "updatedAt": "2026-10-04T15:00:00Z"
    },
    {
        "orderId": "ORD007",
        "id": "ORD007",
        "customerName": "Elite Corp Uniforms",
        "customerContact": "9877889900",
        "productId": "PRD001",
        "productName": "Uniform",
        "productType": "Uniform",
        "quantity": 1200,
        "deadline": "2026-10-04",
        "specifications": "Embroidered corporate chest emblem on each garment.",
        "fabricType": "Poly-Viscose Anti-wrinkle Fabric",
        "color": "Corporate Navy",
        "sizes": ["Standard Corporate Set"],
        "priority": "Urgent",
        "status": "Delayed",
        "currentStage": "Quality Check",
        "createdBy": "USR002",
        "createdAt": "2026-09-12T09:00:00Z",
        "updatedAt": "2026-10-03T17:00:00Z"
    }
]

SEED_PRODUCTION = [
    # ORD001 stages
    {"productionId": "ORD001_1", "id": "ORD001_1", "orderId": "ORD001", "stage": "Cutting", "status": "In Progress", "assignedEmployeeId": "EMP001", "assignedEmployeeName": "Ramesh Kumar", "quantity": 1000, "completedQuantity": 600, "progress": 60, "startDate": "2026-09-02T10:00:00Z", "expectedCompletion": "2026-10-10", "completedDate": None, "remarks": "Pattern cutting in progress", "createdAt": "2026-09-01T10:00:00Z", "updatedAt": "2026-09-02T10:00:00Z"},
    {"productionId": "ORD001_2", "id": "ORD001_2", "orderId": "ORD001", "stage": "Stitching", "status": "Pending", "assignedEmployeeId": "EMP002", "assignedEmployeeName": "Suresh Babu", "quantity": 1000, "completedQuantity": 0, "progress": 0, "startDate": None, "expectedCompletion": "2026-10-25", "completedDate": None, "remarks": "", "createdAt": "2026-09-01T10:00:00Z", "updatedAt": "2026-09-01T10:00:00Z"},
    {"productionId": "ORD001_3", "id": "ORD001_3", "orderId": "ORD001", "stage": "Finishing", "status": "Pending", "assignedEmployeeId": None, "assignedEmployeeName": None, "quantity": 1000, "completedQuantity": 0, "progress": 0, "startDate": None, "expectedCompletion": "2026-11-05", "completedDate": None, "remarks": "", "createdAt": "2026-09-01T10:00:00Z", "updatedAt": "2026-09-01T10:00:00Z"},
    {"productionId": "ORD001_4", "id": "ORD001_4", "orderId": "ORD001", "stage": "Quality Check", "status": "Pending", "assignedEmployeeId": None, "assignedEmployeeName": None, "quantity": 1000, "completedQuantity": 0, "progress": 0, "startDate": None, "expectedCompletion": "2026-11-10", "completedDate": None, "remarks": "", "createdAt": "2026-09-01T10:00:00Z", "updatedAt": "2026-09-01T10:00:00Z"},
    {"productionId": "ORD001_5", "id": "ORD001_5", "orderId": "ORD001", "stage": "Packaging", "status": "Pending", "assignedEmployeeId": None, "assignedEmployeeName": None, "quantity": 1000, "completedQuantity": 0, "progress": 0, "startDate": None, "expectedCompletion": "2026-11-15", "completedDate": None, "remarks": "", "createdAt": "2026-09-01T10:00:00Z", "updatedAt": "2026-09-01T10:00:00Z"},
    {"productionId": "ORD001_6", "id": "ORD001_6", "orderId": "ORD001", "stage": "Dispatch", "status": "Pending", "assignedEmployeeId": None, "assignedEmployeeName": None, "quantity": 1000, "completedQuantity": 0, "progress": 0, "startDate": None, "expectedCompletion": "2026-11-20", "completedDate": None, "remarks": "", "createdAt": "2026-09-01T10:00:00Z", "updatedAt": "2026-09-01T10:00:00Z"},

    # ORD002 stages
    {"productionId": "ORD002_1", "id": "ORD002_1", "orderId": "ORD002", "stage": "Cutting", "status": "Completed", "assignedEmployeeId": "EMP001", "assignedEmployeeName": "Ramesh Kumar", "quantity": 500, "completedQuantity": 500, "progress": 100, "startDate": "2026-09-11T09:00:00Z", "expectedCompletion": "2026-09-15", "completedDate": "2026-09-14T17:00:00Z", "remarks": "Completed", "createdAt": "2026-09-10T09:00:00Z", "updatedAt": "2026-09-14T17:00:00Z"},
    {"productionId": "ORD002_2", "id": "ORD002_2", "orderId": "ORD002", "stage": "Stitching", "status": "Completed", "assignedEmployeeId": "EMP002", "assignedEmployeeName": "Suresh Babu", "quantity": 500, "completedQuantity": 500, "progress": 100, "startDate": "2026-09-15T09:00:00Z", "expectedCompletion": "2026-09-20", "completedDate": "2026-09-19T18:00:00Z", "remarks": "Completed", "createdAt": "2026-09-10T09:00:00Z", "updatedAt": "2026-09-19T18:00:00Z"},
    {"productionId": "ORD002_3", "id": "ORD002_3", "orderId": "ORD002", "stage": "Finishing", "status": "Completed", "assignedEmployeeId": "EMP003", "assignedEmployeeName": "Priya Sharma", "quantity": 500, "completedQuantity": 500, "progress": 100, "startDate": "2026-09-20T09:00:00Z", "expectedCompletion": "2026-09-24", "completedDate": "2026-09-24T16:00:00Z", "remarks": "Pressed & tagged", "createdAt": "2026-09-10T09:00:00Z", "updatedAt": "2026-09-24T16:00:00Z"},
    {"productionId": "ORD002_4", "id": "ORD002_4", "orderId": "ORD002", "stage": "Quality Check", "status": "In Progress", "assignedEmployeeId": "EMP004", "assignedEmployeeName": "Deepak Verma", "quantity": 500, "completedQuantity": 250, "progress": 50, "startDate": "2026-09-25T09:00:00Z", "expectedCompletion": "2026-09-28", "completedDate": None, "remarks": "Visual check", "createdAt": "2026-09-10T09:00:00Z", "updatedAt": "2026-09-25T09:00:00Z"},
    {"productionId": "ORD002_5", "id": "ORD002_5", "orderId": "ORD002", "stage": "Packaging", "status": "Pending", "assignedEmployeeId": "EMP005", "assignedEmployeeName": "Anitha Raj", "quantity": 500, "completedQuantity": 0, "progress": 0, "startDate": None, "expectedCompletion": "2026-10-02", "completedDate": None, "remarks": "Pending QC", "createdAt": "2026-09-10T09:00:00Z", "updatedAt": "2026-09-10T09:00:00Z"},
    {"productionId": "ORD002_6", "id": "ORD002_6", "orderId": "ORD002", "stage": "Dispatch", "status": "Pending", "assignedEmployeeId": "EMP006", "assignedEmployeeName": "Karthik Raja", "quantity": 500, "completedQuantity": 0, "progress": 0, "startDate": None, "expectedCompletion": "2026-10-05", "completedDate": None, "remarks": "", "createdAt": "2026-09-10T09:00:00Z", "updatedAt": "2026-09-10T09:00:00Z"}
]

SEED_INVENTORY = [
    {
        "materialId": "MAT001",
        "id": "MAT001",
        "materialName": "100% Combed Cotton Fabric (Sky Blue)",
        "category": "Raw Materials",
        "quantity": 5000.0,
        "unit": "meters",
        "minimumStock": 1000.0,
        "supplier": "ABC Textiles Ltd",
        "status": "In Stock",
        "createdAt": "2026-01-01T10:00:00Z",
        "updatedAt": "2026-09-01T10:00:00Z"
    },
    {
        "materialId": "MAT002",
        "id": "MAT002",
        "materialName": "Polyester Sewing Thread Spools (Navy)",
        "category": "Raw Materials",
        "quantity": 800.0,
        "unit": "spools",
        "minimumStock": 1000.0,
        "supplier": "Coats Garment Thread Supplies",
        "status": "Low Stock",
        "createdAt": "2026-01-01T10:00:00Z",
        "updatedAt": "2026-09-15T12:00:00Z"
    },
    {
        "materialId": "MAT003",
        "id": "MAT003",
        "materialName": "Mother of Pearl Formal Buttons (Pack of 100)",
        "category": "Raw Materials",
        "quantity": 0.0,
        "unit": "packs",
        "minimumStock": 200.0,
        "supplier": "Apex Button Accessories",
        "status": "Out of Stock",
        "createdAt": "2026-01-01T10:00:00Z",
        "updatedAt": "2026-09-20T10:00:00Z"
    },
    {
        "materialId": "MAT004",
        "id": "MAT004",
        "materialName": "Cut Fabric Bundles - Cotton Shirt",
        "category": "Work In Progress",
        "quantity": 1200.0,
        "unit": "bundles",
        "minimumStock": 500.0,
        "supplier": "Internal Cutting Dept",
        "status": "In Stock",
        "createdAt": "2026-09-01T10:00:00Z",
        "updatedAt": "2026-09-20T15:00:00Z"
    },
    {
        "materialId": "MAT005",
        "id": "MAT005",
        "materialName": "Packaged Cotton Formal Shirts (Boxed)",
        "category": "Finished Goods",
        "quantity": 600.0,
        "unit": "boxes",
        "minimumStock": 200.0,
        "supplier": "Internal Packaging Dept",
        "status": "In Stock",
        "createdAt": "2026-09-05T10:00:00Z",
        "updatedAt": "2026-09-24T16:00:00Z"
    }
]

SEED_ASSIGNMENTS = [
    {
        "assignmentId": "ASN001",
        "id": "ASN001",
        "employeeId": "EMP001",
        "employeeName": "Ramesh Kumar",
        "orderId": "ORD001",
        "productionId": "ORD001_1",
        "stage": "Cutting",
        "task": "Cut 1000 sky blue cotton shirt body patterns",
        "quantity": 1000,
        "assignedDate": "2026-09-02T10:00:00Z",
        "expectedCompletion": "2026-10-10",
        "status": "Assigned",
        "createdAt": "2026-09-02T10:00:00Z",
        "updatedAt": "2026-09-02T10:00:00Z"
    }
]

SEED_NOTIFICATIONS = [
    {
        "notificationId": "NOT001",
        "id": "NOT001",
        "userId": "USR001",
        "type": "ORDER",
        "title": "New Order Created",
        "message": "Order ORD001 has been created for ABC Fashion Inc",
        "orderId": "ORD001",
        "isRead": False,
        "createdAt": "2026-09-01T10:00:00Z"
    },
    {
        "notificationId": "NOT002",
        "id": "NOT002",
        "userId": "ALL",
        "type": "INVENTORY",
        "title": "Low Stock Alert",
        "message": "Polyester Sewing Thread Spools (Navy) quantity is below minimum stock threshold",
        "orderId": None,
        "isRead": False,
        "createdAt": "2026-09-15T12:00:00Z"
    }
]

def seed_collection(col_name, records, id_key="id"):
    """Insert seed items if they don't already exist in Firestore."""
    col_ref = db.collection(col_name)
    inserted = 0
    skipped = 0

    for item in records:
        doc_id = str(item.get(id_key))
        doc_ref = col_ref.document(doc_id)
        if doc_ref.get().exists:
            skipped += 1
        else:
            doc_ref.set(item)
            inserted += 1

    print(f"[{col_name:18}] Inserted: {inserted:2d} | Skipped (already exist): {skipped:2d}")

def run_seed():
    print("==================================================")
    print("Seeding Cloud Firestore: garmentmanager-ae69f")
    print("==================================================")

    seed_collection("users", SEED_USERS, "uid")
    seed_collection("employees", SEED_EMPLOYEES, "employeeId")
    seed_collection("products", SEED_PRODUCTS, "productId")
    seed_collection("orders", SEED_ORDERS, "orderId")
    seed_collection("production", SEED_PRODUCTION, "productionId")
    seed_collection("inventory", SEED_INVENTORY, "materialId")
    seed_collection("assignments", SEED_ASSIGNMENTS, "assignmentId")
    seed_collection("notifications", SEED_NOTIFICATIONS, "notificationId")

    # Initial audit log
    audit_ref = db.collection("auditLogs").document("LOG0001")
    if not audit_ref.get().exists:
        audit_ref.set({
            "logId": "LOG0001",
            "userId": "USR001",
            "userName": "Admin User",
            "action": "SYSTEM_INITIALIZED",
            "entityType": "system",
            "entityId": "SYSTEM",
            "description": "Initial Firestore seed completed successfully.",
            "timestamp": "2026-01-01T00:00:00Z"
        })
        print(f"[{'auditLogs':18}] Inserted:  1 | Skipped:  0")
    else:
        print(f"[{'auditLogs':18}] Inserted:  0 | Skipped:  1")

    print("==================================================")
    print("Firestore seeding completed successfully!")
    print("==================================================")

if __name__ == "__main__":
    run_seed()
