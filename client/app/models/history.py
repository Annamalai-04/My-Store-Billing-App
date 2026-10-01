from dataclasses import dataclass


@dataclass
class History:

    history_id: int | None = None

    product_name: str = ""

    quantity: int = 0

    total_price: float = 0.0

    updated_date: str = ""

    exp_date: str = ""

    stock: int = 0

    worker_name: str = ""