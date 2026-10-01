from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QLineEdit, QPushButton


class BillProductEntry(QFrame):
    def __init__(self, add_callback=None, scan_callback=None, clear_callback=None, parent=None):
        super().__init__(parent)
        self.setObjectName("productEntryFrame")

        self.available_stock = 0

        l = QGridLayout(self)

        l.addWidget(QLabel("Name"), 0, 0)
        self.name_input = QLineEdit()
        l.addWidget(self.name_input, 0, 1)

        l.addWidget(QLabel("Group"), 0, 2)
        self.group_input = QLineEdit()
        l.addWidget(self.group_input, 0, 3)

        l.addWidget(QLabel("Quantity"), 1, 0)
        self.quantity_input = QLineEdit()
        l.addWidget(self.quantity_input, 1, 1)

        l.addWidget(QLabel("Price"), 1, 2)
        self.price_input = QLineEdit()
        l.addWidget(self.price_input, 1, 3)

        l.addWidget(QLabel("Discount"), 2, 0)
        self.discount_input = QLineEdit("0")
        l.addWidget(self.discount_input, 2, 1)

        self.add_button = QPushButton("Add")
        l.addWidget(self.add_button, 2, 2)

        l.addWidget(QLabel("Total"), 3, 0)
        self.total_input = QLineEdit("0.00")
        self.total_input.setReadOnly(True)
        l.addWidget(self.total_input, 3, 1)

        self.scan_button = QPushButton("Scan")
        l.addWidget(self.scan_button, 3, 2)

        if add_callback:
            self.add_button.clicked.connect(add_callback)
        if scan_callback:
            self.scan_button.clicked.connect(scan_callback)


    def set_stock(self, stock):
        try:
            self.available_stock = max(int(stock or 0), 0)
        except (TypeError, ValueError):
            self.available_stock = 0

        # Do not block typing with a validator. The page performs the
        # final validation and shows the exact stock message.
        self.quantity_input.setProperty("available_stock", self.available_stock)

        if self.available_stock <= 0:
            self.quantity_input.setToolTip("Product stock over")
        else:
            self.quantity_input.setToolTip(
                f"Available stock: {self.available_stock}"
            )

    def stock(self):
        return self.available_stock

    def clear(self):
        self.name_input.clear()
        self.group_input.clear()
        self.quantity_input.clear()
        self.price_input.clear()
        self.discount_input.setText("0")
        self.total_input.setText("0.00")
        self.available_stock = 0
        self.quantity_input.setProperty("available_stock", 0)
        self.quantity_input.setToolTip("")
        self.name_input.setProperty("product_id", None)
