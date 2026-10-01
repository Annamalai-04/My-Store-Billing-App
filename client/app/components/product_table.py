from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
)


class ProductTable(QFrame):
    HEADERS = [
        "sno",
        "name",
        "group",
        "stock",
        "price",
        "discount",
        "exp date",
        "add/updated date",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("productViewPanel")

        layout = QVBoxLayout(self)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("search"))

        self.table_search = QLineEdit()
        self.table_search.setPlaceholderText("Search product")
        search_layout.addWidget(self.table_search, 1)

        self.view_all_button = QPushButton("viewall")
        search_layout.addWidget(self.view_all_button)

        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.HEADERS))
        self.table.setHorizontalHeaderLabels(self.HEADERS)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        layout.addWidget(self.table)

    def clear(self):
        self.table.setRowCount(0)

    def add_product(
        self,
        name,
        group_name,
        stock,
        price,
        *args,
        product_data=None,
        discount=None,
        expiry_date=None,
        updated_date=None,
    ):
        """
        Add one backend product to the table.

        Supports both old and new callers:

        Old:
            name, group, stock, price, expiry_date, updated_date

        New:
            name, group, stock, price, discount,
            expiry_date, updated_date
        """

        # Support the positional versions used by older ProductInPage files.
        if args:
            if len(args) == 2:
                # Old signature:
                # expiry_date, updated_date
                if expiry_date is None:
                    expiry_date = args[0]
                if updated_date is None:
                    updated_date = args[1]

            elif len(args) == 3:
                # New signature:
                # discount, expiry_date, updated_date
                if discount is None:
                    discount = args[0]
                if expiry_date is None:
                    expiry_date = args[1]
                if updated_date is None:
                    updated_date = args[2]

            else:
                raise TypeError(
                    "add_product() expected either "
                    "2 or 3 values after price."
                )

        row = self.table.rowCount()
        self.table.insertRow(row)

        values = [
            row + 1,
            name,
            group_name,
            stock,
            price,
            "" if discount is None else discount,
            "" if expiry_date is None else expiry_date,
            "" if updated_date is None else updated_date,
        ]

        for column, value in enumerate(values):
            item = QTableWidgetItem(str(value))

            # Keep the complete backend product object hidden in
            # the NAME cell so ProductInPage can populate MODIFY.
            if column == 1 and product_data is not None:
                item.setData(
                    Qt.ItemDataRole.UserRole,
                    product_data
                )

            self.table.setItem(row, column, item)

    def get_product_data(self, row):
        if row < 0 or row >= self.table.rowCount():
            return None

        item = self.table.item(row, 1)

        if item is None:
            return None

        return item.data(Qt.ItemDataRole.UserRole)
