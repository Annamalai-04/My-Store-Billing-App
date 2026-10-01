from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem
)


class StockHistoryTable(QFrame):

    search_requested = Signal(str)
    filter_requested = Signal()

    def __init__(self):
        super().__init__()

        self.setObjectName(
            "stockHistoryPanel"
        )

        self.create_ui()

    # =====================================================
    # UI
    # =====================================================

    def create_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            8,
            8,
            8,
            8
        )

        layout.setSpacing(5)

        # -------------------------------------------------
        # TOP
        # -------------------------------------------------

        top_layout = QHBoxLayout()

        title = QLabel(
            "stock his"
        )

        title.setObjectName(
            "historyTitle"
        )

        top_layout.addWidget(
            title
        )

        top_layout.addStretch()

        # Search

        self.search_input = QLineEdit()

        self.search_input.setObjectName(
            "historySearch"
        )

        self.search_input.setPlaceholderText(
            "search"
        )

        self.search_input.textChanged.connect(
            self.search_requested.emit
        )

        top_layout.addWidget(
            self.search_input
        )

        # Filter

        self.filter_button = QPushButton(
            "filter"
        )

        self.filter_button.setObjectName(
            "filterButton"
        )

        self.filter_button.clicked.connect(
            self.filter_requested.emit
        )

        top_layout.addWidget(
            self.filter_button
        )

        layout.addLayout(
            top_layout
        )

        # -------------------------------------------------
        # TABLE
        # -------------------------------------------------

        self.table = QTableWidget()

        self.table.setObjectName(
            "stockHistoryTable"
        )

        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels([
            "no",
            "name",
            "updated date",
            "exp date",
            "stock"
        ])

        self.table.verticalHeader().setVisible(
            False
        )

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            header.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            1,
            header.ResizeMode.Stretch
        )

        header.setSectionResizeMode(
            2,
            header.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            3,
            header.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            4,
            header.ResizeMode.ResizeToContents
        )

        layout.addWidget(
            self.table
        )

    # =====================================================
    # ADD PRODUCT
    # =====================================================

    def add_product(
        self,
        product
    ):

        row = self.table.rowCount()

        self.table.insertRow(row)

        self.table.setItem(
            row,
            0,
            QTableWidgetItem(
                str(row + 1)
            )
        )

        self.table.setItem(
            row,
            1,
            QTableWidgetItem(
                product.name
            )
        )

        self.table.setItem(
            row,
            2,
            QTableWidgetItem(
                product.added_updated_date
            )
        )

        self.table.setItem(
            row,
            3,
            QTableWidgetItem(
                product.exp_date
            )
        )

        self.table.setItem(
            row,
            4,
            QTableWidgetItem(
                str(product.stock)
            )
        )

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(self):

        self.table.setRowCount(0)