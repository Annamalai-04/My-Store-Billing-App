from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    QHBoxLayout,
    QPushButton,
)


class BillProductTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setColumnCount(8)
        self.setHorizontalHeaderLabels([
            "SNO",
            "NAME",
            "GROUP",
            "QTY",
            "PRICE",
            "DIS.",
            "TOTAL",
            "REMOVE / UPDATE",
        ])

        self.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)

    def add_product(
        self,
        pid,
        name,
        group,
        q,
        price,
        discount,
        remove_cb,
        update_cb,
        stock=0,
    ):
        row = self.rowCount()
        self.insertRow(row)

        vals = [
            row + 1,
            name,
            group,
            q,
            f"{price:.2f}",
            f"{discount:.2f}",
            f"{max(q * price - discount, 0):.2f}",
        ]

        for c, v in enumerate(vals):
            self.setItem(
                row,
                c,
                QTableWidgetItem(str(v))
            )

        # Store product ID.
        self.item(row, 0).setData(
            Qt.ItemDataRole.UserRole,
            int(pid)
        )

        # Store available stock for checkout validation.
        self.item(row, 0).setData(
            Qt.ItemDataRole.UserRole + 1,
            int(stock or 0)
        )

        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(2, 2, 2, 2)

        remove_button = QPushButton("R")
        update_button = QPushButton("U")

        remove_button.clicked.connect(
            lambda: remove_cb(w)
        )
        update_button.clicked.connect(
            lambda: update_cb(w)
        )

        layout.addWidget(remove_button)
        layout.addWidget(update_button)

        self.setCellWidget(row, 7, w)

    def row_for_widget(self, w):
        for row in range(self.rowCount()):
            if self.cellWidget(row, 7) is w:
                return row
        return -1

    def product_id_at(self, row):
        item = self.item(row, 0)

        if item is None:
            return None

        return item.data(Qt.ItemDataRole.UserRole)

    def stock_at(self, row):
        item = self.item(row, 0)

        if item is None:
            return 0

        return int(
            item.data(Qt.ItemDataRole.UserRole + 1) or 0
        )

    def remove_widget_row(self, w):
        row = self.row_for_widget(w)

        if row >= 0:
            self.removeRow(row)
            self.renumber()

    def renumber(self):
        for row in range(self.rowCount()):
            item = self.item(row, 0)

            if item is not None:
                # Change only visible SNO.
                # Keep product ID and stock UserRole data.
                item.setText(str(row + 1))

    def items_for_checkout(self):
        items = []

        for row in range(self.rowCount()):
            product_id = self.product_id_at(row)

            if product_id is None:
                raise ValueError(
                    f"Product ID is missing for bill row {row + 1}."
                )

            quantity = int(
                self.item(row, 3).text()
            )

            available_stock = self.stock_at(row)

            if quantity > available_stock:
                name = self.item(row, 1).text()

                raise ValueError(
                    f"Stock over for {name}. "
                    f"Available: {available_stock}, "
                    f"requested: {quantity}."
                )

            items.append({
                "productId": int(product_id),
                "quantity": quantity,
                "unitPrice": float(
                    self.item(row, 4).text()
                ),
                "discount": float(
                    self.item(row, 5).text()
                ),
                "totalPrice": float(
                    self.item(row, 6).text()
                ),
            })

        return items

    def total(self):
        return sum(
            float(self.item(row, 6).text())
            for row in range(self.rowCount())
        )
