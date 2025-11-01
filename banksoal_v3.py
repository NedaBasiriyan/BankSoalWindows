import pandas as pd
import random
from fpdf import FPDF
from docx import Document

BANK_FILE = "database.csv"

class QuestionBank:
    def __init__(self):
        self.questions = pd.DataFrame()
        self.original_questions = pd.DataFrame()  # نگهداری نسخه اصلی
        self.selected_questions = pd.DataFrame()
        self.load_questions()

    def load_questions(self):
        try:
            self.questions = pd.read_csv(BANK_FILE)
            self.original_questions = self.questions.copy()
        except FileNotFoundError:
            self.questions = pd.DataFrame(columns=[
                "Question", "Answer", "Option1", "Option2", "Option3", "Category", "Source"
            ])
            self.original_questions = self.questions.copy()

    def save_questions(self):
        self.questions.to_csv(BANK_FILE, index=False)
        self.original_questions = self.questions.copy()

    def add_question(self, question_data):
        self.questions = pd.concat([self.questions, pd.DataFrame([question_data])], ignore_index=True)
        self.original_questions = self.questions.copy()

    def list_questions(self):
        return self.questions.copy()

    def filter_questions(self, **kwargs):
        # فیلتر بر اساس ستون‌ها، kwargs مثل Category="ریاضی"
        filtered = self.questions.copy()
        for key, value in kwargs.items():
            if key in filtered.columns:
                filtered = filtered[filtered[key].astype(str).str.contains(value, case=False)]
        return filtered

    def select_questions(self, mode="manual", indices=None, count=None):
        """
        mode: "manual" یا "random"
        indices: لیست شماره سوال‌ها برای دستی
        count: تعداد سوالات برای تصادفی
        """
        if mode == "manual" and indices:
            self.selected_questions = self.questions.iloc[indices].copy()
        elif mode == "random" and count:
            self.selected_questions = self.questions.sample(n=min(count, len(self.questions))).copy()
        else:
            self.selected_questions = pd.DataFrame()
        return self.selected_questions

    def export_pdf(self, filename="output.pdf"):
        if self.selected_questions.empty:
            data = self.questions
        else:
            data = self.selected_questions

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for idx, row in data.iterrows():
            pdf.multi_cell(0, 8, f"{idx+1}. {row['Question']}")
            pdf.multi_cell(0, 8, f"A) {row['Option1']}    B) {row['Option2']}    C) {row['Option3']}")
            pdf.ln(4)
        pdf.output(filename)

    def export_word(self, filename="output.docx"):
        if self.selected_questions.empty:
            data = self.questions
        else:
            data = self.selected_questions

        doc = Document()
        for idx, row in data.iterrows():
            doc.add_paragraph(f"{idx+1}. {row['Question']}")
            doc.add_paragraph(f"A) {row['Option1']}    B) {row['Option2']}    C) {row['Option3']}")
            doc.add_paragraph("\n")
        doc.save(filename)

    def reset_view(self):
        # بازگشت به حالت اولیه
        self.questions = self.original_questions.copy()
        self.selected_questions = pd.DataFrame()
