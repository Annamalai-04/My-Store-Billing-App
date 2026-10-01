from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDateEdit,
    QToolTip
)

from PySide6.QtCore import QDate

import pyqtgraph as pg


class WorkerHourlyChart(QFrame):

    def __init__(self):

        super().__init__()

        self.values = []

        self.setObjectName(
            "workerHourlyPanel"
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
            "product count"
        )

        self.chart.setLabel(
            "bottom",
            "8 hrs"
        )

        layout.addWidget(
            self.chart
        )

        # -------------------------------------------------
        # BOTTOM
        # -------------------------------------------------

        bottom = QHBoxLayout()

        title = QLabel(
            "worker hourly chart"
        )

        bottom.addWidget(
            title
        )

        bottom.addStretch()

        self.date_edit = QDateEdit()

        self.date_edit.setDate(
            QDate.currentDate()
        )

        self.date_edit.setCalendarPopup(
            True
        )

        bottom.addWidget(
            self.date_edit
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
            10,
            12,
            11,
            8,
            6,
            5,
            7,
            12
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
                1,
                len(values) + 1
            )
        )

        self.chart.plot(
            x_values,
            values,
            pen=pg.mkPen(
                width=2
            )
        )

        self.scatter = pg.ScatterPlotItem(
            x=x_values,
            y=values,
            size=8,
            brush=pg.mkBrush(
                50,
                70,
                150
            )
        )

        self.chart.addItem(
            self.scatter
        )

        self.chart.setXRange(
            0,
            len(values) + 1
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

        mouse_point = (
            self.chart.plotItem.vb.mapSceneToView(
                scene_pos
            )
        )

        index = round(
            mouse_point.x()
        ) - 1

        if (
            index < 0
            or index >= len(self.values)
        ):
            QToolTip.hideText()
            return

        value = self.values[index]

        data_x = index + 1

        scene_point = (
            self.chart.plotItem.vb.mapViewToScene(
                pg.Point(
                    data_x,
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
            f"Products: {value}"
        )