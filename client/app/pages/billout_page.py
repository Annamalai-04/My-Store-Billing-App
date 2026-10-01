from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QMessageBox,
)
from app.components.bill_product_entry import BillProductEntry
from app.components.bill_product_table import BillProductTable
from app.models.product import Product
from app.services.product_service import ProductService
from app.services.billing_service import BillingService
from app.services.customer_service import CustomerService
from app.services.scan_service import BarcodeScanner
from app.utils.storage import get_worker
from app.utils.style_loader import load_style


class BillOutPage(QWidget):
    def __init__(self):
        super().__init__()
        load_style(self, "app/styles/billout_page.qss")
        self.ps = ProductService()
        self.bs = BillingService()
        self.cs = CustomerService()
        self.scanner = BarcodeScanner()
        self.create_ui()

    def create_ui(self):
        main = QVBoxLayout(self)
        content = QHBoxLayout()
        left = QVBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setObjectName("searchBox")
        self.search_box.setPlaceholderText("Search product by name")
        left.addWidget(self.search_box)
        self.entry = BillProductEntry(self.add_product, self.scan_product)
        left.addWidget(self.entry)
        self.product_table = BillProductTable()
        left.addWidget(self.product_table)
        content.addLayout(left, 7)
        self.create_right_panel(content)
        main.addLayout(content)
        self.search_box.textChanged.connect(self.search_products)

    def create_right_panel(self, parent):
        f = QFrame()
        f.setObjectName("rightPanel")
        l = QVBoxLayout(f)

        r = QHBoxLayout()
        r.addWidget(QLabel("Name"))
        self.customer_name_input = QLineEdit()
        self.customer_name_input.setPlaceholderText("Customer name")
        r.addWidget(self.customer_name_input)
        l.addLayout(r)

        r = QHBoxLayout()
        r.addWidget(QLabel("Phone"))
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Customer phone")
        r.addWidget(self.phone_input)
        l.addLayout(r)

        r = QHBoxLayout()
        r.addWidget(QLabel("Total"))
        self.customer_total = QLineEdit("0.00")
        self.customer_total.setReadOnly(True)
        r.addWidget(self.customer_total)
        l.addLayout(r)

        self.checkout_button = QPushButton("Checkout")
        self.checkout_button.clicked.connect(self.checkout)
        l.addWidget(self.checkout_button)

        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_selected)
        l.addWidget(self.remove_button)

        l.addStretch()
        parent.addWidget(f)

    def search_products(self, text):
        if not text.strip():
            return

        try:
            rows = self.ps.get_products(text)

            if len(rows) == 1:
                product = Product.from_dict(rows[0])

                if product.stock <= 0:
                    self.entry.clear()
                    self.entry.name_input.setText(product.name)
                    self.entry.set_stock(0)
                    self.entry.add_button.setEnabled(False)
                    QMessageBox.warning(
                        self,
                        "Stock",
                        f"Product stock over: {product.name}\nAvailable stock: 0",
                    )
                    return

                self.entry.add_button.setEnabled(True)
                self.fill(product)

        except Exception:
            pass

    def fill(self, p):
            self.entry.name_input.setText(p.name)
            self.entry.group_input.setText(p.group_name)
            self.entry.price_input.setText(f"{p.price:.2f}")
            self.entry.discount_input.setText(f"{p.discount:.2f}")
            self.entry.quantity_input.setText("1")
            self.entry.name_input.setProperty("product_id", p.product_id)
            self.entry.set_stock(p.stock)

            if p.stock <= 0:
                QMessageBox.warning(
                    self,
                    "Stock",
                    f"Product stock over: {p.name}\nAvailable stock: 0",
                )
                self.entry.add_button.setEnabled(False)
            else:
                self.entry.add_button.setEnabled(True)

            self.update_entry_total()

    def update_entry_total(self):
        """Calculate the current BillOut entry total."""
        try:
            quantity = float(self.entry.quantity_input.text() or 0)
            price = float(self.entry.price_input.text() or 0)
            discount = float(self.entry.discount_input.text() or 0)

            total = max((quantity * price) - discount, 0)

            self.entry.total_input.setText(f"{total:.2f}")

        except ValueError:
            self.entry.total_input.setText("0.00")

    def add_product(self):
        pid = self.entry.name_input.property("product_id")

        if pid is None:
            QMessageBox.warning(
                self,
                "Product",
                "Search/select a database product first.",
            )
            return

        try:
            q = int(self.entry.quantity_input.text())
            price = float(self.entry.price_input.text())
            discount = float(self.entry.discount_input.text() or 0)
        except ValueError:
            QMessageBox.warning(
                self,
                "Product",
                "Invalid quantity/price/discount.",
            )
            return

        if q <= 0:
            QMessageBox.warning(
                self,
                "Product",
                "Quantity must be greater than 0.",
            )
            return

        stock = self.entry.stock()

        if stock <= 0:
            QMessageBox.warning(
                self,
                "Stock",
                f"Product stock over: {self.entry.name_input.text()}",
            )
            return

        if q > stock:
            QMessageBox.warning(
                self,
                "Stock",
                f"Insufficient stock for {self.entry.name_input.text()}."
                f"\nAvailable stock: {stock}"
                f"\nRequested quantity: {q}",
            )
            return

        total = max((q * price) - discount, 0)
        self.entry.total_input.setText(f"{total:.2f}")

        self.product_table.add_product(
            pid,
            self.entry.name_input.text(),
            self.entry.group_input.text(),
            q,
            price,
            discount,
            self.remove_row,
            self.update_row,
            stock=stock,
        )

        self.update_total()
        self.entry.clear()

    def clear_entry(self):
        """Clear only the current product-entry fields."""
        self.entry.clear()

    def scan_product(self):
            try:
                barcode = self.scanner.scan_from_phone()
            except Exception as e:
                QMessageBox.critical(self, "Scanner", str(e))
                return
            if not barcode:
                return
            try:
                r = self.ps.scan_barcode(barcode)
            except Exception as e:
                QMessageBox.critical(self, "Scan", f"Spring Boot request failed:\n{e}")
                return
            if not r.get("found"):
                QMessageBox.information(
                    self, "Scan", r.get("message", "Product not found.")
                )
                return
            self.entry.name_input.setText(r.get("name") or "")
            self.entry.group_input.setText(r.get("groupName") or "Other")
            self.entry.quantity_input.setText("1")
            # Product found in our MySQL database.
            # Spring Boot currently returns source="MYSTOREAPP".
            # Accept both names so the frontend also works with older backend code.
            source = str(r.get("source") or "").upper()

            if source in ("MYSTOREAPP", "LOCAL_DB"):
                self.entry.price_input.setText(
                    f"{float(r.get('price') or 0):.2f}"
                )

                self.entry.discount_input.setText(
                    f"{float(r.get('discount') or 0):.2f}"
                )

                self.entry.name_input.setProperty(
                    "product_id",
                    r.get("productId")
                )

                stock = int(r.get("stock") or 0)
                self.entry.set_stock(stock)

                if stock <= 0:
                    self.entry.add_button.setEnabled(False)
                    self.entry.total_input.setText("0.00")
                    QMessageBox.warning(
                        self,
                        "Stock",
                        f"Product stock over: {r.get('name') or 'Product'}"
                        f"\nAvailable stock: 0",
                    )
                    return

                self.entry.add_button.setEnabled(True)
                self.update_entry_total()

            else:
                self.entry.price_input.clear()
                self.entry.discount_input.setText("0")
                self.entry.total_input.setText("0.00")
                self.entry.name_input.setProperty("product_id", None)

                QMessageBox.information(
                    self,
                    "External product",
                    "Basic product data found. Add it to ProductIn with your store price/stock/expiry before billing.",
                )

    def update_row(self, w):
        row = self.product_table.row_for_widget(w)
        if row < 0:
            return
        self.entry.name_input.setText(self.product_table.item(row, 1).text())
        self.entry.group_input.setText(self.product_table.item(row, 2).text())
        self.entry.quantity_input.setText(self.product_table.item(row, 3).text())
        self.entry.price_input.setText(self.product_table.item(row, 4).text())
        self.entry.discount_input.setText(self.product_table.item(row, 5).text())
        self.entry.name_input.setProperty(
            "product_id", self.product_table.product_id_at(row)
        )
        self.entry.set_stock(self.product_table.stock_at(row))
        self.entry.add_button.setEnabled(self.entry.stock() > 0)
        self.update_entry_total()
        self.product_table.removeRow(row)
        self.product_table.renumber()
        self.update_total()

    def remove_row(self, w):
        self.product_table.remove_widget_row(w)
        self.update_total()

    def remove_selected(self):
        selected_rows = {
            i.row()
            for i in self.product_table.selectedIndexes()
        }

        if selected_rows:
            # A bill row is selected: remove it from the bill.
            for row in sorted(selected_rows, reverse=True):
                self.product_table.removeRow(row)

            self.product_table.renumber()
            self.update_total()
            return

        # No bill row is selected: remove/clear the product currently
        # typed or loaded in the entry area.
        self.entry.clear()

        # Clear the search text too, so the product is not immediately
        # loaded again by the search signal.
        self.search_box.blockSignals(True)
        self.search_box.clear()
        self.search_box.blockSignals(False)

        self.entry.add_button.setEnabled(True)
        self.update_entry_total()

    def update_total(self):
        self.customer_total.setText(f"{self.product_table.total():.2f}")

    def checkout(self):
        w = get_worker()
        if not w:
            QMessageBox.warning(self, "Login", "Please sign in before checkout.")
            return

        if self.product_table.rowCount() == 0:
            QMessageBox.warning(self, "Checkout", "Add at least one product.")
            return

        customer_name = self.customer_name_input.text().strip()
        customer_phone = self.phone_input.text().strip()

        if not customer_name:
            QMessageBox.warning(
                self, "Customer", "Please enter the customer name."
            )
            return

        if not customer_phone:
            QMessageBox.warning(
                self, "Customer", "Please enter the customer phone."
            )
            return

        try:
            # Create/find the customer using the values entered in
            # the Customer panel.
            c = self.cs.find_or_create(
                customer_name,
                customer_phone
            )

            # Normal backend response is customerId. "id" is accepted
            # too, so None is never sent to the checkout API.
            customer_id = c.get("customerId") or c.get("id")

            if customer_id is None:
                raise RuntimeError(
                    f"Customer API did not return customerId. Response: {c}"
                )

            items = self.product_table.items_for_checkout()

            r = self.bs.checkout(
                customer_id,
                w.get("workerId"),
                customer_phone,
                items,
            )

            QMessageBox.information(
                self,
                "Checkout",
                f"Bill completed.\nBill ID: {r.get('billId')}"
            )

            self.product_table.setRowCount(0)
            self.update_total()

            # Prepare the panel for the next customer.
            self.customer_name_input.clear()
            self.phone_input.clear()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Checkout",
                f"Checkout failed:\n{e}"
            )
