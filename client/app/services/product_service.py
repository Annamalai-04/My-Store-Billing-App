from app.services.api_service import ApiService


class ProductService:
    def __init__(self):
        self.api = ApiService()

    def get_products(self, search=""):
        return self.api.get(
            "/products",
            {"search": search} if search.strip() else None
        )

    def create_product(self, product):
        return self.api.post("/products", product)

    def update_product(self, id, product):
        return self.api.put(f"/products/{id}", product)

    def delete_product(self, id):
        return self.api.delete(f"/products/{id}")

    def scan_barcode(self, barcode):
        return self.api.get(f"/products/scan/{barcode}")

    def add_stock(self, product_id, quantity):
        return self.api.patch(
            f"/products/{product_id}/add-stock",
            {"quantity": int(quantity)}
        )
