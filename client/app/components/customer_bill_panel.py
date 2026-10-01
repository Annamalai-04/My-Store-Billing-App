from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton
)


class CustomerBillPanel(QFrame):

    checkout_requested = Signal()
    remove_requested = Signal()

    def __init__(self):
        super().__init__()

        self.setObjectName(
            "rightPanel"
        )

        self.create_ui()

    def create_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            20, 25, 20, 20
        )

        layout.setSpacing(15)

        # Date
        date_layout = QHBoxLayout()

        date_layout.addWidget(
            QLabel("Date")
        )

        self.date_input = QLineEdit()

        self.date_input.setObjectName(
            "rightInput"
        )

        date_layout.addWidget(
            self.date_input
        )

        layout.addLayout(
            date_layout
        )

        # Phone
        phone_layout = QHBoxLayout()

        phone_layout.addWidget(
            QLabel("Phone")
        )

        self.phone_input = QLineEdit()

        self.phone_input.setObjectName(
            "rightInput"
        )

        phone_layout.addWidget(
            self.phone_input
        )

        layout.addLayout(
            phone_layout
        )

        # Total
        total_layout = QHBoxLayout()

        total_layout.addWidget(
            QLabel("Total")
        )

        self.total_input = QLineEdit()

        self.total_input.setObjectName(
            "rightInput"
        )

        self.total_input.setReadOnly(True)

        self.total_input.setText(
            "0.00"
        )

        total_layout.addWidget(
            self.total_input
        )

        layout.addLayout(
            total_layout
        )

        # View
        self.view_button = QPushButton(
            "View"
        )

        self.view_button.setObjectName(
            "bigButton"
        )

        layout.addWidget(
            self.view_button
        )

        # Checkout
        self.checkout_button = QPushButton(
            "Checkout"
        )

        self.checkout_button.setObjectName(
            "checkoutButton"
        )

        self.checkout_button.clicked.connect(
            self.checkout_requested.emit
        )

        layout.addWidget(
            self.checkout_button
        )

        # Bottom buttons
        bottom_layout = QHBoxLayout()

        self.draft_button = QPushButton(
            "Draft"
        )

        self.draft_button.setObjectName(
            "smallButton"
        )

        self.remove_button = QPushButton(
            "Remove"
        )

        self.remove_button.setObjectName(
            "smallButton"
        )

        self.remove_button.clicked.connect(
            self.remove_requested.emit
        )

        bottom_layout.addWidget(
            self.draft_button
        )

        bottom_layout.addWidget(
            self.remove_button
        )

        layout.addLayout(
            bottom_layout
        )

        layout.addStretch()

    # =====================================================
    # UPDATE TOTAL
    # =====================================================

    def set_total(self, total):

        self.total_input.setText(
            f"{total:.2f}"
        )

    # =====================================================
    # CUSTOMER DATA
    # =====================================================

    def get_phone(self):

        return self.phone_input.text().strip()

    def get_date(self):

        return self.date_input.text().strip()