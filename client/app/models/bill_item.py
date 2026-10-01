from dataclasses import dataclass


@dataclass
class BillItem:

    name: str
    quantity: int
    price: float
    discount: float = 0.0

    @property
    def total(self):
        total = (
            self.quantity * self.price
        ) - self.discount

        return max(total, 0.0)