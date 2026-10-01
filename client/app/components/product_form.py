from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QLineEdit, QPushButton


class ProductForm(QFrame):
    def __init__(self, add_callback=None, clear_callback=None, parent=None):
        super().__init__(parent)
        self.setObjectName("newPanel")

        l = QGridLayout(self)
        l.setContentsMargins(10, 8, 10, 8)

        t = QLabel("NEW")
        t.setObjectName("panelTitle")
        l.addWidget(t, 0, 0, 1, 4)

        # Worker-entered product details
        l.addWidget(QLabel("name"), 1, 0)
        self.new_name = QLineEdit()
        self.new_name.setObjectName("productInput")
        l.addWidget(self.new_name, 1, 1)

        l.addWidget(QLabel("group"), 1, 2)
        self.new_group = QLineEdit()
        l.addWidget(self.new_group, 1, 3)

        l.addWidget(QLabel("barcode"), 2, 0)
        self.new_barcode = QLineEdit()
        l.addWidget(self.new_barcode, 2, 1)

        l.addWidget(QLabel("stock"), 2, 2)
        self.new_stock = QLineEdit()
        l.addWidget(self.new_stock, 2, 3)

        l.addWidget(QLabel("price"), 3, 0)
        self.new_price = QLineEdit()
        l.addWidget(self.new_price, 3, 1)

        l.addWidget(QLabel("dis"), 3, 2)
        self.new_discount = QLineEdit("0")
        l.addWidget(self.new_discount, 3, 3)

        l.addWidget(QLabel("exp date"), 4, 0)
        self.new_exp_date = QLineEdit()
        l.addWidget(self.new_exp_date, 4, 1)

        l.addWidget(QLabel("status"), 4, 2)
        self.new_status = QLineEdit("ACTIVE")
        l.addWidget(self.new_status, 4, 3)

        self.add_button = QPushButton("add")
        self.add_button.setObjectName("actionButton")
        l.addWidget(self.add_button, 5, 2)

        self.new_button = QPushButton("new")
        self.new_button.setObjectName("actionButton")
        l.addWidget(self.new_button, 5, 3)

        if add_callback:
            self.add_button.clicked.connect(add_callback)

        if clear_callback:
            self.new_button.clicked.connect(clear_callback)

    def clear(self):
        self.new_name.clear()
        self.new_group.clear()
        self.new_barcode.clear()
        self.new_stock.clear()
        self.new_discount.setText("0")
        self.new_price.clear()
        self.new_exp_date.clear()
        self.new_status.setText("ACTIVE")
