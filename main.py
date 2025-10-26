# main.py
# برنامه ویندوزی آفلاین بانک سوال با PyQt5
# تمام امکانات: ورود، دسته‌بندی، جستجو، حذف، ویرایش، جدول، پرینت PDF

import sys
import csv
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QLineEdit,
                             QLabel, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QMessageBox, QComboBox, QFileDialog, QInputDialog)
from PyQt5.QtCore import Qt
from fpdf import FPDF

DATABASE_FILE = "database.csv"
CATEGORY_FILE = "categories.csv"

class BankSoalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BankSoal App")
        self.setGeometry(100, 100, 900, 600)
        self.categories = []
        self.load_categories()
        self.initUI()
        self.load_data()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # فرم ورود سوال
        form_layout = QHBoxLayout()
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("متن سوال")
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("پاسخ صحیح")
        self.option1_input = QLineEdit()
        self.option1_input.setPlaceholderText("گزینه ۱")
        self.option2_input = QLineEdit()
        self.option2_input.setPlaceholderText("گزینه ۲")
        self.option3_input = QLineEdit()
        self.option3_input.setPlaceholderText("گزینه ۳")
        self.category_combo = QComboBox()
        self.category_combo.addItems(self.categories)
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("منبع / کتاب")

        form_layout.addWidget(self.question_input)
        form_layout.addWidget(self.answer_input)
        form_layout.addWidget(self.option1_input)
        form_layout.addWidget(self.option2_input)
        form_layout.addWidget(self.option3_input)
        form_layout.addWidget(self.category_combo)
        form_layout.addWidget(self.source_input)

        layout.addLayout(form_layout)

        # دکمه‌ها
        button_layout = QHBoxLayout()
        add_btn = QPushButton("افزودن سوال")
        add_btn.clicked.connect(self.add_question)
        edit_btn = QPushButton("ویرایش سوال انتخابی")
        edit_btn.clicked.connect(self.edit_question)
        delete_btn = QPushButton("حذف سوال انتخابی")
        delete_btn.clicked.connect(self.delete_question)
        search_btn = QPushButton("جستجو")
        search_btn.clicked.connect(self.search_questions)
        print_btn = QPushButton("پرینت PDF")
        print_btn.clicked.connect(self.print_pdf)
        manage_cat_btn = QPushButton("مدیریت دسته‌بندی")
        manage_cat_btn.clicked.connect(self.manage_categories)

        button_layout.addWidget(add_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(search_btn)
        button_layout.addWidget(print_btn)
        button_layout.addWidget(manage_cat_btn)

        layout.addLayout(button_layout)

        # جدول نمایش سوال‌ها
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["سوال", "پاسخ صحیح", "گزینه ۱", "گزینه ۲", "گزینه ۳", "دسته‌بندی", "منبع"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        central_widget.setLayout(layout)

    # مدیریت دسته‌بندی
    def load_categories(self):
        if os.path.exists(CATEGORY_FILE):
            with open(CATEGORY_FILE, newline='', encoding='utf-8') as f:
                self.categories = [row[0] for row in csv.reader(f)]
        else:
            self.categories = ["عمومی"]
            self.save_categories()

    def save_categories(self):
        with open(CATEGORY_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for cat in self.categories:
                writer.writerow([cat])

    def manage_categories(self):
        text, ok = QInputDialog.getText(self, "مدیریت دسته‌بندی", "دسته‌بندی جدید:")
        if ok and text:
            if text not in self.categories:
                self.categories.append(text)
                self.save_categories()
                self.category_combo.addItem(text)
                QMessageBox.information(self, "موفق", "دسته‌بندی اضافه شد.")
            else:
                QMessageBox.warning(self, "خطا", "این دسته‌بندی قبلاً وجود دارد.")

    # بارگذاری و ذخیره داده‌ها
    def load_data(self):
        self.table.setRowCount(0)
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row_data in reader:
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    for col, item in enumerate(row_data):
                        self.table.setItem(row, col, QTableWidgetItem(item))

    def save_data(self):
        with open(DATABASE_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    row_data.append(self.table.item(row, col).text())
                writer.writerow(row_data)

    # افزودن سوال
    def add_question(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(self.question_input.text()))
        self.table.setItem(row, 1, QTableWidgetItem(self.answer_input.text()))
        self.table.setItem(row, 2, QTableWidgetItem(self.option1_input.text()))
        self.table.setItem(row, 3, QTableWidgetItem(self.option2_input.text()))
        self.table.setItem(row, 4, QTableWidgetItem(self.option3_input.text()))
        self.table.setItem(row, 5, QTableWidgetItem(self.category_combo.currentText()))
        self.table.setItem(row, 6, QTableWidgetItem(self.source_input.text()))
        self.save_data()
        QMessageBox.information(self, "موفق", "سوال اضافه شد.")
        self.clear_inputs()

    # ویرایش سوال
    def edit_question(self):
        selected = self.table.currentRow()
        if selected >= 0:
            self.table.setItem(selected, 0, QTableWidgetItem(self.question_input.text()))
            self.table.setItem(selected, 1, QTableWidgetItem(self.answer_input.text()))
            self.table.setItem(selected, 2, QTableWidgetItem(self.option1_input.text()))
            self.table.setItem(selected, 3, QTableWidgetItem(self.option2_input.text()))
            self.table.setItem(selected, 4, QTableWidgetItem(self.option3_input.text()))
            self.table.setItem(selected, 5, QTableWidgetItem(self.category_combo.currentText()))
            self.table.setItem(selected, 6, QTableWidgetItem(self.source_input.text()))
            self.save_data()
            QMessageBox.information(self, "موفق", "سوال ویرایش شد.")
            self.clear_inputs()
        else:
            QMessageBox.warning(self, "خطا", "ابتدا یک سوال را انتخاب کنید.")

    # حذف سوال
    def delete_question(self):
        selected = self.table.currentRow()
        if selected >= 0:
            confirm = QMessageBox.question(self, "تایید حذف", "آیا مطمئن هستید؟", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.table.removeRow(selected)
                self.save_data()
        else:
            QMessageBox.warning(self, "خطا", "ابتدا یک سوال را انتخاب کنید.")

    # جستجو
    def search_questions(self):
        text, ok = QInputDialog.getText(self, "جستجو", "متن یا دسته‌بندی یا منبع:")
        if ok and text:
            for row in range(self.table.rowCount()):
                match = False
                for col in [0,5,6]:
                    if text in self.table.item(row, col).text():
                        match = True
                        break
                self.table.setRowHidden(row, not match)

    # پرینت PDF
    def print_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "ذخیره PDF", "", "PDF Files (*.pdf)")
        if path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for row in range(self.table.rowCount()):
                row_text = ""
                for col in range(self.table.columnCount()):
                    row_text += f"{self.table.horizontalHeaderItem(col).text()}: {self.table.item(row,col).text()}  |  "
                pdf.multi_cell(0, 8, row_text)
                pdf.ln()
            pdf.output(path)
            QMessageBox.information(self, "موفق", "PDF ذخیره شد.")

    # پاک کردن فیلدها
    def clear_inputs(self):
        self.question_input.clear()
        self.answer_input.clear()
        self.option1_input.clear()
        self.option2_input.clear()
        self.option3_input.clear()
        self.source_input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BankSoalApp()
    window.show()
    sys.exit(app.exec_())
