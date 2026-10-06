from backend.repositories.firestore_repository import FirestoreRepository
from backend.services.employee_service import EmployeeService

order_repo = FirestoreRepository("orders")
production_repo = FirestoreRepository("production")
employee_repo = FirestoreRepository("employees")
inventory_repo = FirestoreRepository("inventory")
transaction_repo = FirestoreRepository("inventoryTransactions")

class ReportService:
    @staticmethod
    def get_production_report(stage=None, status=None, employee_id=None):
        """Generate production performance and stage statistics from Firestore."""
        filters = {}
        if stage:
            filters["stage"] = stage
        if status:
            filters["status"] = status
        if employee_id:
            filters["assignedEmployeeId"] = employee_id

        filtered = production_repo.get_all(filters=filters)

        total_production = len(filtered)
        completed_production = sum(1 for p in filtered if p.get("status") == "Completed")
        pending_production = sum(1 for p in filtered if p.get("status") in ("Pending", "In Progress"))
        failed_rework_production = sum(1 for p in filtered if p.get("status") in ("Failed", "Rework"))

        stage_wise = {}
        for p in filtered:
            st = p.get("stage", "Unknown")
            if st not in stage_wise:
                stage_wise[st] = {
                    "total": 0,
                    "completed": 0,
                    "inProgress": 0,
                    "quantity": 0,
                    "completedQuantity": 0
                }
            stage_wise[st]["total"] += 1
            stage_wise[st]["quantity"] += p.get("quantity", 0)
            stage_wise[st]["completedQuantity"] += p.get("completedQuantity", 0)
            if p.get("status") == "Completed":
                stage_wise[st]["completed"] += 1
            elif p.get("status") == "In Progress":
                stage_wise[st]["inProgress"] += 1

        return {
            "totalProduction": total_production,
            "completedProduction": completed_production,
            "pendingProduction": pending_production,
            "failedReworkProduction": failed_rework_production,
            "stageWiseStatistics": stage_wise,
            "records": filtered
        }

    @staticmethod
    def get_order_report(status=None, priority=None):
        """Generate summary report for orders."""
        filters = {}
        if status:
            filters["status"] = status
        if priority:
            filters["priority"] = priority

        filtered = order_repo.get_all(filters=filters)

        total_orders = len(filtered)
        completed = sum(1 for o in filtered if o.get("status") == "Completed")
        pending = sum(1 for o in filtered if o.get("status") == "Pending")
        in_production = sum(1 for o in filtered if o.get("status") in ("In Production", "Rework"))
        delayed = sum(1 for o in filtered if o.get("status") == "Delayed")

        return {
            "totalOrders": total_orders,
            "completed": completed,
            "pending": pending,
            "inProduction": in_production,
            "delayed": delayed,
            "orders": filtered
        }

    @staticmethod
    def get_employee_report(department=None):
        """Generate performance report across employees."""
        employees = employee_repo.get_all()
        if department:
            employees = [e for e in employees if e.get("department", "").lower() == department.lower()]

        report_list = []
        for emp in employees:
            perf, _, _ = EmployeeService.get_employee_performance(emp.get("employeeId") or emp.get("id"))
            if perf:
                report_list.append(perf)

        return {
            "totalEmployees": len(report_list),
            "employees": report_list
        }

    @staticmethod
    def get_inventory_report(category=None):
        """Generate inventory stock and movement report."""
        filters = {"category": category} if category else None
        inventory = inventory_repo.get_all(filters=filters)

        total_materials = len(inventory)
        low_stock = sum(1 for i in inventory if i.get("status") == "Low Stock")
        out_of_stock = sum(1 for i in inventory if i.get("status") == "Out of Stock")

        transactions = transaction_repo.get_all(sort_by="createdAt", reverse=True, limit=20)

        return {
            "totalMaterials": total_materials,
            "lowStock": low_stock,
            "outOfStock": out_of_stock,
            "stockMovement": transactions,
            "materials": inventory
        }
