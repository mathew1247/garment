from backend.repositories.firestore_repository import FirestoreRepository
from backend.utils.helpers import is_past_date

order_repo = FirestoreRepository("orders")
production_repo = FirestoreRepository("production")
inventory_repo = FirestoreRepository("inventory")
employee_repo = FirestoreRepository("employees")
notification_repo = FirestoreRepository("notifications")
audit_repo = FirestoreRepository("auditLogs")

class DashboardService:
    @staticmethod
    def get_dashboard_data():
        """
        Aggregate comprehensive dashboard statistics directly from Cloud Firestore:
        - Order counts: total, completed, pending, inProduction, delayed
        - Production stages: cutting, stitching, finishing, quality, packaging, dispatch
        - Inventory stats: inStock, lowStock, outOfStock
        - Recent orders (top 5)
        - Recent activities (from auditLogs, top 5)
        - Recent notifications (top 5)
        - Employee stats
        - Delayed orders list
        """
        orders = order_repo.get_all(sort_by="createdAt", reverse=True)
        production = production_repo.get_all(sort_by="startDate", reverse=True)
        inventory = inventory_repo.get_all()
        employees = employee_repo.get_all()
        notifications = notification_repo.get_all(sort_by="createdAt", reverse=True, limit=5)
        audit_logs = audit_repo.get_all(sort_by="timestamp", reverse=True, limit=5)

        total_orders = len(orders)
        completed_orders = 0
        pending_orders = 0
        in_production = 0
        delayed_orders_count = 0
        delayed_orders_list = []

        for ord_item in orders:
            status = ord_item.get("status", "")
            deadline = ord_item.get("deadline", "")
            is_delayed = status not in ("Completed", "Cancelled") and is_past_date(deadline)

            if is_delayed:
                delayed_orders_count += 1
                delayed_orders_list.append(ord_item)

            if status in ("Completed", "Dispatched"):
                completed_orders += 1
            elif status == "Pending":
                pending_orders += 1
            elif status in ("In Production", "In Progress", "Rework"):
                in_production += 1
            elif status == "Delayed" and not is_delayed:
                delayed_orders_count += 1
                delayed_orders_list.append(ord_item)

        # Stage active counts (stages that are In Progress or Rework)
        stage_counts = {
            "cutting": 0,
            "stitching": 0,
            "finishing": 0,
            "quality": 0,
            "packaging": 0,
            "dispatch": 0
        }
        for p in production:
            if p.get("status") in ("In Progress", "Rework"):
                st = p.get("stage", "").lower()
                if "cutting" in st:
                    stage_counts["cutting"] += 1
                elif "stitching" in st:
                    stage_counts["stitching"] += 1
                elif "finishing" in st:
                    stage_counts["finishing"] += 1
                elif "quality" in st or "qc" in st:
                    stage_counts["quality"] += 1
                elif "packaging" in st:
                    stage_counts["packaging"] += 1
                elif "dispatch" in st:
                    stage_counts["dispatch"] += 1

        # Inventory status counts
        inventory_stats = {
            "inStock": 0,
            "lowStock": 0,
            "outOfStock": 0
        }
        for item in inventory:
            st = item.get("status", "")
            if st == "In Stock":
                inventory_stats["inStock"] += 1
            elif st == "Low Stock":
                inventory_stats["lowStock"] += 1
            elif st == "Out of Stock":
                inventory_stats["outOfStock"] += 1

        total_employees = len(employees)
        active_employees = sum(1 for e in employees if e.get("status") == "Active")

        return {
            "totalOrders": total_orders,
            "completedOrders": completed_orders,
            "pendingOrders": pending_orders,
            "inProduction": in_production,
            "delayedOrders": delayed_orders_count,
            "productionStages": stage_counts,
            "inventory": inventory_stats,
            "employeeStats": {
                "totalEmployees": total_employees,
                "activeEmployees": active_employees
            },
            "recentOrders": orders[:5],
            "recentProductionActivity": production[:5],
            "recentActivities": audit_logs,
            "recentNotifications": notifications,
            "delayedOrdersList": delayed_orders_list[:5]
        }
