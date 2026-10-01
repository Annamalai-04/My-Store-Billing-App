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


class WeeklyChart(QFrame):

    def __init__(self):
        super().__init__()

        self.setObjectName(
            "weeklyChartPanel"
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
            "weekly chart"
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
            "7 week days"
        )

        layout.addWidget(
            self.chart
        )

        # -------------------------------------------------
        # WEEK SELECTOR
        # -------------------------------------------------

        bottom_layout = QHBoxLayout()

        bottom_layout.addStretch()

        self.week_combo = QComboBox()

        self.week_combo.addItems([
            "week 1",
            "week 2",
            "week 3",
            "week 4"
        ])

        bottom_layout.addWidget(
            self.week_combo
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
            40,
            20,
            70,
            45,
            60,
            48,
            25
        ])

    # =====================================================
    # DATA
    # =====================================================

    def set_data(self, values):

        self.values = values

        self.chart.clear()

        x_values = list(
            range(
                len(values)
            )
        )

        # -------------------------------------------------
        # BAR GRAPH
        # -------------------------------------------------

        self.bar_graph = pg.BarGraphItem(
            x=x_values,
            height=values,
            width=0.6
        )

        self.chart.addItem(
            self.bar_graph
        )

        # -------------------------------------------------
        # RANGE
        # -------------------------------------------------

        self.chart.setXRange(
            -1,
            len(values)
        )

        max_value = max(values)

        self.chart.setYRange(
            0,
            max_value * 1.15
        )

    # =====================================================
    # HOVER
    # =====================================================

    def mouse_moved(self, scene_pos):

        if not self.values:
            return

        # Convert mouse position to chart/data coordinates.

        mouse_point = (
            self.chart.plotItem.vb.mapSceneToView(
                scene_pos
            )
        )

        mouse_x = mouse_point.x()
        mouse_y = mouse_point.y()

        # Determine which bar the mouse is over.

        bar_index = round(
            mouse_x
        )

        if (
            bar_index < 0
            or bar_index >= len(self.values)
        ):
            QToolTip.hideText()
            return

        # Each bar has width 0.6.
        # Therefore the mouse must be inside
        # +/- 0.3 from the bar center.

        bar_center = bar_index

        if abs(
            mouse_x - bar_center
        ) > 0.3:

            QToolTip.hideText()
            return

        bar_height = self.values[
            bar_index
        ]

        # Mouse must be between the bottom
        # and top of the bar.

        if (
            mouse_y < 0
            or mouse_y > bar_height
        ):

            QToolTip.hideText()
            return

        # Show exact value.
        bar_scene = (
            self.chart.plotItem.vb.mapViewToScene(
                pg.Point(
                    bar_center,
                    bar_height
                )
            )
        )

        local_pos = self.chart.mapFromScene(
            bar_scene
        )

        global_pos = self.chart.mapToGlobal(
            local_pos
        )

        QToolTip.showText(
            global_pos,
            f"Sales: {bar_height}"
        )