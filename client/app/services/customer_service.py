from app.services.api_service import ApiService


class CustomerService:
    def __init__(self):
        self.api = ApiService()

    def all(self):
        return self.api.get("/customers")

    def find_or_create(self, name, phone):
        return self.api.post(
            "/customers/find-or-create", {"name": name, "phone": phone}
        )
