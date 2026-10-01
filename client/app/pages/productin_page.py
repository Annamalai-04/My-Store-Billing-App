from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QInputDialog

from app.components.product_form import ProductForm
from app.components.product_modify import ProductModify
from app.components.product_table import ProductTable
from app.services.product_service import ProductService
from app.models.product import Product
from app.utils.style_loader import load_style


class ProductInPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("productinPage")
        load_style(self, "app/styles/productin_page.qss")

        self.service = ProductService()

        self.create_ui()
        self.load_products()

    def create_ui(self):
        main = QVBoxLayout(self)

        top = QHBoxLayout()

        self.form = ProductForm(
            self.add_product,
            self.clear_new_fields
        )
        top.addWidget(self.form)

        self.modify = ProductModify(
            self.update_product,
            self.delete_product,
            self.add_stock
        )

        # Search in the MODIFY panel.
        self.modify.modify_search.textChanged.connect(
            self.search_modify_product
        )

        top.addWidget(self.modify)

        main.addLayout(top)

        self.product_table = ProductTable()

        # Normal table search.
        self.product_table.table_search.textChanged.connect(
            self.search_products
        )

        self.product_table.view_all_button.clicked.connect(
            self.load_products
        )

        # Double-click a product row -> populate MODIFY panel.
        self.product_table.table.cellDoubleClicked.connect(
            self.on_product_double_clicked
        )

        main.addWidget(self.product_table)

    # ---------------------------------------------------------
    # TABLE
    # ---------------------------------------------------------

    def show_products(self, raw):
        self.product_table.clear()

        for d in raw:
            p = Product.from_dict(d)

            self.product_table.add_product(
                p.name,
                p.group_name,
                p.stock,
                f"{p.price:.2f}",
                f"{p.discount:.2f}",
                p.expiry_date or "",
                p.updated_at or p.created_at or "",
                product_data=d,
            )

    def load_products(self):
        try:
            self.show_products(
                self.service.get_products()
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Server",
                str(e)
            )

    def search_products(self, text):
        text = text.strip()

        if not text:
            self.load_products()
            return

        try:
            self.show_products(
                self.service.get_products(text)
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Search",
                str(e)
            )

    # ---------------------------------------------------------
    # MODIFY SEARCH
    # ---------------------------------------------------------

    def search_modify_product(self, text):
        """
        Search from the MODIFY search box.

        Examples:
            think_book
            9780143452133
            product name
            barcode

        When one matching product is found, all Modify fields
        are populated automatically.
        """

        text = text.strip()

        if not text:
            return

        try:
            products = self.service.get_products(text)

            if not products:
                return

            selected = None

            # Prefer an exact name match.
            for product in products:
                name = str(product.get("name") or "").strip()
                if name.lower() == text.lower():
                    selected = product
                    break

            # Otherwise prefer an exact barcode match.
            if selected is None:
                for product in products:
                    barcode = str(product.get("barcode") or "").strip()
                    if barcode.lower() == text.lower():
                        selected = product
                        break

            # If the search returned only one product, use it.
            if selected is None and len(products) == 1:
                selected = products[0]

            if selected is not None:
                self.populate_modify(selected)

        except Exception:
            # Do not show an error popup for every key pressed.
            # Normal server errors are shown when the user performs
            # the actual update/delete operation.
            return

    def populate_modify(self, d):
        """
        Put one backend product into the MODIFY panel.
        """

        product_id = (
            d.get("productId")
            or d.get("product_id")
            or d.get("id")
        )

        name = d.get("name") or ""
        group_name = (
            d.get("groupName")
            or d.get("group_name")
            or ""
        )
        barcode = d.get("barcode") or ""
        price = d.get("price")
        discount = d.get("discount")
        stock = d.get("stock")
        expiry_date = (
            d.get("expiryDate")
            or d.get("expiry_date")
            or ""
        )
        status = d.get("status") or "ACTIVE"

        # The search box becomes the product ID after a product
        # has been found. Update/Delete therefore operate on the
        # correct database record.
        if product_id is not None:
            self.modify.modify_search.setText(
                str(product_id)
            )

        self.modify.modify_name.setText(str(name))
        self.modify.modify_group.setText(str(group_name))
        self.modify.modify_barcode.setText(str(barcode))
        self.modify.modify_price.setText(
            "" if price is None else str(price)
        )
        self.modify.modify_discount.setText(
            "" if discount is None else str(discount)
        )
        self.modify.modify_stock.setText(
            "" if stock is None else str(stock)
        )
        self.modify.modify_exp_date.setText(
            str(expiry_date)
        )
        self.modify.modify_status.setText(
            str(status)
        )

    def on_product_double_clicked(self, row, column):
        """
        Double-clicking any cell in a product row populates
        the MODIFY panel.
        """

        d = self.product_table.get_product_data(row)

        if d is not None:
            self.populate_modify(d)

    # ---------------------------------------------------------
    # ADD
    # ---------------------------------------------------------

    def add_product(self):
        try:
            p = Product(
        name=self.form.new_name.text().strip(),
        group_name=self.form.new_group.text().strip(),
        barcode=self.form.new_barcode.text().strip(),
        price=float(self.form.new_price.text() or 0),
        discount=float(self.form.new_discount.text() or 0),
        stock=int(self.form.new_stock.text() or 0),
        expiry_date=(
            self.form.new_exp_date.text().strip()
            or None
        ),
    )

            if not p.name or not p.group_name:
                raise ValueError(
                    "Name and group are required"
                )

            self.service.create_product(
                p.to_dict()
            )

            self.form.clear()
            self.load_products()

        except Exception as e:
            QMessageBox.warning(
                self,
                "Product",
                str(e)
            )

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------

    def update_product(self):
        try:
            pid_text = self.modify.modify_search.text().strip()

            if not pid_text:
                raise ValueError(
                    "Search or select a product first."
                )

            try:
                pid = int(pid_text)
            except ValueError:
                raise ValueError(
                    "Please search a product name/barcode "
                    "or double-click a product row first."
                )

            # Send the complete Modify data to the backend.
            # This includes barcode as well.
            data = {
                "name": self.modify.modify_name.text().strip(),
                "groupName": self.modify.modify_group.text().strip(),
                "barcode": self.modify.modify_barcode.text().strip(),
                "price": float(
                    self.modify.modify_price.text() or 0
                ),
                "discount": float(
                    self.modify.modify_discount.text() or 0
                ),
                "stock": int(
                    self.modify.modify_stock.text() or 0
                ),
                "expiryDate": (
                    self.modify.modify_exp_date.text().strip()
                    or None
                ),
                "status": (
                    self.modify.modify_status.text().strip()
                    or "ACTIVE"
                ),
            }

            if not data["name"] or not data["groupName"]:
                raise ValueError(
                    "Name and group are required"
                )

            self.service.update_product(
                pid,
                data
            )

            self.load_products()

        except Exception as e:
            QMessageBox.warning(
                self,
                "Update",
                str(e)
            )

    # ---------------------------------------------------------
    # ADD STOCK
    # ---------------------------------------------------------

    def add_stock(self):
        try:
            pid_text = self.modify.modify_search.text().strip()

            if not pid_text:
                raise ValueError("Search or select a product first.")

            try:
                pid = int(pid_text)
            except ValueError:
                raise ValueError(
                    "Please search a product name/barcode or "
                    "double-click a product row first."
                )

            current_stock = int(
                self.modify.modify_stock.text().strip() or 0
            )

            add_quantity, ok = QInputDialog.getInt(
                self,
                "Add Stock",
                f"Current stock: {current_stock}\n\nEnter quantity to add:",
                1,
                1,
                1000000,
                1,
            )

            if not ok:
                return

            result = self.service.add_stock(pid, add_quantity)

            new_stock = (
                result.get("stock")
                if isinstance(result, dict)
                else None
            )

            if new_stock is None:
                QMessageBox.information(
                    self,
                    "Stock",
                    f"Stock added successfully. Added: {add_quantity}",
                )
            else:
                QMessageBox.information(
                    self,
                    "Stock",
                    f"Stock added successfully.\nNew stock: {new_stock}",
                )

            self.load_products()

        except Exception as e:
            QMessageBox.warning(
                self,
                "Add Stock",
                str(e)
            )

    # ---------------------------------------------------------
    # DELETE
    # ---------------------------------------------------------

    def delete_product(self):
        try:
            pid_text = self.modify.modify_search.text().strip()

            if not pid_text:
                raise ValueError(
                    "Search or select a product first."
                )

            self.service.delete_product(
                int(pid_text)
            )

            self.modify.clear()
            self.load_products()

        except Exception as e:
            QMessageBox.warning(
                self,
                "Delete",
                str(e)
            )

    # ---------------------------------------------------------
    # CLEAR
    # ---------------------------------------------------------

    def clear_new_fields(self):
        self.form.clear()
