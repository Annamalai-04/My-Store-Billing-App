from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import (
    QPainter,
    QPen,
    QBrush,
    QColor,
    QFont
)
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QWidget
)

import math


# =========================================================
# ROTATABLE DONUT CHART
# =========================================================

class DonutChart(QWidget):

    def __init__(
        self,
        percentage=70
    ):

        super().__init__()

        self.percentage = percentage

        # Starting angle of the donut.
        # 90 degrees means the first section starts
        # from the top.
        self.start_angle = 90

        # Dragging state
        self.dragging = False
        self.last_angle = 0

        self.setMinimumSize(
            250,
            200
        )

        self.setMouseTracking(
            True
        )

    # =====================================================
    # PAINT
    # =====================================================

    def paintEvent(
        self,
        event
    ):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        # -------------------------------------------------
        # CENTER
        # -------------------------------------------------

        center = QPointF(
            self.width() / 2,
            self.height() / 2
        )

        # -------------------------------------------------
        # SIZE
        # -------------------------------------------------

        size = min(
            self.width(),
            self.height()
        )

        outer_radius = (
            size * 0.42
        )

        inner_radius = (
            size * 0.25
        )

        outer_rect = (
            center.x() - outer_radius,
            center.y() - outer_radius,
            outer_radius * 2,
            outer_radius * 2
        )

        # -------------------------------------------------
        # ANGLES
        # -------------------------------------------------

        attendance_angle = (
            self.percentage / 100
        ) * 360

        remaining_angle = (
            360 - attendance_angle
        )

        # Qt uses 1/16 degree.

        green_start = (
            self.start_angle * 16
        )

        green_span = (
            -attendance_angle * 16
        )

        remaining_start = (
            (
                self.start_angle
                - attendance_angle
            ) * 16
        )

        remaining_span = (
            -remaining_angle * 16
        )

        # -------------------------------------------------
        # ATTENDANCE SECTION
        # -------------------------------------------------

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.setBrush(
            QBrush(
                QColor(
                    35,
                    180,
                    75
                )
            )
        )

        painter.drawPie(
            *outer_rect,
            int(green_start),
            int(green_span)
        )

        # -------------------------------------------------
        # REMAINING SECTION
        # -------------------------------------------------

        painter.setBrush(
            QBrush(
                QColor(
                    245,
                    235,
                    180
                )
            )
        )

        painter.drawPie(
            *outer_rect,
            int(remaining_start),
            int(remaining_span)
        )

        # -------------------------------------------------
        # INNER HOLE
        # -------------------------------------------------

        inner_rect = (
            center.x() - inner_radius,
            center.y() - inner_radius,
            inner_radius * 2,
            inner_radius * 2
        )

        painter.setBrush(
            QBrush(
                QColor(
                    255,
                    255,
                    255
                )
            )
        )

        painter.setPen(
            QPen(
                QColor(
                    0,
                    0,
                    0
                ),
                3
            )
        )

        painter.drawEllipse(
            *inner_rect
        )

        # -------------------------------------------------
        # CENTER PERCENTAGE
        # -------------------------------------------------

        painter.setPen(
            QColor(
                0,
                0,
                0
            )
        )

        font = QFont()

        font.setPointSize(
            15
        )

        font.setBold(
            False
        )

        painter.setFont(
            font
        )

        percentage_text = (
            f"{self.percentage}%"
        )

        text_rect = painter.boundingRect(
            self.rect(),
            Qt.AlignmentFlag.AlignCenter,
            percentage_text
        )

        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignCenter,
            percentage_text
        )

        # -------------------------------------------------
        # PERCENTAGE LABELS ON DONUT
        # -------------------------------------------------

        self.draw_percentage_label(
            painter,
            center,
            outer_radius,
            self.percentage,
            self.start_angle
            - (
                attendance_angle / 2
            )
        )

        self.draw_percentage_label(
            painter,
            center,
            outer_radius,
            100 - self.percentage,
            self.start_angle
            - attendance_angle
            - (
                remaining_angle / 2
            )
        )

        painter.end()

    # =====================================================
    # DRAW % LABEL
    # =====================================================

    def draw_percentage_label(
        self,
        painter,
        center,
        radius,
        value,
        angle
    ):

        # Position text in the middle of the donut section

        label_radius = radius * 0.78

        radians = math.radians(angle)

        x = (
            center.x()
            + label_radius
            * math.cos(radians)
        )

        y = (
            center.y()
            - label_radius
            * math.sin(radians)
        )

        # Create the text here
        label_text = f"{int(value)}%"

        font = QFont()

        font.setPointSize(11)

        font.setBold(False)

        painter.setFont(font)

        painter.setPen(
            QColor(
                0,
                0,
                0
            )
        )

        text_rect = painter.boundingRect(
            int(x - 30),
            int(y - 15),
            60,
            30,
            Qt.AlignmentFlag.AlignCenter,
            label_text
        )

        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignCenter,
            label_text
        )

    # =====================================================
    # MOUSE PRESS
    # =====================================================

    def mousePressEvent(
        self,
        event
    ):

        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):

            self.dragging = True

            self.last_angle = (
                self.get_mouse_angle(
                    event.position()
                )
            )

            event.accept()

    # =====================================================
    # MOUSE MOVE
    # =====================================================

    def mouseMoveEvent(
        self,
        event
    ):

        if not self.dragging:
            return

        current_angle = (
            self.get_mouse_angle(
                event.position()
            )
        )

        difference = (
            current_angle
            - self.last_angle
        )

        self.start_angle += difference

        # Keep angle within 0-360.

        self.start_angle %= 360

        self.last_angle = (
            current_angle
        )

        self.update()

        event.accept()

    # =====================================================
    # MOUSE RELEASE
    # =====================================================

    def mouseReleaseEvent(
        self,
        event
    ):

        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):

            self.dragging = False

            event.accept()

    # =====================================================
    # GET MOUSE ANGLE
    # =====================================================

    def get_mouse_angle(
        self,
        position
    ):

        center_x = (
            self.width() / 2
        )

        center_y = (
            self.height() / 2
        )

        dx = (
            position.x()
            - center_x
        )

        dy = (
            center_y
            - position.y()
        )

        angle = math.degrees(
            math.atan2(
                dy,
                dx
            )
        )

        return angle


# =========================================================
# PROFILE ATTENDANCE COMPONENT
# =========================================================

class ProfileAttendance(QFrame):

    def __init__(
        self,
        percentage=70
    ):

        super().__init__()

        self.percentage = percentage

        self.setObjectName(
            "attendancePanel"
        )

        self.create_ui()

    # =====================================================
    # UI
    # =====================================================

    def create_ui(
        self
    ):

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            10,
            8,
            10,
            8
        )

        layout.setSpacing(
            3
        )

        # -------------------------------------------------
        # DONUT
        # -------------------------------------------------

        self.donut = DonutChart(
            self.percentage
        )

        layout.addWidget(
            self.donut,
            1
        )

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        title = QLabel(
            "Overall Attendence"
        )

        title.setObjectName(
            "attendanceTitle"
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            title
        )

    # =====================================================
    # UPDATE PERCENTAGE
    # =====================================================

    def set_percentage(
        self,
        percentage
    ):

        # Keep percentage between 0 and 100.

        percentage = max(
            0,
            min(
                100,
                percentage
            )
        )

        self.percentage = percentage

        self.donut.percentage = (
            percentage
        )

        self.donut.update()