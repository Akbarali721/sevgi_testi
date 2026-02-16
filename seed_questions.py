# seed_questions.py
from app.db.database import SessionLocal
from app.db.models import Question

def main():
    db = SessionLocal()

    # qayta qo'shilmasin
    if db.query(Question).first():
        print("✅ Savollar avvaldan bor. Seed o'tkazilmadi.")
        return

    questions = [
        Question(
            text="Sevgan insoningiz ko‘proq nimani qadrlaydi?",
            option_a="Iliq so‘z, mehr va e’tibor",
            option_b="Amaliy yordam, ish bilan qo‘llab-quvvatlash",
            tag="care",
            a_score=1, b_score=1, is_active=True,
        ),
        Question(
            text="U xafa bo‘lsa, sizdan ko‘proq nimani kutadi?",
            option_a="Tinglash va tushunish",
            option_b="Muammoni tezda hal qilish",
            tag="support",
            a_score=1, b_score=1, is_active=True,
        ),
        Question(
            text="Sovg‘a masalasida u qaysi tomonga yaqin?",
            option_a="Mayda, lekin samimiy sovg‘a",
            option_b="Katta va ‘wow’ sovg‘a",
            tag="romance",
            a_score=1, b_score=1, is_active=True,
        ),
        Question(
            text="Birga vaqt o‘tkazishda u nimani yoqtiradi?",
            option_a="Sayr / tashqarida",
            option_b="Uyda sokin dam",
            tag="time",
            a_score=1, b_score=1, is_active=True,
        ),
        Question(
            text="Nizoda u nimani xohlaydi?",
            option_a="Hurmat bilan muloyim gaplashish",
            option_b="Tezda yechim topib, tinchish",
            tag="communication",
            a_score=1, b_score=1, is_active=True,
        ),
        Question(
            text="Unga qaysi biri ko‘proq ‘sevgi’ bo‘lib tuyuladi?",
            option_a="Birga vaqt va e’tibor",
            option_b="Barqarorlik va ishonch",
            tag="love_language",
            a_score=1, b_score=1, is_active=True,
        ),
        Question(
            text="Surpriz qilsangiz, qaysi biri yoqimliroq?",
            option_a="Kutilmagan kichik e’tibor",
            option_b="Oldindan rejalangan katta surpriz",
            tag="romance",
            a_score=1, b_score=1, is_active=True,
        ),
        Question(
            text="U siz bilan gaplashganda ko‘proq nimani sezadi?",
            option_a="Ohang va kayfiyatni",
            option_b="Gapning mazmunini",
            tag="communication",
            a_score=1, b_score=1, is_active=True,
        ),
    ]

    db.add_all(questions)
    db.commit()
    db.close()
    print(f"✅ Seed done: {len(questions)} ta savol qo‘shildi!")

if __name__ == "__main__":
    main()
