# Import Modules
import sys
import csv
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout,
    QComboBox, QLineEdit, QDateEdit, QTableWidget, QMessageBox, QHeaderView, QTableWidgetItem
)
from PyQt5.QtSql import QSqlDatabase, QSqlQuery


# App Class
class ExpenseTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        # Main App Object & Settings
        self.setWindowTitle("Expense Tracking Application")
        self.resize(1000, 800)

        # UI Elements
        self.date_box = QDateEdit()
        self.date_box.setDate(QDate.currentDate())
        self.dropdown_box = QComboBox()
        self.amount = QLineEdit()
        self.amount.setValidator(QDoubleValidator(0.0, 1000000.0, 2))  # Accept decimals up to 2 decimal places
        self.description = QLineEdit()

        # Buttons (increased size and bold text)
        self.add_button = QPushButton("Add Expense")
        self.add_button.setStyleSheet("background-color: lightgreen; color: black; font-weight: bold; font-size: 20px; padding: 15px;")
        self.add_button.clicked.connect(self.add_expense)

        self.delete_button = QPushButton("Delete Expense")
        self.delete_button.setStyleSheet("background-color: red; color: white; font-weight: bold; font-size: 20px; padding: 15px;")
        self.delete_button.clicked.connect(self.delete_expense)

        self.export_button = QPushButton("Export to CSV")
        self.export_button.setStyleSheet("background-color: orange; color: white; font-weight: bold; font-size: 20px; padding: 15px;")
        self.export_button.clicked.connect(self.export_to_csv)

        self.dark_mode_button = QPushButton("Toggle Dark Mode")
        self.dark_mode_button.setStyleSheet("background-color: gray; color: white; font-weight: bold; font-size: 20px; padding: 15px;")
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by ID, Description, or Category...")
        self.search_bar.setStyleSheet("font-size: 18px; padding: 10px;")
        self.search_bar.textChanged.connect(self.search_expenses)

        self.total_expense_label = QLabel("Total Expenses: $0")
        self.total_expense_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.table = QTableWidget()
        self.table.setColumnCount(5)  # Id, Date, Category, Amount, Description
        self.table.setHorizontalHeaderLabels(["Id", "Date", "Category", "Amount", "Description"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #87CEFA;  /* Light blue for selected rows */
                color: black;
            }
        """)

        # Dropdown Items
        self.dropdown_box.addItems([
            "Food", "Entertainment", "Transportation", "Bills",
            "Rent", "Utilities", "Healthcare", "Education", "Shopping", "Others"
        ])
        self.dropdown_box.setStyleSheet("font-size: 18px; padding: 10px;")

        # Layouts
        self.master_layout = QVBoxLayout()
        self.row1 = QHBoxLayout()
        self.row2 = QHBoxLayout()
        self.row3 = QHBoxLayout()

        # Row 1
        self.row1.addWidget(QLabel("Date:"))
        self.row1.addWidget(self.date_box)
        self.row1.addWidget(QLabel("Category:"))
        self.row1.addWidget(self.dropdown_box)

        # Row 2
        self.row2.addWidget(QLabel("Amount:"))
        self.row2.addWidget(self.amount)
        self.row2.addWidget(QLabel("Description:"))
        self.row2.addWidget(self.description)

        # Row 3
        self.row3.addWidget(self.add_button)
        self.row3.addWidget(self.delete_button)
        self.row3.addWidget(self.export_button)
        self.row3.addWidget(self.dark_mode_button)

        # Master Layout
        self.master_layout.addWidget(self.search_bar)
        self.master_layout.addLayout(self.row1)
        self.master_layout.addLayout(self.row2)
        self.master_layout.addLayout(self.row3)
        self.master_layout.addWidget(self.table)
        self.master_layout.addWidget(self.total_expense_label)
        self.setLayout(self.master_layout)

        # Load Data
        self.load_table()

    def load_table(self):
        self.table.setRowCount(0)
        total_expense = 0

        query = QSqlQuery("SELECT * FROM expenses")
        row = 0
        while query.next():
            expense_id = query.value(0)
            date = query.value(1)
            category = query.value(2)
            amount = query.value(3)
            description = query.value(4)

            total_expense += float(amount)

            # Add values to Table
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(expense_id)))
            self.table.setItem(row, 1, QTableWidgetItem(date))
            self.table.setItem(row, 2, QTableWidgetItem(category))
            self.table.setItem(row, 3, QTableWidgetItem(f"${amount:.2f}"))  # Format to USD
            self.table.setItem(row, 4, QTableWidgetItem(description))
            row += 1

        self.total_expense_label.setText(f"Total Expenses: ${total_expense:.2f}")

    def add_expense(self):
        date = self.date_box.date().toString("yyyy-MM-dd")
        category = self.dropdown_box.currentText()
        amount = self.amount.text()
        description = self.description.text()

        if not amount or not description:
            QMessageBox.warning(self, "Input Error", "Please fill all fields.")
            return

        try:
            amount = float(amount)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Amount must be a valid decimal number.")
            return

        query = QSqlQuery()
        query.prepare("""
            INSERT INTO expenses (date, category, amount, description)
            VALUES (?, ?, ?, ?)
        """)
        query.addBindValue(date)
        query.addBindValue(category)
        query.addBindValue(amount)
        query.addBindValue(description)
        query.exec_()

        self.date_box.setDate(QDate.currentDate())
        self.dropdown_box.setCurrentIndex(0)
        self.amount.clear()
        self.description.clear()

        self.load_table()

    def delete_expense(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "No row selected.")
            return

        expense_id = int(self.table.item(selected_row, 0).text())

        confirm = QMessageBox.question(self, "Are you sure?", "Do you want to delete this expense?", QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.No:
            return

        query = QSqlQuery()
        query.prepare("DELETE FROM expenses WHERE id = ?")
        query.addBindValue(expense_id)
        query.exec_()

        self.load_table()

    def search_expenses(self, text):
        self.table.setRowCount(0)
        query = QSqlQuery(f"""
            SELECT * FROM expenses
            WHERE description LIKE '%{text}%' OR category LIKE '%{text}%' OR id LIKE '%{text}%'
        """)
        row = 0
        while query.next():
            expense_id = query.value(0)
            date = query.value(1)
            category = query.value(2)
            amount = query.value(3)
            description = query.value(4)

            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(expense_id)))
            self.table.setItem(row, 1, QTableWidgetItem(date))
            self.table.setItem(row, 2, QTableWidgetItem(category))
            self.table.setItem(row, 3, QTableWidgetItem(f"${amount:.2f}"))  # Format to USD
            self.table.setItem(row, 4, QTableWidgetItem(description))
            row += 1

    def export_to_csv(self):
        file_name = "expenses.csv"
        with open(file_name, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Id", "Date", "Category", "Amount", "Description"])
            query = QSqlQuery("SELECT * FROM expenses")
            while query.next():
                writer.writerow([
                    query.value(0), query.value(1), query.value(2),
                    query.value(3), query.value(4)
                ])
        QMessageBox.information(self, "Export Successful", f"Data exported to {file_name}")

    def toggle_dark_mode(self):
        if self.styleSheet() == "":
            self.setStyleSheet("""
                QWidget { background-color: #2e2e2e; color: white; font-size: 18px; }
                QLineEdit, QComboBox, QDateEdit { background-color: #444; color: white; }
                QTableWidget { background-color: #444; color: white; }
                QHeaderView::section { background-color: #555; color: white; }
            """)
        else:
            self.setStyleSheet("")


# Create Database
database = QSqlDatabase.addDatabase("QSQLITE")
database.setDatabaseName("expense_tracker.db")
if not database.open():
    QMessageBox.critical(None, "Error", "Could not open your database.")
    sys.exit(1)

query = QSqlQuery()
query.exec_("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        category TEXT,
        amount REAL,
        description TEXT
    )
""")

# Run the App
app = QApplication([])
window = ExpenseTrackerApp()
window.show()
app.exec_()
