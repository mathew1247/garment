class PackagingModel:
    @staticmethod
    def to_dict(packaging_id, order_id, quantity, status="Completed", packed_date=None, remarks=""):
        return {
            "packagingId": packaging_id,
            "orderId": order_id,
            "quantity": int(quantity),
            "status": status,
            "packedDate": packed_date,
            "remarks": remarks or ""
        }
