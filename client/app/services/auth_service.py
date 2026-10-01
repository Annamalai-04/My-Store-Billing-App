from app.services.api_service import ApiService
from app.utils.storage import set_worker, clear_worker, get_worker


class AuthService:
    def __init__(self):
        self.api = ApiService()

    def login(self, username, password):
        w = self.api.post(
            "/workers/login", {"username": username, "password": password}
        )
        set_worker(w)
        return w

    def logout(self):
        w = get_worker()
        if w and w.get("workerId"):
            self.api.post(f"/workers/{w['workerId']}/logout")
        clear_worker()
