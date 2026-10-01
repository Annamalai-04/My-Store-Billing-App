from collections import defaultdict
from datetime import date, timedelta, datetime

from PySide6.QtCore import Qt, QRectF, QPoint
from PySide6.QtGui import QPainter, QPen, QBrush, QFont
import requests

from app.services.product_service import ProductService

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QMessageBox, QScrollArea
)

from app.services.history_service import HistoryService
from app.utils.style_loader import load_style
from app.utils.constants import API_BASE_URL
from concurrent.futures import ThreadPoolExecutor


class SalesChart(QWidget):
    """Small dependency-free line/bar chart with exact hover values."""

    def __init__(self, values=None, mode="line", title="", parent=None):
        super().__init__(parent)
        self.values = values or []
        self.mode = mode
        self.title = title
        self.setMinimumHeight(230)
        self.setMouseTracking(True)
        self.hover_index = -1

    def set_data(self, values):
        self.values = values or []
        self.hover_index = -1
        self.update()

    def mouseMoveEvent(self, event):
        if not self.values:
            self.hover_index = -1
            self.update()
            return

        left, right = 55, 20
        width = max(1, self.width() - left - right)
        step = width / max(1, len(self.values) - 1 if self.mode == "line" else len(self.values))
        x = event.position().x() - left

        if self.mode == "line":
            idx = round(x / step) if step else 0
        else:
            idx = int(x / step) if step else 0

        self.hover_index = idx if 0 <= idx < len(self.values) else -1
        self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.hover_index = -1
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), self.palette().base())

        if not self.values:
            p.setPen(self.palette().text().color())
            p.drawText(self.rect(), Qt.AlignCenter, "No data")
            return

        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(10)
        p.setFont(title_font)
        p.setPen(self.palette().text().color())
        p.drawText(12, 20, self.title)

        left, top, right, bottom = 55, 35, 20, 35
        chart = QRectF(left, top, max(1, self.width()-left-right), max(1, self.height()-top-bottom))

        max_value = max(float(v[1]) for v in self.values)
        if max_value <= 0:
            max_value = 1.0

        pen = QPen(self.palette().mid().color(), 1)
        p.setPen(pen)
        for i in range(5):
            y = chart.bottom() - chart.height() * i / 4
            p.drawLine(QPoint(int(chart.left()), int(y)), QPoint(int(chart.right()), int(y)))
            p.drawText(5, int(y + 4), f"{max_value * i / 4:.0f}")

        n = len(self.values)
        step = chart.width() / max(1, n - 1 if self.mode == "line" else n)

        if self.mode == "bar":
            bar_width = max(4.0, step * 0.55)
            for i, (label, value) in enumerate(self.values):
                x = chart.left() + i * step + (step - bar_width) / 2
                h = chart.height() * float(value) / max_value
                y = chart.bottom() - h
                p.fillRect(QRectF(x, y, bar_width, h), QBrush(self.palette().highlight()))
                if i == self.hover_index:
                    p.setPen(QPen(self.palette().text().color(), 2))
                    p.drawRect(QRectF(x, y, bar_width, h))
                if n <= 10 or i % max(1, n // 7) == 0:
                    p.setPen(self.palette().text().color())
                    p.drawText(QRectF(x-35, chart.bottom()+5, bar_width+70, 30),
                               Qt.AlignHCenter | Qt.AlignTop, str(label))

        else:
            points = []
            for i, (label, value) in enumerate(self.values):
                x = chart.left() + i * step
                y = chart.bottom() - chart.height() * float(value) / max_value
                points.append((x, y))

            p.setPen(QPen(self.palette().highlight().color(), 2))
            for i in range(1, len(points)):
                p.drawLine(QPoint(int(points[i-1][0]), int(points[i-1][1])),
                           QPoint(int(points[i][0]), int(points[i][1])))

            for i, ((label, value), (x, y)) in enumerate(zip(self.values, points)):
                p.setBrush(QBrush(self.palette().highlight()))
                p.setPen(QPen(self.palette().highlight().color(), 1))
                p.drawEllipse(QPoint(int(x), int(y)), 4, 4)
                if n <= 12 or i % max(1, n // 7) == 0:
                    p.setPen(self.palette().text().color())
                    p.drawText(QRectF(x-25, chart.bottom()+5, 50, 25),
                               Qt.AlignHCenter | Qt.AlignTop, str(label)[5:10])

        if 0 <= self.hover_index < len(self.values):
            label, value = self.values[self.hover_index]
            text = f"{label}: {float(value):.2f}"
            p.setPen(QPen(self.palette().text().color(), 1))
            p.setBrush(QBrush(self.palette().toolTipBase()))
            box = QRectF(10, 25, min(260, self.width()-20), 28)
            p.drawRoundedRect(box, 5, 5)
            p.drawText(box, Qt.AlignCenter, text)


class CheckHistoryPage(QWidget):
    """Database-backed sales history, daily table and sales charts."""

    def __init__(self):
        super().__init__()
        load_style(self, "app/styles/checkhistory_page.qss")

        self.service = HistoryService()
        self.history = []
        self.daily_totals = {}

        self.worker_names = {}
        self.product_names = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 12)
        root.setSpacing(10)

        title = QLabel("CHECK HISTORY")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        root.addWidget(title)

        self.summary = QLabel("Loading history...")
        root.addWidget(self.summary)

        table_frame = QFrame()
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)

        table_title = QLabel("TODAY HISTORY")
        table_title.setStyleSheet("font-weight: bold;")
        table_layout.addWidget(table_title)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "SNO", "WORKER", "PRODUCT", "QTY",
            "PRICE", "DIS.", "TOTAL"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table_layout.addWidget(self.table)
        root.addWidget(table_frame, 1)

        charts = QHBoxLayout()
        self.month_chart = SalesChart(mode="line", title="MONTHLY SALES — LAST 30 DAYS")
        self.week_chart = SalesChart(mode="bar", title="WEEKLY SALES — LAST 4 WEEKS")
        charts.addWidget(self.month_chart, 1)
        charts.addWidget(self.week_chart, 1)
        root.addLayout(charts)

        self.load_history()

    def refresh(self):
        """Reload the latest history, workers and products."""
        self.load_history()

    @staticmethod
    def _parse_date(value):
        if not value:
            return None
        text = str(value)
        try:
            return datetime.fromisoformat(text.replace("Z", "")).date()
        except ValueError:
            try:
                return date.fromisoformat(text[:10])
            except ValueError:
                return None

    def load_history(self):
        try:
            # Load independent API data in parallel.
            # This avoids waiting for products, workers and history one-by-one.
            with ThreadPoolExecutor(max_workers=3) as executor:
                products_future = executor.submit(self._load_products)
                workers_future = executor.submit(self._load_workers)
                history_future = executor.submit(self.service.get_history)

                self.product_names = products_future.result()
                self.worker_names = workers_future.result()
                self.history = history_future.result() or []

            self.build_ui_data()

        except Exception as e:
            self.history = []
            self.summary.setText("Could not load history.")
            QMessageBox.warning(self, "History", f"Could not load history:\n{e}")

    def _load_products(self):
        try:
            products = ProductService().get_products() or []
            return {
                str(p.get("productId")): p.get("name", "-")
                for p in products
                if p.get("productId") is not None
            }
        except Exception:
            return {}

    def _load_workers(self):
        try:
            response = requests.get(
                f"{API_BASE_URL}/workers",
                timeout=5
            )
            response.raise_for_status()
            workers = response.json() or []
            return {
                str(w.get("workerId")): w.get("name", "-")
                for w in workers
                if w.get("workerId") is not None
            }
        except Exception:
            return {}

    def build_ui_data(self):
        today = date.today()
        daily = defaultdict(float)

        for row in self.history:
            d = self._parse_date(row.get("saleDate"))
            if d:
                daily[d] += float(row.get("totalPrice") or 0)

        self.daily_totals = dict(daily)

        today_rows = [
            row for row in self.history
            if self._parse_date(row.get("saleDate")) == today
        ]

        total_today = sum(float(x.get("totalPrice") or 0) for x in today_rows)
        all_sales = sum(float(x.get("totalPrice") or 0) for x in self.history)

        self.summary.setText(
            f"Today: {len(today_rows)} sale rows    |    "
            f"Today sales: ₹{total_today:.2f}    |    "
            f"All history sales: ₹{all_sales:.2f}"
        )

        self.table.setRowCount(0)
        for i, row in enumerate(today_rows, start=1):
            self.table.insertRow(i - 1)
            worker_id = row.get("workerId")
            product_id = row.get("productId")

            worker_name = (
                row.get("workerName")
                or row.get("worker_name")
                or self.worker_names.get(str(worker_id))
                or "-"
            )

            product_name = (
                row.get("productName")
                or row.get("product_name")
                or self.product_names.get(str(product_id))
                or "-"
            )

            values = [
                i,
                worker_name,
                product_name,
                row.get("quantity", 0),
                f"{float(row.get('unitPrice') or 0):.2f}",
                f"{float(row.get('discount') or 0):.2f}",
                f"{float(row.get('totalPrice') or 0):.2f}",
            ]
            for col, value in enumerate(values):
                self.table.setItem(i - 1, col, QTableWidgetItem(str(value)))

        month_values = []
        for offset in range(29, -1, -1):
            d = today - timedelta(days=offset)
            month_values.append((d.isoformat(), daily.get(d, 0.0)))

        # ---------------------------------------------------------
        # WEEKLY SALES — LAST 4 COMPLETED/ACTIVE WEEKS
        #
        # Each bar represents one 7-day week, not one day.
        #
        # Week 4 = current week
        # Week 3 = previous week
        # Week 2 = two weeks ago
        # Week 1 = three weeks ago
        #
        # When a new week starts, the bars automatically shift:
        # old Week 4 -> Week 3
        # old Week 3 -> Week 2
        # old Week 2 -> Week 1
        # new current week -> Week 4
        # ---------------------------------------------------------
        week_values = []

        # Monday is the beginning of the business week.
        current_week_start = today - timedelta(days=today.weekday())

        for weeks_ago in range(3, -1, -1):
            week_start = current_week_start - timedelta(days=weeks_ago * 7)
            week_end = week_start + timedelta(days=6)

            week_total = 0.0

            for day_offset in range(7):
                d = week_start + timedelta(days=day_offset)
                week_total += daily.get(d, 0.0)

            # Example label:
            # "Sep 08-14"
            label = (
                f"{week_start.strftime('%b %d')}-"
                f"{week_end.strftime('%d')}"
            )

            week_values.append((label, week_total))

        self.month_chart.set_data(month_values)
        self.week_chart.set_data(week_values)
