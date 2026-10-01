from app.services.api_service import ApiService


class BillingService:
    def __init__(self):
        self.api = ApiService()

    def checkout(self, customer_id, worker_id, customer_phone, items):
        return self.api.post(
            "/billing/checkout",
            {
                "customerId": customer_id,
                "workerId": worker_id,
                "customerPhone": customer_phone,
                "items": items,
            },
        )
