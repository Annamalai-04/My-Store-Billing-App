from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QToolTip
)

import pyqtgraph as pg


class MonthlyChart(QFrame):

    def __init__(self):
        super().__init__()

        self.setObjectName(
            "monthlyChartPanel"
        )

        self.values = []

        self.create_ui()

    # =====================================================
    # UI
    # =====================================================

    def create_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            10,
            8,
            10,
            8
        )

        layout.setSpacing(5)

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        title = QLabel(
            "monthly chart"
        )

        title.setObjectName(
            "chartTitle"
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            title
        )

        # -------------------------------------------------
        # CHART
        # -------------------------------------------------

        self.chart = pg.PlotWidget()

        self.chart.setBackground(
            "white"
        )

        self.chart.showGrid(
            x=True,
            y=True,
            alpha=0.2
        )

        self.chart.setLabel(
            "left",
            "nos range"
        )

        self.chart.setLabel(
            "bottom",
            "months"
        )

        layout.addWidget(
            self.chart
        )

        # -------------------------------------------------
        # YEAR
        # -------------------------------------------------

        bottom_layout = QHBoxLayout()

        bottom_layout.addStretch()

        self.year_combo = QComboBox()

        self.year_combo.addItems([
            "2026",
            "2025",
            "2024"
        ])

        bottom_layout.addWidget(
            self.year_combo
        )

        layout.addLayout(
            bottom_layout
        )

        # -------------------------------------------------
        # MOUSE HOVER
        # -------------------------------------------------

        self.chart.scene().sigMouseMoved.connect(
            self.mouse_moved
        )

        # -------------------------------------------------
        # TEST DATA
        # -------------------------------------------------

        self.set_data([
            120,
            180,
            150,
            210,
            260,
            180,
            200,
            280,
            220,
            190,
            240,
            300
        ])

    # =====================================================
    # DATA
    # =====================================================

    def set_data(self, values):

        self.values = values

        self.chart.clear()

        x_values = list(
            range(
                1,
                len(values) + 1
            )
        )

        # -------------------------------------------------
        # LINE
        # -------------------------------------------------

        self.chart.plot(
            x_values,
            values,
            pen=pg.mkPen(
                width=2
            )
        )

        # -------------------------------------------------
        # DOTS
        # -------------------------------------------------

        self.scatter = pg.ScatterPlotItem(
            x=x_values,
            y=values,
            size=9,
            brush=pg.mkBrush(
                50,
                70,
                150
            ),
            pen=pg.mkPen(
                50,
                70,
                150
            )
        )

        self.chart.addItem(
            self.scatter
        )

    # =====================================================
    # HOVER
    # =====================================================

    def mouse_moved(self, scene_pos):

        if not self.values:
            return

        # Convert mouse position from scene coordinates
        # to chart/data coordinates.

        mouse_point = (
            self.chart.plotItem.vb.mapSceneToView(
                scene_pos
            )
        )

        mouse_x = mouse_point.x()
        mouse_y = mouse_point.y()

        # Find nearest month.

        nearest_index = round(
            mouse_x
        ) - 1

        if (
            nearest_index < 0
            or nearest_index >= len(self.values)
        ):
            QToolTip.hideText()
            return

        data_x = nearest_index + 1
        data_y = self.values[
            nearest_index
        ]

        # Convert the actual data point to
        # screen coordinates.

        point_scene = (
            self.chart.plotItem.vb.mapViewToScene(
                pg.Point(
                    data_x,
                    data_y
                )
            )
        )

        # Calculate distance from mouse to dot.

        dx = (
            scene_pos.x()
            - point_scene.x()
        )

        dy = (
            scene_pos.y()
            - point_scene.y()
        )

        distance = (
            dx * dx
            + dy * dy
        ) ** 0.5

        # Only show tooltip when mouse is
        # reasonably close to the dot.

        if distance <= 12:

            local_pos = self.chart.mapFromScene(
                point_scene
            )

            global_pos = self.chart.mapToGlobal(
                local_pos
            )

            QToolTip.showText(
                global_pos,
                f"Sales: {data_y}"
            )

        else:

            QToolTip.hideText()