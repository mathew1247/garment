class OrderModel:
    """Order representation."""
    @staticmethod
    def to_dict(order_id, customer_name, customer_contact, product_name, product_type,
                quantity, deadline, specifications="", fabric_type="", color="",
                sizes=None, priority="Medium", status="Pending", current_stage="Cutting",
                created_by=None, created_at=None, updated_at=None):
        return {
            "orderId": order_id,
            "customerName": customer_name,
            "customerContact": customer_contact,
            "productName": product_name,
            "productType": product_type,
            "quantity": int(quantity),
            "deadline": deadline,
            "specifications": specifications,
            "fabricType": fabric_type,
            "color": color,
            "sizes": sizes or [],
            "priority": priority,
            "status": status,
            "currentStage": current_stage,
            "createdBy": created_by,
            "createdAt": created_at,
            "updatedAt": updated_at
        }
