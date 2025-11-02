# main.py
import sys
import pandas as pd
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
        self.resize(950, 600)

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

    # بارگذاری جدول (شماره ردیف نمایش داده می‌شود)
    def load_table(self, data: pd.DataFrame):
        data = data.reset_index()  # keep original index in 'index' column
        rows = len(data)
        cols = len(data.columns) - 1  # exclude the added 'index' column for headerlabels
        self.table.clear()
        self.table.setRowCount(rows)
        self.table.setColumnCount(cols + 1)  # add a leading "No" column
        headers = ["No"] + [c for c in data.columns if c != "index"]
        self.table.setHorizontalHeaderLabels(headers)

        for i, (_, row) in enumerate(data.iterrows()):
            # No column
            self.table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            col_j = 1
            for col in data.columns:
                if col == "index":
                    continue
                val = str(row[col]) if pd.notna(row[col]) else ""
                self.table.setItem(i, col_j, QTableWidgetItem(val))
                col_j += 1

        # store the displayed DataFrame to be able to map selection -> original index label
        self.displayed_df = data  # has 'index' column (original labels)

    # جست‌وجو
    def search_questions(self):
        text = self.search_input.text().strip()
        if text:
            filtered = self.bank.questions[self.bank.questions.apply(lambda row: row.astype(str).str.contains(text, case=False, na=False).any(), axis=1)]
        else:
            filtered = self.bank.questions
        self.current_data = filtered
        self.load_table(self.current_data)

    # فیلتر ستون
    def apply_column_filter(self):
        column = self.column_filter.currentText()
        value = self.filter_input.text().strip()
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
        ok_bool, err = self.bank.add_question(data)
        if not ok_bool:
            QMessageBox.critical(self, "خطا در افزودن", f"خطا: {err}")
            return
        saved, err = self.bank.save_questions()
        if not saved:
            QMessageBox.critical(self, "خطا در ذخیره", f"خطا: {err}")
        self.current_data = self.bank.list_questions()
        self.load_table(self.current_data)

    # ویرایش سوال
    def edit_question(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "خطا", "یک سوال را انتخاب کنید")
            return
        # original index label for the selected displayed row
        orig_label = self.displayed_df.at[selected, "index"]
        cols = ["Question","Answer","Option1","Option2","Option3","Category","Source"]
        data = {}
        for j, col in enumerate(cols):
            current_text = str(self.bank.questions.at[orig_label, col]) if orig_label in self.bank.questions.index else ""
            text, ok = QInputDialog.getText(self, "ویرایش سوال", f"{col}:", text=current_text)
            if not ok:
                return
            data[col] = text
        try:
            # use .loc with label to update
            for k, v in data.items():
                self.bank.questions.at[orig_label, k] = v
            saved, err = self.bank.save_questions()
            if not saved:
                QMessageBox.critical(self, "خطا در ذخیره", f"خطا: {err}")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ویرایش: {e}")
            return
        self.current_data = self.bank.list_questions()
        self.load_table(self.current_data)

    # حذف سوال
    def delete_question(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "خطا", "یک سوال را انتخاب کنید")
            return
        orig_label = self.displayed_df.at[selected, "index"]
        reply = QMessageBox.question(self, "تایید حذف", "آیا از حذف این سوال مطمئن هستید؟", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.bank.questions = self.bank.questions.drop(index=orig_label)
                self.bank.questions.reset_index(drop=True, inplace=True)  # reindex so labels remain simple
                saved, err = self.bank.save_questions()
                if not saved:
                    QMessageBox.critical(self, "خطا در ذخیره", f"خطا: {err}")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در حذف: {e}")
                return
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
            if not filename.lower().endswith(".pdf"):
                filename += ".pdf"
            success, err = self.bank.export_pdf(filename)
            if success:
                QMessageBox.information(self, "موفقیت", f"فایل PDF با نام {filename} ساخته شد")
            else:
                QMessageBox.critical(self, "خطا در خروجی PDF", f"خروجی ساخته نشد:\n{err}")

    # خروجی Word
    def export_word(self):
        filename, ok = QInputDialog.getText(self, "خروجی Word", "نام فایل خروجی (مثال: output.docx):")
        if ok and filename:
            if not filename.lower().endswith(".docx"):
                filename += ".docx"
            success, err = self.bank.export_word(filename)
            if success:
                QMessageBox.information(self, "موفقیت", f"فایل Word با نام {filename} ساخته شد")
            else:
                QMessageBox.critical(self, "خطا در خروجی Word", f"خروجی ساخته نشد:\n{err}")

    # انتخاب سوال‌ها (دستی یا تصادفی)
    def select_questions(self):
        mode, ok = QInputDialog.getItem(self, "انتخاب سوال‌ها", "نوع انتخاب:", ["دستی", "تصادفی"], 0, False)
        if not ok:
            return
        if mode == "دستی":
            indices_str, ok = QInputDialog.getText(self, "انتخاب دستی", "شماره سوال‌ها (همان شماره‌های ستون No؛ با ویرگول جدا کنید):")
            if ok and indices_str:
                try:
                    # parse numbers (1-based displayed)
                    nums = [int(x.strip()) for x in indices_str.split(",") if x.strip()]
                    # map displayed numbers to original labels using displayed_df
                    labels = []
                    for n in nums:
                        pos = n - 1
                        if 0 <= pos < len(self.displayed_df):
                            labels.append(self.displayed_df.at[pos, "index"])
                    if not labels:
                        QMessageBox.warning(self, "هشدار", "هیچ شماره معتبری وارد نشد")
                        return
                    ok_bool, err = self.bank.select_questions(mode="manual", indices=labels, indices_are_labels=True)
                    if not ok_bool:
                        QMessageBox.critical(self, "خطا در انتخاب", f"خطا: {err}")
                        return
                    QMessageBox.information(self, "موفقیت", f"{len(labels)} سوال انتخاب شد")
                except Exception:
                    QMessageBox.warning(self, "خطا", "ورودی نامعتبر")
        else:  # تصادفی
            try:
                max_count = len(self.bank.questions)
                count, ok = QInputDialog.getInt(self, "انتخاب تصادفی", "تعداد سوالات:", 1, 1, max_count)
                if ok:
                    ok_bool, err = self.bank.select_questions(mode="random", count=count)
                    if not ok_bool:
                        QMessageBox.critical(self, "خطا در انتخاب", f"خطا: {err}")
                        return
                    QMessageBox.information(self, "موفقیت", f"{count} سوال انتخاب شد")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BankSoalApp()
    window.show()
    sys.exit(app.exec_())
