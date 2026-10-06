class InventoryModel:
    @staticmethod
    def to_dict(material_id, material_name, category, quantity, unit, minimum_stock,
                supplier="", status="In Stock", created_at=None, updated_at=None):
        return {
            "materialId": material_id,
            "materialName": material_name,
            "category": category,
            "quantity": float(quantity),
            "unit": unit,
            "minimumStock": float(minimum_stock),
            "supplier": supplier,
            "status": status,
            "createdAt": created_at,
            "updatedAt": updated_at
        }

    @staticmethod
    def calculate_status(quantity, minimum_stock):
        if quantity <= 0:
            return "Out of Stock"
        elif quantity <= minimum_stock:
            return "Low Stock"
        return "In Stock"
