from dataclasses import dataclass


@dataclass
class Product:
    product_id: int | None = None
    name: str = ""
    group_name: str = ""
    barcode: str = ""
    price: float = 0.0
    discount: float = 0.0
    stock: int = 0
    expiry_date: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    status: str = "ACTIVE"

    @classmethod
    def from_dict(cls, d):
        return cls(
            d.get("productId"),
            d.get("name", ""),
            d.get("groupName", ""),
            d.get("barcode", ""),
            float(d.get("price") or 0),
            float(d.get("discount") or 0),
            int(d.get("stock") or 0),
            d.get("expiryDate"),
            d.get("createdAt"),
            d.get("updatedAt"),
            d.get("status", "ACTIVE"),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "groupName": self.group_name,
            "barcode": self.barcode,
            "price": self.price,
            "discount": self.discount,
            "stock": self.stock,
            "expiryDate": self.expiry_date,
        }
