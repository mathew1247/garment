from backend.repositories.firestore_repository import FirestoreRepository

product_repo = FirestoreRepository("products")

class ProductService:
    @staticmethod
    def create_product(data):
        """Create a new product in Firestore."""
        prod_id = data.get("productId")
        if prod_id:
            prod_id = str(prod_id).strip()
            existing = product_repo.get_by_id(prod_id)
            if existing:
                return None, f"Product with ID '{prod_id}' already exists"
        else:
            count = product_repo.count() + 1
            prod_id = f"PRD{count:03d}"

        product_record = {
            "productId": prod_id,
            "id": prod_id,
            "productCode": data.get("productCode", f"CODE-{prod_id}"),
            "productName": data.get("productName", "").strip(),
            "productType": data.get("productType", "General").strip(),
            "description": data.get("description", ""),
            "fabricType": data.get("fabricType", ""),
            "availableSizes": data.get("availableSizes", ["S", "M", "L", "XL"]),
            "colors": data.get("colors", [])
        }
        return product_repo.create(product_record, doc_id=prod_id), None

    @staticmethod
    def get_products():
        """Retrieve all products."""
        return product_repo.get_all(sort_by="productName")

    @staticmethod
    def get_product_by_id(product_id):
        """Retrieve product by ID."""
        return product_repo.get_by_id(product_id)

    @staticmethod
    def update_product(product_id, update_data):
        """Update product details."""
        prod = product_repo.get_by_id(product_id)
        if not prod:
            return None, "Product not found"
        updated = product_repo.update(product_id, update_data)
        return updated, None

    @staticmethod
    def delete_product(product_id):
        """Delete product."""
        return product_repo.delete(product_id)
