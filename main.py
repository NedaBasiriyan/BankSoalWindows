import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QLabel, QInputDialog, QMessageBox, QComboBox
)
from banksoal_v3 import QuestionBank

class BankSoalApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("بانک سوالات")
        self.resize(900, 600)

        # کلاس مدیریت بانک سوالات
        self.bank = QuestionBank()
        self.current_data = self.bank.list_questions()

        self.initUI()
        self.load_table(self.current_data)

    def initUI(self):
        layout = QVBoxLayout()

        # بالای صفحه: جست‌وجو و فیلتر
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جست‌وجو...")
        self.search_input.textChanged.connect(self.search_questions)
        filter_layout.addWidget(QLabel("جست‌وجو:"))
        filter_layout.addWidget(self.search_input)

        # فیلتر ستون‌ها
        self.column_filter = QComboBox()
        self.column_filter.addItems(["Question","Answer","Option1","Option2","Option3","Category","Source"])
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("مقدار فیلتر...")
        filter_btn = QPushButton("فیلتر")
        filter_btn.clicked.connect(self.apply_column_filter)
        filter_layout.addWidget(QLabel("فیلتر ستون:"))
        filter_layout.addWidget(self.column_filter)
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(filter_btn)

        layout.addLayout(filter_layout)

        # جدول نمایش سوالات
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # دکمه‌ها
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("افزودن سوال")
        add_btn.clicked.connect(self.add_question)
        edit_btn = QPushButton("ویرایش سوال")
        edit_btn.clicked.connect(self.edit_question)
        delete_btn = QPushButton("حذف سوال")
        delete_btn.clicked.connect(self.delete_question)
        reset_btn = QPushButton("بازگشت به حالت اولیه")
        reset_btn.clicked.connect(self.reset_view)

        pdf_btn = QPushButton("خروجی PDF")
        pdf_btn.clicked.connect(self.export_pdf)
        word_btn = QPushButton("خروجی Word")
        word_btn.clicked.connect(self.export_word)

        select_btn = QPushButton("انتخاب سوال‌ها")
        select_btn.clicked.connect(self.select_questions)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(reset_btn)
        btn_layout.addWidget(pdf_btn)
        btn_layout.addWidget(word_btn)
        btn_layout.addWidget(select_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    # بارگذاری جدول
    def load_table(self, data):
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(data.columns))
        self.table.setHorizontalHeaderLabels(data.columns.tolist())
        for i, (_, row) in enumerate(data.iterrows()):
            for j, col in enumerate(data.columns):
                self.table.setItem(i, j, QTableWidgetItem(str(row[col])))

    # جست‌وجو
    def search_questions(self):
        text = self.search_input.text()
        if text:
            filtered = self.bank.questions[self.bank.questions.apply(lambda row: row.astype(str).str.contains(text, case=False).any(), axis=1)]
        else:
            filtered = self.bank.questions
        self.current_data = filtered
        self.load_table(self.current_data)

    # فیلتر ستون
    def apply_column_filter(self):
        column = self.column_filter.currentText()
        value = self.filter_input.text()
        if value:
            filtered = self.bank.filter_questions(**{column: value})
        else:
            filtered = self.bank.questions
        self.current_data = filtered
        self.load_table(self.current_data)

    # افزودن سوال
    def add_question(self):
        cols = ["Question","Answer","Option1","Option2","Option3","Category","Source"]
        data = {}
        for col in cols:
            text, ok = QInputDialog.getText(self, "افزودن سوال", f"{col}:")
            if not ok:
                return
            data[col] = text
        self.bank.add_question(data)
        self.current_data = self.bank.list_questions()
        self.load_table(self.current_data)

    # ویرایش سوال
    def edit_question(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "خطا", "یک سوال را انتخاب کنید")
            return
        cols = ["Question","Answer","Option1","Option2","Option3","Category","Source"]
        data = {}
        for j, col in enumerate(cols):
            text, ok = QInputDialog.getText(self, "ویرایش سوال", f"{col}:", text=self.current_data.iloc[selected][col])
            if not ok:
                return
            data[col] = text
        self.bank.questions.iloc[selected] = pd.Series(data)
        self.bank.save_questions()
        self.current_data = self.bank.list_questions()
        self.load_table(self.current_data)

    # حذف سوال
    def delete_question(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "خطا", "یک سوال را انتخاب کنید")
            return
        self.bank.questions.drop(self.current_data.index[selected], inplace=True)
        self.bank.save_questions()
        self.current_data = self.bank.list_questions()
        self.load_table(self.current_data)

    # بازگشت به حالت اولیه
    def reset_view(self):
        self.bank.reset_view()
        self.current_data = self.bank.list_questions()
        self.load_table(self.current_data)
        self.search_input.clear()
        self.filter_input.clear()

    # خروجی PDF
    def export_pdf(self):
        filename, ok = QInputDialog.getText(self, "خروجی PDF", "نام فایل خروجی (مثال: output.pdf):")
        if ok and filename:
            self.bank.export_pdf(filename)
            QMessageBox.information(self, "موفقیت", f"فایل PDF با نام {filename} ساخته شد")

    # خروجی Word
    def export_word(self):
        filename, ok = QInputDialog.getText(self, "خروجی Word", "نام فایل خروجی (مثال: output.docx):")
        if ok and filename:
            self.bank.export_word(filename)
            QMessageBox.information(self, "موفقیت", f"فایل Word با نام {filename} ساخته شد")

    # انتخاب سوال‌ها (دستی یا تصادفی)
    def select_questions(self):
        mode, ok = QInputDialog.getItem(self, "انتخاب سوال‌ها", "نوع انتخاب:", ["دستی", "تصادفی"], 0, False)
        if ok:
            if mode == "دستی":
                indices_str, ok = QInputDialog.getText(self, "انتخاب دستی", "شماره سوال‌ها (با ویرگول جدا کنید):")
                if ok and indices_str:
                    try:
                        indices = [int(x.strip())-1 for x in indices_str.split(",")]
                        self.bank.select_questions(mode="manual", indices=indices)
                        QMessageBox.information(self, "موفقیت", f"{len(indices)} سوال انتخاب شد")
                    except:
                        QMessageBox.warning(self, "خطا", "ورودی نامعتبر")
            else:  # تصادفی
                count, ok = QInputDialog.getInt(self, "انتخاب تصادفی", "تعداد سوالات:", 1, 1, len(self.bank.questions))
                if ok:
                    self.bank.select_questions(mode="random", count=count)
                    QMessageBox.information(self, "موفقیت", f"{count} سوال انتخاب شد")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BankSoalApp()
    window.show()
    sys.exit(app.exec_())
