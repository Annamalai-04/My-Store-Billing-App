from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QLineEdit, QPushButton


class ProductModify(QFrame):
    def __init__(
        self,
        update_callback=None,
        delete_callback=None,
        add_stock_callback=None,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("modifyPanel")

        l = QGridLayout(self)

        t = QLabel("MODIFY")
        t.setObjectName("panelTitle")
        l.addWidget(t, 0, 0, 1, 4)

        # Search existing product by product ID, name, or barcode.
        l.addWidget(QLabel("search"), 1, 0)
        self.modify_search = QLineEdit()
        self.modify_search.setPlaceholderText("product id / name / barcode")
        l.addWidget(self.modify_search, 1, 1, 1, 3)

        fields = [
            ("name", "modify_name", 2, 0),
            ("group", "modify_group", 2, 2),
            ("barcode", "modify_barcode", 3, 0),
            ("price", "modify_price", 3, 2),
            ("dis", "modify_discount", 4, 0),
            ("stock", "modify_stock", 4, 2),
            ("exp date", "modify_exp_date", 5, 0),
            ("status", "modify_status", 5, 2),
        ]

        for label, attr, row, col in fields:
            l.addWidget(QLabel(label), row, col)
            w = QLineEdit()
            setattr(self, attr, w)
            l.addWidget(w, row, col + 1)

        self.update_button = QPushButton("upd")
        self.delete_button = QPushButton("del")
        self.add_stock_button = QPushButton("add stock")

        l.addWidget(self.update_button, 6, 1)
        l.addWidget(self.add_stock_button, 6, 2)
        l.addWidget(self.delete_button, 6, 3)

        if update_callback:
            self.update_button.clicked.connect(update_callback)

        if delete_callback:
            self.delete_button.clicked.connect(delete_callback)

        if add_stock_callback:
            self.add_stock_button.clicked.connect(add_stock_callback)

    def clear(self):
        for a in [
            "modify_search",
            "modify_name",
            "modify_group",
            "modify_barcode",
            "modify_price",
            "modify_discount",
            "modify_stock",
            "modify_exp_date",
            "modify_status",
        ]:
            getattr(self, a).clear()

        self.modify_status.setText("ACTIVE")
