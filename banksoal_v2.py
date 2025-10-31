import json
import os
import random

# مسیر فایل بانک سوالات
BANK_FILE = "question_bank_v2.json"

# نمونه داده اولیه با ستون‌های اضافی
default_questions = [
    {
        "id": 1,
        "question": "ویندوز ۱۰ در چه سالی منتشر شد؟",
        "options": ["2014", "2015", "2016", "2017"],
        "answer": "2015",
        "lesson": "کامپیوتر",
        "source": "کتاب درسی",
        "teacher": "آقای احمدی",
        "year": 2020,
        "term": 1
    },
    {
        "id": 2,
        "question": "کلید میانبر برای کپی کردن چیست؟",
        "options": ["Ctrl+C", "Ctrl+V", "Ctrl+X", "Alt+C"],
        "answer": "Ctrl+C",
        "lesson": "کامپیوتر",
        "source": "جزوه استاد",
        "teacher": "خانم حسینی",
        "year": 2021,
        "term": 2
    }
]

# اگر فایل وجود نداشت، ایجاد شود
if not os.path.exists(BANK_FILE):
    with open(BANK_FILE, "w", encoding="utf-8") as f:
        json.dump(default_questions, f, ensure_ascii=False, indent=4)

# افزودن سوال جدید
def add_question(question, options, answer, lesson, source, teacher, year, term):
    with open(BANK_FILE, "r+", encoding="utf-8") as f:
        data = json.load(f)
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
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.truncate()

# نمایش سوالات
def list_questions():
    with open(BANK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        for q in data:
            print(f"{q['id']}. {q['question']}")
            for idx, opt in enumerate(q["options"], 1):
                print(f"   {idx}. {opt}")
            print(f"   پاسخ: {q['answer']}")
            print(f"   درس: {q['lesson']}, منبع: {q['source']}, استاد: {q['teacher']}, سال: {q['year']}, ترم: {q['term']}\n")

# فیلتر سوالات بر اساس ستون‌ها
def filter_questions(lesson=None, source=None, teacher=None, year=None, term=None):
    with open(BANK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        filtered = [
            q for q in data
            if (lesson is None or q["lesson"] == lesson)
            and (source is None or q["source"] == source)
            and (teacher is None or q["teacher"] == teacher)
            and (year is None or q["year"] == year)
            and (term is None or q["term"] == term)
        ]
        for q in filtered:
            print(f"{q['id']}. {q['question']} (درس: {q['lesson']}, منبع: {q['source']}, استاد: {q['teacher']}, سال: {q['year']}, ترم: {q['term']})")

# نمونه استفاده
if __name__ == "__main__":
    print("لیست کامل سوالات:")
    list_questions()

    print("\nفیلتر بر اساس درس 'کامپیوتر':")
    filter_questions(lesson="کامپیوتر")

    print("\nافزودن یک سوال جدید:")
    add_question(
        question="Python چیست؟",
        options=["زبان برنامه نویسی", "سیستم عامل", "نرم افزار", "پایگاه داده"],
        answer="زبان برنامه نویسی",
        lesson="کامپیوتر",
        source="کتاب مرجع",
        teacher="آقای احمدی",
        year=2023,
        term=1
    )

    print("\nلیست سوالات پس از افزودن:")
    list_questions()
