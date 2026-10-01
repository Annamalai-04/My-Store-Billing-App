from collections import defaultdict
from datetime import date, timedelta, datetime

from PySide6.QtCore import Qt, QRectF, QPoint
from PySide6.QtGui import QPainter, QPen, QBrush, QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QDialog,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QDialogButtonBox,
)

from app.services.history_service import HistoryService
from app.services.auth_service import AuthService
from app.services.api_service import ApiService
from app.utils.storage import get_worker, clear_worker
from app.utils.style_loader import load_style


class DonutWidget(QWidget):
    def __init__(self, percent=0, title="Attendance", parent=None):
        super().__init__(parent)
        self.percent = percent
        self.title = title
        self.setMinimumHeight(190)

    def set_percent(self, value):
        self.percent = max(0, min(100, float(value)))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        side = min(self.width(), self.height()) - 30
        x = (self.width() - side) / 2
        y = 10

        base_pen = QPen(self.palette().mid().color(), 18)
        p.setPen(base_pen)
        p.drawArc(QRectF(x, y, side, side), 0, 360 * 16)

        value_pen = QPen(self.palette().highlight().color(), 18)
        p.setPen(value_pen)
        p.drawArc(QRectF(x, y, side, side), 90 * 16, -int(self.percent * 3.6 * 16))

        p.setPen(self.palette().text().color())
        font = QFont()
        font.setBold(True)
        font.setPointSize(16)
        p.setFont(font)
        p.drawText(
            QRectF(x, y + side * 0.35, side, 30), Qt.AlignCenter, f"{self.percent:.0f}%"
        )

        font.setPointSize(9)
        p.setFont(font)
        p.drawText(QRectF(x, y + side * 0.53, side, 25), Qt.AlignCenter, self.title)


