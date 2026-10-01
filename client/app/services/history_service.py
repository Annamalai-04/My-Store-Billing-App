from app.services.api_service import ApiService


class HistoryService:
    def __init__(self):
        self.api = ApiService()

    def get_history(self):
        return self.api.get("/history")

    def get_worker_sessions(self, worker_id, from_date, to_date):
        return self.api.get(
            f"/workers/{worker_id}/sessions", {"from": from_date, "to": to_date}
        )
