from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton
)


class ProfileInfo(QFrame):

    logout_requested = Signal()
    update_requested = Signal()

    def __init__(self, worker):

        super().__init__()

        self.worker = worker

        self.setObjectName(
            "profileInfoPanel"
        )

        self.create_ui()

    # =====================================================
    # UI
    # =====================================================

    def create_ui(self):

        layout = QGridLayout(self)

        layout.setContentsMargins(
            12,
            12,
            12,
            8
        )

        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(8)

        # -------------------------------------------------
        # NAME
        # -------------------------------------------------

        layout.addWidget(
            QLabel("name"),
            0,
            0
        )

        self.name_input = QLineEdit()

        self.name_input.setObjectName(
            "profileEntry"
        )

        self.name_input.setText(
            self.worker.name
        )

        layout.addWidget(
            self.name_input,
            0,
            1
        )

        # -------------------------------------------------
        # AGE
        # -------------------------------------------------

        layout.addWidget(
            QLabel("age"),
            0,
            2
        )

        self.age_input = QLineEdit()

        self.age_input.setObjectName(
            "ageEntry"
        )

        self.age_input.setText(
            str(self.worker.age)
        )

        layout.addWidget(
            self.age_input,
            0,
            3
        )

        # -------------------------------------------------
        # TOTAL PRICE SOLD
        # -------------------------------------------------

        layout.addWidget(
            QLabel("total price\nsold"),
            1,
            0
        )

        self.total_sold_input = QLineEdit()

        self.total_sold_input.setObjectName(
            "profileEntry"
        )

        self.total_sold_input.setText(
            f"{self.worker.total_price_sold:.2f}"
        )

        self.total_sold_input.setReadOnly(
            True
        )

        layout.addWidget(
            self.total_sold_input,
            1,
            1
        )

        # -------------------------------------------------
        # LOGOUT
        # -------------------------------------------------

        self.logout_button = QPushButton(
            "logout"
        )

        self.logout_button.setObjectName(
            "profileButton"
        )

        self.logout_button.clicked.connect(
            self.logout_requested.emit
        )

        layout.addWidget(
            self.logout_button,
            2,
            0
        )

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------

        self.update_button = QPushButton(
            "update"
        )

        self.update_button.setObjectName(
            "profileButton"
        )

        self.update_button.clicked.connect(
            self.update_requested.emit
        )

        layout.addWidget(
            self.update_button,
            2,
            1
        )

        # -------------------------------------------------
        # TODAY LOGGED HOURS
        # -------------------------------------------------

        self.today_hours_button = QPushButton(
            "today\nlogged in hr"
        )

        self.today_hours_button.setObjectName(
            "profileButton"
        )

        self.today_hours_button.setEnabled(
            False
        )

        layout.addWidget(
            self.today_hours_button,
            2,
            2,
            1,
            2
        )

        self.update_hours()

    # =====================================================
    # UPDATE HOURS
    # =====================================================

    def update_hours(self):

        self.today_hours_button.setText(
            f"today\n"
            f"logged {self.worker.today_logged_hours:.1f} hr"
        )

    # =====================================================
    # UPDATE WORKER
    # =====================================================

    def set_worker(self, worker):

        self.worker = worker

        self.name_input.setText(
            worker.name
        )

        self.age_input.setText(
            str(worker.age)
        )

        self.total_sold_input.setText(
            f"{worker.total_price_sold:.2f}"
        )

        self.update_hours()