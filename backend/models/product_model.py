class ProductModel:
    @staticmethod
    def to_dict(product_id, product_code, product_name, product_type,
                description="", fabric_type="", available_sizes=None,
                colors=None, created_at=None, updated_at=None):
        return {
            "productId": product_id,
            "productCode": product_code,
            "productName": product_name,
            "productType": product_type,
            "description": description,
            "fabricType": fabric_type,
            "availableSizes": available_sizes or ["S", "M", "L", "XL"],
            "colors": colors or [],
            "createdAt": created_at,
            "updatedAt": updated_at
        }
