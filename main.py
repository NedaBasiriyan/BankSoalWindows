import sys
from PyQt5 import QtWidgets, QtCore
from banksoal_v3 import QuestionBank

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("بانک سوالات مدرسه - نسخه نهایی")
        self.setGeometry(100, 100, 900, 600)

        self.bank = QuestionBank()

        # ---- ویجت‌ها ----
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        # نوار دکمه‌ها
        button_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(button_layout)

        self.btn_add = QtWidgets.QPushButton("افزودن سوال")
        self.btn_save = QtWidgets.QPushButton("ذخیره")
        self.btn_reset = QtWidgets.QPushButton("بازگشت به حالت اولیه")
        self.btn_search = QtWidgets.QPushButton("جستجو")
        self.btn_pdf = QtWidgets.QPushButton("خروجی PDF")
        self.btn_word = QtWidgets.QPushButton("خروجی Word")
        self.btn_random = QtWidgets.QPushButton("انتخاب تصادفی سوالات")

        for b in [self.btn_add, self.btn_save, self.btn_reset, self.btn_search, self.btn_pdf, self.btn_word, self.btn_random]:
            button_layout.addWidget(b)

        # جدول
        self.table = QtWidgets.QTableWidget()
        layout.addWidget(self.table)

        # فیلتر بالای جدول
        filter_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(filter_layout)
        self.filter_label = QtWidgets.QLabel("فیلتر بر اساس:")
        self.filter_input = QtWidgets.QLineEdit()
        self.filter_column = QtWidgets.QComboBox()
        self.filter_column.addItems(["Question", "Answer", "Category", "Source"])
        self.filter_btn = QtWidgets.QPushButton("اعمال فیلتر")
        filter_layout.addWidget(self.filter_label)
        filter_layout.addWidget(self.filter_column)
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(self.filter_btn)

        # بارگذاری داده‌ها
        self.refresh_table()

        # اتصال دکمه‌ها
        self.btn_add.clicked.connect(self.add_question)
        self.btn_save.clicked.connect(self.save)
        self.btn_pdf.clicked.connect(self.export_pdf)
        self.btn_word.clicked.connect(self.export_word)
        self.btn_search.clicked.connect(self.search)
        self.btn_reset.clicked.connect(self.reset_view)
        self.btn_random.clicked.connect(self.select_random)
        self.filter_btn.clicked.connect(self.apply_filter)

    # ---- متدها ----
    def refresh_table(self, data=None):
        if data is None:
            data = self.bank.questions
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(data.columns))
        self.table.setHorizontalHeaderLabels(data.columns)

        for i, row in data.iterrows():
            for j, value in enumerate(row):
                self.table.setItem(i, j, QtWidgets.QTableWidgetItem(str(value)))

        self.table.resizeColumnsToContents()

    def add_question(self):
        row = {col: "" for col in self.bank.questions.columns}
        success, err = self.bank.add_question(row)
        if success:
            self.refresh_table()
        else:
            QtWidgets.QMessageBox.warning(self, "خطا", err)

    def save(self):
        success, err = self.bank.save_questions()
        if success:
            QtWidgets.QMessageBox.information(self, "ذخیره شد", "سوالات با موفقیت ذخیره شدند.")
        else:
            QtWidgets.QMessageBox.warning(self, "خطا در ذخیره", err)

    def export_pdf(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "ذخیره به صورت PDF", "", "PDF Files (*.pdf)")
        if filename:
            success, err = self.bank.export_pdf(filename)
            if success:
                QtWidgets.QMessageBox.information(self, "موفق", "خروجی PDF با موفقیت ایجاد شد.")
            else:
                QtWidgets.QMessageBox.warning(self, "خطا در خروجی", err)

    def export_word(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "ذخیره به صورت Word", "", "Word Files (*.docx)")
        if filename:
            success, err = self.bank.export_word(filename)
            if success:
                QtWidgets.QMessageBox.information(self, "موفق", "فایل Word با موفقیت ایجاد شد.")
            else:
                QtWidgets.QMessageBox.warning(self, "خطا در خروجی", err)

    def search(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "جستجو", "عبارت مورد نظر:")
        if ok and text:
            filtered = self.bank.filter_questions(Question=text)
            self.refresh_table(filtered)

    def reset_view(self):
        self.bank.reset_view()
        self.refresh_table()

    def select_random(self):
        count, ok = QtWidgets.QInputDialog.getInt(self, "انتخاب تصادفی", "تعداد سوالات:", min=1, max=len(self.bank.questions))
        if ok:
            success, err = self.bank.select_questions(mode="random", count=count)
            if success:
                self.refresh_table(self.bank.selected_questions)
                QtWidgets.QMessageBox.information(self, "موفق", f"{count} سوال به صورت تصادفی انتخاب شد.")
            else:
                QtWidgets.QMessageBox.warning(self, "خطا", err)

    def apply_filter(self):
        col = self.filter_column.currentText()
        val = self.filter_input.text()
        filtered = self.bank.filter_questions(**{col: val})
        self.refresh_table(filtered)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
