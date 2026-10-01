from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    QLabel
)

from app.utils.style_loader import load_style


class Navbar(QWidget):

    def __init__(self):
        super().__init__()

        self.setObjectName("navbar")

        load_style(
            self,
            "app/styles/navbar.qss"
        )

        self.create_ui()

    # =====================================================
    # CREATE NAVBAR
    # =====================================================

    def create_ui(self):

        nav_layout = QHBoxLayout(self)

        nav_layout.setContentsMargins(
            20,
            8,
            20,
            8
        )

        nav_layout.setSpacing(10)

        # =================================================
        # LOGO
        # =================================================

        self.logo = QLabel("Logo")

        self.logo.setObjectName("logo")

        nav_layout.addWidget(
            self.logo
        )

        nav_layout.addSpacing(25)

        # =================================================
        # NAVIGATION BUTTONS
        # =================================================

        self.billout_button = QPushButton(
            "BillOut"
        )

        self.productin_button = QPushButton(
            "ProductIn"
        )

        self.history_button = QPushButton(
            "CheckHistory"
        )

        self.profile_button = QPushButton(
            "Profile"
        )

        # Add buttons

        nav_layout.addWidget(
            self.billout_button
        )

        nav_layout.addWidget(
            self.productin_button
        )

        nav_layout.addWidget(
            self.history_button
        )

        nav_layout.addWidget(
            self.profile_button
        )

        # Push everything to the left

        nav_layout.addStretch()