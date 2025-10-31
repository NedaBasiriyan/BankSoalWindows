import json
import os
import random
from docx import Document
from fpdf import FPDF

# مسیر فایل بانک سوالات
BANK_FILE = "question_bank_v2.json"

# بارگذاری بانک سوالات
def load_questions():
    if not os.path.exists(BANK_FILE):
        print("فایل بانک سوالات پیدا نشد!")
        return []
    with open(BANK_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ذخیره بانک سوالات
def save_questions(data):
    with open(BANK_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# افزودن سوال
def add_question(question, options, answer, lesson, source, teacher, year, term):
    data = load_questions()
    new_id = max([q["id"] for q in data], default=0) + 1
    data.append({
        "id": new_id,
        "question": question,
        "options": options,
        "answer": answer,
        "lesson": lesson,
        "source": source,
        "teacher": teacher,
        "year": year,
        "term": term
    })
    save_questions(data)

# لیست سوالات
def list_questions(data=None):
    if data is None:
        data = load_questions()
    for q in data:
        print(f"{q['id']}. {q['question']}")
        for idx, opt in enumerate(q["options"], 1):
            print(f"   {idx}. {opt}")
        print(f"   پاسخ: {q['answer']}")
        print(f"درس: {q['lesson']}, منبع: {q['source']}, استاد: {q['teacher']}, سال: {q['year']}, ترم: {q['term']}\n")

# فیلتر سوالات
def filter_questions(lesson=None, source=None, teacher=None, year=None, term=None):
    data = load_questions()
    filtered = [
        q for q in data
        if (lesson is None or q["lesson"] == lesson)
        and (source is None or q["source"] == source)
        and (teacher is None or q["teacher"] == teacher)
        and (year is None or q["year"] == year)
        and (term is None or q["term"] == term)
    ]
    return filtered

# انتخاب سوالات برای خروجی
def select_questions(data, count=None, manual_ids=None):
    if manual_ids:
        selected = [q for q in data if q["id"] in manual_ids]
    else:
        if count is None or count > len(data):
            count = len(data)
        selected = random.sample(data, count)
    return selected

# خروجی Word
def export_word(selected, filename="questions.docx"):
    doc = Document()
    for q in selected:
        doc.add_paragraph(f"{q['id']}. {q['question']}")
        for idx, opt in enumerate(q["options"], 1):
            doc.add_paragraph(f"   {idx}. {opt}")
        doc.add_paragraph(f"پاسخ: {q['answer']}\n")
    doc.save(filename)
    print(f"فایل Word ذخیره شد: {filename}")

# خروجی PDF
def export_pdf(selected, filename="questions.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for q in selected:
        pdf.multi_cell(0, 8, f"{q['id']}. {q['question']}")
        for idx, opt in enumerate(q["options"], 1):
            pdf.multi_cell(0, 8, f"   {idx}. {opt}")
        pdf.multi_cell(0, 8, f"پاسخ: {q['answer']}\n")
    pdf.output(filename)
    print(f"فایل PDF ذخیره شد: {filename}")

# بازگشت به حالت اولیه (لیست کامل)
def reset_view():
    return load_questions()

# نمونه استفاده
if __name__ == "__main__":
    all_q = reset_view()
    print("لیست کامل سوالات:")
    list_questions(all_q)

    # فیلتر نمونه
    filtered = filter_questions(lesson="کامپیوتر")
    print("\nسوالات فیلتر شده بر اساس درس 'کامپیوتر':")
    list_questions(filtered)

    # انتخاب تصادفی 2 سوال
    selected_random = select_questions(filtered, count=2)
    print("\nسوالات انتخاب تصادفی:")
    list_questions(selected_random)
    export_word(selected_random)
    export_pdf(selected_random)

    # انتخاب دستی سوالات با شناسه
    selected_manual = select_questions(filtered, manual_ids=[1])
    print("\nسوالات انتخاب دستی:")
    list_questions(selected_manual)
    export_word(selected_manual, filename="manual_questions.docx")
    export_pdf(selected_manual, filename="manual_questions.pdf")
