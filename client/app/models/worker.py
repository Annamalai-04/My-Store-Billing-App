from dataclasses import dataclass


@dataclass
class Worker:

    worker_id: int | None = None

    name: str = ""

    age: int = 0

    total_price_sold: float = 0.0

    today_logged_hours: float = 0.0

    attendance_percentage: float = 0.0