class SimpleChart(QWidget):
    def __init__(self, values=None, mode="bar", title="", parent=None):
        super().__init__(parent)
        self.values = values or []
        self.mode = mode
        self.title = title
        self.hover = -1
        self.setMinimumHeight(220)
        self.setMouseTracking(True)

    def set_data(self, values):
        self.values = values or []
        self.hover = -1
        self.update()

    def mouseMoveEvent(self, event):
        if not self.values:
            return
        left, right = 55, 20
        width = max(1, self.width() - left - right)
        step = width / max(1, len(self.values) - (1 if self.mode == "line" else 0))
        x = event.position().x() - left
        index = round(x / step) if self.mode == "line" else int(x / step)
        self.hover = index if 0 <= index < len(self.values) else -1
        self.update()

    def leaveEvent(self, event):
        self.hover = -1
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), self.palette().base())

        if not self.values:
            p.setPen(self.palette().text().color())
            p.drawText(self.rect(), Qt.AlignCenter, "No data")
            return

        f = QFont()
        f.setBold(True)
        p.setFont(f)
        p.setPen(self.palette().text().color())
        p.drawText(10, 20, self.title)

        left, top, right, bottom = 55, 35, 20, 35
        chart = QRectF(
            left, top, self.width() - left - right, self.height() - top - bottom
        )
        maximum = max(float(v[1]) for v in self.values) or 1.0

        p.setPen(QPen(self.palette().mid().color(), 1))
        for i in range(5):
            y = chart.bottom() - chart.height() * i / 4
            p.drawLine(
                QPoint(int(chart.left()), int(y)), QPoint(int(chart.right()), int(y))
            )
            p.drawText(4, int(y + 4), f"{maximum*i/4:.0f}")

        step = chart.width() / max(
            1, len(self.values) - (1 if self.mode == "line" else 0)
        )

        if self.mode == "line":
            pts = []
            for i, (label, value) in enumerate(self.values):
                x = chart.left() + i * step
                y = chart.bottom() - chart.height() * float(value) / maximum
                pts.append((x, y))

            p.setPen(QPen(self.palette().highlight().color(), 2))
            for i in range(1, len(pts)):
                p.drawLine(
                    QPoint(int(pts[i - 1][0]), int(pts[i - 1][1])),
                    QPoint(int(pts[i][0]), int(pts[i][1])),
                )

            for i, ((label, value), (x, y)) in enumerate(zip(self.values, pts)):
                p.setBrush(QBrush(self.palette().highlight()))
                p.drawEllipse(QPoint(int(x), int(y)), 4, 4)
                if len(self.values) <= 12 or i % max(1, len(self.values) // 7) == 0:
                    p.setPen(self.palette().text().color())
                    p.drawText(
                        QRectF(x - 25, chart.bottom() + 5, 50, 25),
                        Qt.AlignHCenter,
                        str(label)[5:10],
                    )

        else:
            bar_width = max(5, step * 0.55)
            for i, (label, value) in enumerate(self.values):
                x = chart.left() + i * step + (step - bar_width) / 2
                h = chart.height() * float(value) / maximum
                y = chart.bottom() - h
                p.fillRect(
                    QRectF(x, y, bar_width, h), QBrush(self.palette().highlight())
                )
                if len(self.values) <= 10 or i % max(1, len(self.values) // 7) == 0:
                    p.setPen(self.palette().text().color())
                    p.drawText(
                        QRectF(x - 20, chart.bottom() + 5, bar_width + 40, 25),
                        Qt.AlignHCenter,
                        str(label)[5:10],
                    )

        if 0 <= self.hover < len(self.values):
            label, value = self.values[self.hover]
            p.setPen(self.palette().text().color())
            p.setBrush(QBrush(self.palette().toolTipBase()))
            box = QRectF(10, 25, min(270, self.width() - 20), 28)
            p.drawRoundedRect(box, 5, 5)
            p.drawText(box, Qt.AlignCenter, f"{label}: {float(value):.2f}")


class ProfilePage(QWidget):
    """Worker profile and live DB-backed sales/session statistics."""

    def __init__(self):
        super().__init__()
        load_style(self, "app/styles/profile_page.qss")

        self.service = HistoryService()
        self.worker = get_worker()
        self.history = []
        self.sessions = []

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 12)
        root.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("PROFILE")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()

        self.login_button = QPushButton("LOGIN")
        self.signup_button = QPushButton("SIGNUP")
        self.update_button = QPushButton("UPDATE")
        self.logout_button = QPushButton("LOGOUT")
        for button in (
            self.login_button,
            self.signup_button,
            self.update_button,
            self.logout_button,
        ):
            button.setMinimumWidth(95)
            button.setMinimumHeight(32)
            header.addWidget(button)

        self.login_button.clicked.connect(self.show_login_dialog)
        self.signup_button.clicked.connect(self.show_signup_dialog)
        self.update_button.clicked.connect(self.show_update_dialog)
        self.logout_button.clicked.connect(self.logout_worker)

        root.addLayout(header)

        info = QFrame()
        info_layout = QHBoxLayout(info)

        self.name_label = QLabel("Name: -")
        self.username_label = QLabel("Username: -")
        self.role_label = QLabel("Role: -")
        self.phone_label = QLabel("Phone: -")

        for label in (
            self.name_label,
            self.username_label,
            self.role_label,
            self.phone_label,
        ):
            label.setStyleSheet("font-size: 14px;")
            info_layout.addWidget(label)

        root.addWidget(info)

        cards = QHBoxLayout()

        self.sales_label = QLabel("₹0.00")
        self.minutes_label = QLabel("0 min")
        self.rows_label = QLabel("0")

        cards.addWidget(self._card("TOTAL SOLD", self.sales_label))
        cards.addWidget(self._card("MONTHLY LOGGED HOURS", self.minutes_label))
        cards.addWidget(self._card("SALES ROWS", self.rows_label))
        root.addLayout(cards)

        middle = QHBoxLayout()

        attendance_frame = QFrame()
        attendance_layout = QVBoxLayout(attendance_frame)
        self.attendance_chart = DonutWidget(0, "MONTHLY ATTENDANCE")
        self.attendance_detail = QLabel("0 / 0 days")
        self.attendance_detail.setAlignment(Qt.AlignCenter)
        attendance_layout.addWidget(self.attendance_chart)
        attendance_layout.addWidget(self.attendance_detail)
        middle.addWidget(attendance_frame, 1)

        self.week_chart = SimpleChart(mode="bar", title="WEEKLY LOGGED HOURS — THIS WEEK (MON-SUN)")
        middle.addWidget(self.week_chart, 2)

        root.addLayout(middle)

        self.hour_chart = SimpleChart(
            mode="line", title="TODAY'S HOURLY PRODUCT COUNT"
        )
        root.addWidget(self.hour_chart)

        root.addWidget(QLabel("RECENT SESSIONS"))

        self.session_table = QTableWidget(0, 4)
        self.session_table.setHorizontalHeaderLabels(
            ["DATE", "LOGIN", "LOGOUT", "DURATION"]
        )
        self.session_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.session_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        root.addWidget(self.session_table, 1)

        self.update_action_buttons()
        self.load_data()

    def _clear_stats(self):
        self.sales_label.setText("₹0.00")
        self.minutes_label.setText("0 min")
        self.rows_label.setText("0")
        self.attendance_chart.set_percent(0)
        self.attendance_detail.setText("0 / 0 days")
        self.week_chart.set_data([])
        self.hour_chart.set_data([])
        self.session_table.setRowCount(0)

    def update_action_buttons(self):
        signed_in = self.worker is not None
        self.login_button.setVisible(not signed_in)
        self.signup_button.setVisible(not signed_in)
        self.update_button.setVisible(signed_in)
        self.logout_button.setVisible(signed_in)

    def _dialog(self, title, fields, existing=None):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumWidth(380)
        form = QFormLayout(dialog)
        edits = {}
        existing = existing or {}

        for key, label, secret in fields:
            edit = QLineEdit()
            edit.setText(str(existing.get(key, "")))
            if secret:
                edit.setEchoMode(QLineEdit.Password)
            form.addRow(label, edit)
            edits[key] = edit

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)
        return dialog, edits

    def show_login_dialog(self):
        fields = [("username", "Username", False), ("password", "Password", True)]
        dialog, edits = self._dialog("Worker Login", fields)
        if dialog.exec() != QDialog.Accepted:
            return
        username = edits["username"].text().strip()
        password = edits["password"].text()
        if not username or not password:
            QMessageBox.warning(self, "Login", "Username and password are required.")
            return
        try:
            self.worker = AuthService().login(username, password)
            self.update_action_buttons()
            self.load_data()
            QMessageBox.information(self, "Login", "Login successful.")
        except Exception as e:
            QMessageBox.warning(self, "Login", f"Login failed:\n{e}")

    def show_signup_dialog(self):
        fields = [
            ("name", "Name", False),
            ("age", "Age", False),
            ("phone", "Phone", False),
            ("username", "Username", False),
            ("password", "Password", True),
        ]
        dialog, edits = self._dialog("Worker Signup", fields)
        if dialog.exec() != QDialog.Accepted:
            return

        name = edits["name"].text().strip()
        username = edits["username"].text().strip()
        password = edits["password"].text()
        phone = edits["phone"].text().strip()
        age_text = edits["age"].text().strip()

        if not name or not username or not password:
            QMessageBox.warning(
                self, "Signup", "Name, username and password are required."
            )
            return

        try:
            age = int(age_text) if age_text else None
            data = {
                "name": name,
                "age": age,
                "phone": phone,
                "username": username,
                "password": password,
                "role": "USER",
                "status": "ACTIVE",
            }
            ApiService().post("/workers/signup", data)
            QMessageBox.information(self, "Signup", "Account created. Please login.")
            self.show_login_dialog()
        except Exception as e:
            QMessageBox.warning(self, "Signup", f"Signup failed:\n{e}")

    def show_update_dialog(self):
        if not self.worker:
            return
        fields = [
            ("name", "Name", False),
            ("age", "Age", False),
            ("phone", "Phone", False),
            ("username", "Username", False),
            ("password", "New Password", True),
        ]
        dialog, edits = self._dialog("Update Worker", fields, self.worker)
        if dialog.exec() != QDialog.Accepted:
            return

        age_text = edits["age"].text().strip()
        data = {
            "name": edits["name"].text().strip(),
            "age": int(age_text) if age_text else None,
            "phone": edits["phone"].text().strip(),
            "username": edits["username"].text().strip(),
        }
        new_password = edits["password"].text()
        if new_password:
            data["password"] = new_password

        try:
            self.worker = ApiService().put(f"/workers/{self.worker['workerId']}", data)
            from app.utils.storage import set_worker

            set_worker(self.worker)
            self.update_action_buttons()
            self.load_data()
            QMessageBox.information(self, "Update", "Profile updated successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Update", f"Update failed:\n{e}")

    def logout_worker(self):
        try:
            AuthService().logout()
        except Exception as e:
            QMessageBox.warning(self, "Logout", f"Logout failed:\n{e}")
            return
        self.worker = None
        self.history = []
        self.sessions = []
        self.update_action_buttons()
        self.load_data()
        QMessageBox.information(self, "Logout", "Logged out successfully.")

    @staticmethod
    def _parse_date(value):
        if not value:
            return None
        try:
            return datetime.fromisoformat(str(value).replace("Z", "")).date()
        except ValueError:
            try:
                return date.fromisoformat(str(value)[:10])
            except ValueError:
                return None

    @staticmethod
    def _card(title, value_label):
        frame = QFrame()
        layout = QVBoxLayout(frame)
        t = QLabel(title)
        t.setStyleSheet("font-weight: bold;")
        value_label.setStyleSheet("font-size: 19px; font-weight: bold;")
        layout.addWidget(t)
        layout.addWidget(value_label)
        return frame

    def load_data(self):
        if not self.worker:
            self.name_label.setText("Name: Not signed in")
            self.username_label.setText("Username: -")
            self.role_label.setText("Role: -")
            self.phone_label.setText("Phone: -")
            self._clear_stats()
            return

        self.name_label.setText(f"Name: {self.worker.get('name', '-')}")
        self.username_label.setText(f"Username: {self.worker.get('username', '-')}")
        self.role_label.setText(f"Role: {self.worker.get('role', '-')}")
        self.phone_label.setText(f"Phone: {self.worker.get('phone', '-')}")

        try:
            today = date.today()

            # Monthly session range.
            month_start = today.replace(day=1)

            self.history = self.service.get_history() or []

            # Load all sessions from the first day of this month
            # through today. Attendance and monthly logged hours
            # are both calculated from this same session data.
            self.sessions = (
                self.service.get_worker_sessions(
                    self.worker["workerId"],
                    str(month_start),
                    str(today)
                )
                or []
            )

            # The weekly chart still uses the current Monday-Sunday week.
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)

            worker_id = self.worker["workerId"]

            worker_history = [
                x for x in self.history
                if x.get("workerId") == worker_id
            ]

            # Keep total sold and sales rows based on the
            # worker's available history.
            total_sales = sum(
                float(x.get("totalPrice") or 0)
                for x in worker_history
            )
            total_rows = len(worker_history)

            self.sales_label.setText(f"₹{total_sales:.2f}")
            self.rows_label.setText(str(total_rows))

            # -----------------------------
            # MONTHLY ATTENDANCE
            # -----------------------------
            # Do NOT count days before the worker joined.
            #
            # Example:
            # Joined: 2026-10-15
            # Month:  October 2026
            # Eligible attendance starts on Oct 15.
            #
            # Oct 1-14 are neither present nor absent.
            # If 8 of Oct 15-31 were logged:
            # 8 / 17 = 47% attendance.
            # -----------------------------
            joined_date = self._parse_date(
                self.worker.get("joinedDate")
                or self.worker.get("joined_date")
            )

            # Fallback only when joinedDate is not supplied by the API.
            # This keeps the profile usable, but the Worker API should
            # ideally return the real joinedDate.
            if joined_date is None:
                known_session_dates = [
                    self._parse_date(
                        x.get("sessionDate") or x.get("loginTime")
                    )
                    for x in self.sessions
                ]
                known_session_dates = [
                    d for d in known_session_dates if d is not None
                ]
                if known_session_dates:
                    joined_date = min(known_session_dates)

            attendance_start = month_start
            if joined_date is not None:
                attendance_start = max(month_start, joined_date)

            if attendance_start <= today:
                eligible_days = (today - attendance_start).days + 1
            else:
                eligible_days = 0

            session_days = {
                self._parse_date(
                    x.get("sessionDate") or x.get("loginTime")
                )
                for x in self.sessions
            }
            session_days.discard(None)

            attendance_days = {
                d for d in session_days
                if attendance_start <= d <= today
            }

            logged_days = len(attendance_days)

            attendance = (
                logged_days / eligible_days * 100
                if eligible_days > 0
                else 0
            )

            self.attendance_chart.title = (
                f"{today.strftime('%B %Y')} ATTENDANCE"
            )
            self.attendance_chart.set_percent(attendance)
            self.attendance_detail.setText(
                f"{logged_days} / {eligible_days} days logged"
            )

            # -----------------------------
            # WEEKLY BAR CHART
            # Always Monday -> Sunday.
            # -----------------------------
            daily_minutes = defaultdict(int)

            for session in self.sessions:
                d = self._parse_date(
                    session.get("sessionDate")
                    or session.get("loginTime")
                )

                if d and week_start <= d <= week_end:
                    daily_minutes[d] += int(
                        session.get("durationMinutes") or 0
                    )

            week_values = []

            for offset in range(7):
                d = week_start + timedelta(days=offset)
                # Convert the daily logged duration from minutes to hours
                # for the chart.
                week_values.append(
                    (
                        d.strftime("%a"),
                        daily_minutes.get(d, 0) / 60.0
                    )
                )

            self.week_chart.set_data(week_values)

            # -----------------------------
            # MONTHLY LOGGED HOURS
            #
            # Every login/logout session in the
            # current month is counted separately.
            # Logout breaks are not counted.
            # -----------------------------
            monthly_minutes = 0

            for session in self.sessions:
                d = self._parse_date(
                    session.get("sessionDate")
                    or session.get("loginTime")
                )

                if d and month_start <= d <= today:
                    monthly_minutes += int(
                        session.get("durationMinutes") or 0
                    )

            self.minutes_label.setText(
                f"{monthly_minutes // 60}h {monthly_minutes % 60:02d}m"
            )

            # -----------------------------
            # TODAY'S SESSIONS
            # Keep this separate from the monthly logged-hours total.
            # It is used only for the recent-session table and today's
            # hourly product chart.
            # -----------------------------
            today_sessions = []

            for session in self.sessions:
                d = self._parse_date(
                    session.get("sessionDate")
                    or session.get("loginTime")
                )

                if d == today:
                    today_sessions.append(session)

            # -----------------------------
            # TODAY'S HOURLY PRODUCT COUNT
            # -----------------------------
            hourly = defaultdict(int)

            for row in worker_history:
                stamp = row.get("saleDate")

                try:
                    dt = datetime.fromisoformat(
                        str(stamp).replace("Z", "")
                    )

                    if dt.date() == today:
                        hourly[dt.hour] += int(
                            row.get("quantity") or 0
                        )

                except (ValueError, TypeError):
                    pass

            hour_values = [
                (f"{h:02d}:00", hourly.get(h, 0))
                for h in range(24)
            ]

            self.hour_chart.set_data(hour_values)

            # -----------------------------
            # TODAY'S LOGIN/LOGOUT SESSIONS
            # -----------------------------
            today_sessions.sort(
                key=lambda s: str(
                    s.get("loginTime") or ""
                ),
                reverse=True
            )

            self.session_table.setRowCount(0)

            for i, session in enumerate(
                today_sessions[:20],
                start=1
            ):
                self.session_table.insertRow(i - 1)

                login = str(
                    session.get("loginTime") or ""
                )
                logout = str(
                    session.get("logoutTime") or ""
                )

                duration = int(
                    session.get("durationMinutes") or 0
                )

                values = [
                    session.get("sessionDate", str(today)),
                    login.replace("T", " ")[:19],
                    logout.replace("T", " ")[:19]
                    if logout else "-",
                    f"{duration // 60}h {duration % 60:02d}m",
                ]

                for col, value in enumerate(values):
                    self.session_table.setItem(
                        i - 1,
                        col,
                        QTableWidgetItem(str(value))
                    )

        except Exception as e:
            QMessageBox.warning(
                self,
                "Profile",
                f"Could not load profile data:\n{e}"
            )

