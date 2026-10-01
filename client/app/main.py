import sys
import threading

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QStackedWidget,
    QMessageBox,
)

from PySide6.QtCore import Signal, QTimer

from app.components.navbar import Navbar
from app.pages.billout_page import BillOutPage
from app.pages.productin_page import ProductInPage
from app.pages.checkhistory_page import CheckHistoryPage
from app.pages.profile_page import ProfilePage
from app.services.update_service import UpdateService


class MainWindow(QMainWindow):

    update_result = Signal(object)

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Store Billing App"
        )

        self.resize(
            1100,
            700
        )

        self.update_service = UpdateService()

        self.create_ui()

        self.update_result.connect(
            self.handle_update_result
        )

        # Check S3 shortly after the main window opens.
        # The actual network request runs in a background thread.
        QTimer.singleShot(
            1000,
            self.check_for_updates
        )

    # =====================================================
    # CREATE MAIN UI
    # =====================================================

    def create_ui(self):

        # =================================================
        # CENTRAL WIDGET
        # =================================================

        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        main_layout = QVBoxLayout(
            central_widget
        )

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        main_layout.setSpacing(0)

        # =================================================
        # NAVBAR
        # =================================================

        self.navbar = Navbar()

        main_layout.addWidget(
            self.navbar
        )

        # =================================================
        # PAGE STACK
        # =================================================

        self.pages = QStackedWidget()

        # -------------------------------------------------
        # BillOut
        # -------------------------------------------------

        self.billout_page = BillOutPage()

        # -------------------------------------------------
        # ProductIn
        # -------------------------------------------------

        self.productin_page = ProductInPage()

        # -------------------------------------------------
        # CheckHistory
        # -------------------------------------------------

        self.history_page = CheckHistoryPage()

        # -------------------------------------------------
        # Profile
        # -------------------------------------------------

        self.profile_page = ProfilePage()

        # =================================================
        # ADD PAGES
        # =================================================

        self.pages.addWidget(
            self.billout_page
        )

        self.pages.addWidget(
            self.productin_page
        )

        self.pages.addWidget(
            self.history_page
        )

        self.pages.addWidget(
            self.profile_page
        )

        main_layout.addWidget(
            self.pages
        )

        # =================================================
        # NAVBAR → PAGE NAVIGATION
        # =================================================

        self.navbar.billout_button.clicked.connect(
            lambda: self.pages.setCurrentIndex(0)
        )

        self.navbar.productin_button.clicked.connect(
            lambda: self.pages.setCurrentIndex(1)
        )

        self.navbar.history_button.clicked.connect(
            lambda: self.pages.setCurrentIndex(2)
        )

        self.navbar.profile_button.clicked.connect(
            lambda: self.pages.setCurrentIndex(3)
        )

    # =====================================================
    # UPDATE CHECK
    # =====================================================

    def check_for_updates(self):

        def worker():

            result = self.update_service.check_for_update()

            self.update_result.emit(
                result
            )

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    # =====================================================
    # HANDLE UPDATE RESULT
    # =====================================================

    def handle_update_result(self, update):

        if not update:
            return

        current_version = update["current_version"]
        latest_version = update["latest_version"]
        download_url = update["download_url"]

        message = QMessageBox(
            QMessageBox.Information,
            "Update Available",
            (
                f"A new version of MyStoreApp is available.\n\n"
                f"Current version: {current_version}\n"
                f"New version: {latest_version}\n\n"
                f"Click Update to install the new version."
            ),
            QMessageBox.NoButton,
            self,
        )

        update_button = message.addButton(
            "Update",
            QMessageBox.AcceptRole
        )

        later_button = message.addButton(
            "Later",
            QMessageBox.RejectRole
        )

        message.exec()

        if message.clickedButton() != update_button:
            return

        try:

            self.update_service.start_update(
                download_url
            )

            # The updater has started. Close this application so the
            # updater can replace MyStoreApp.exe.
            self.close()

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Update Error",
                str(exc)
            )


# =========================================================
# APPLICATION START
# =========================================================

def main():

    app = QApplication(sys.argv)

    # -----------------------------------------------------
    # Global QSS
    # -----------------------------------------------------

    try:

        with open(
            "app/styles/main.qss",
            "r",
            encoding="utf-8"
        ) as file:

            app.setStyleSheet(
                file.read()
            )

    except FileNotFoundError:

        print(
            "Warning: main.qss not found"
        )

    # -----------------------------------------------------
    # Main Window
    # -----------------------------------------------------

    window = MainWindow()

    window.show()

    # -----------------------------------------------------
    # Start Qt
    # -----------------------------------------------------

    sys.exit(
        app.exec()
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()
