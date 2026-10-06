class ProductionModel:
    @staticmethod
    def to_dict(production_id, order_id, stage, status="Pending", assigned_employee_id=None,
                assigned_employee_name=None, quantity=0, completed_quantity=0, progress=0,
                start_date=None, expected_completion=None, completed_date=None, remarks=""):
        return {
            "productionId": production_id,
            "orderId": order_id,
            "stage": stage,
            "status": status,
            "assignedEmployeeId": assigned_employee_id,
            "assignedEmployeeName": assigned_employee_name,
            "quantity": int(quantity),
            "completedQuantity": int(completed_quantity),
            "progress": int(progress),
            "startDate": start_date,
            "expectedCompletion": expected_completion,
            "completedDate": completed_date,
            "remarks": remarks or ""
        }
