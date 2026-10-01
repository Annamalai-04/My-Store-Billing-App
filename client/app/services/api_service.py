import requests
from app.utils.constants import API_BASE_URL, REQUEST_TIMEOUT


class ApiService:
    def __init__(self, base_url=API_BASE_URL):
        self.base_url = base_url.rstrip("/")

    def get(self, path, params=None):
        r = requests.get(self.base_url + path, params=params, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()

    def post(self, path, data=None):
        r = requests.post(self.base_url + path, json=data, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()

    def put(self, path, data=None):
        r = requests.put(self.base_url + path, json=data, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()

    def patch(self, path, data=None):
        r = requests.patch(
            self.base_url + path,
            json=data,
            timeout=REQUEST_TIMEOUT
        )
        r.raise_for_status()
        return r.json()

    def delete(self, path):
        r = requests.delete(self.base_url + path, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return True
