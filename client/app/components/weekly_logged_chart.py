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


class WeeklyLoggedChart(QFrame):

    def __init__(self):

        super().__init__()

        self.values = []

        self.setObjectName(
            "weeklyLoggedPanel"
        )

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
            "hrs"
        )

        self.chart.setLabel(
            "bottom",
            "7 days"
        )

        layout.addWidget(
            self.chart
        )

        # -------------------------------------------------
        # BOTTOM
        # -------------------------------------------------

        bottom = QHBoxLayout()

        title = QLabel(
            "weekly logged in"
        )

        bottom.addWidget(
            title
        )

        bottom.addStretch()

        self.week_combo = QComboBox()

        self.week_combo.addItems([
            "week 1",
            "week 2",
            "week 3",
            "week 4"
        ])

        bottom.addWidget(
            self.week_combo
        )

        layout.addLayout(
            bottom
        )

        # -------------------------------------------------
        # HOVER
        # -------------------------------------------------

        self.chart.scene().sigMouseMoved.connect(
            self.mouse_moved
        )

        # Sample data

        self.set_data([
            4,
            3,
            5,
            2,
            4,
            3,
            0
        ])

    # =====================================================
    # DATA
    # =====================================================

    def set_data(
        self,
        values
    ):

        self.values = values

        self.chart.clear()

        x_values = list(
            range(
                len(values)
            )
        )

        self.bar_graph = pg.BarGraphItem(
            x=x_values,
            height=values,
            width=0.55
        )

        self.chart.addItem(
            self.bar_graph
        )

        self.chart.setXRange(
            -1,
            len(values)
        )

    # =====================================================
    # HOVER
    # =====================================================

    def mouse_moved(
        self,
        scene_pos
    ):

        if not self.values:
            return

        point = (
            self.chart.plotItem.vb.mapSceneToView(
                scene_pos
            )
        )

        index = round(
            point.x()
        )

        if (
            index < 0
            or index >= len(self.values)
        ):
            QToolTip.hideText()
            return

        value = self.values[index]

        if (
            point.y() < 0
            or point.y() > value
        ):
            QToolTip.hideText()
            return

        scene_point = (
            self.chart.plotItem.vb.mapViewToScene(
                pg.Point(
                    index,
                    value
                )
            )
        )

        local_pos = self.chart.mapFromScene(
            scene_point
        )

        global_pos = self.chart.mapToGlobal(
            local_pos
        )

        QToolTip.showText(
            global_pos,
            f"Logged: {value} hrs"
        )