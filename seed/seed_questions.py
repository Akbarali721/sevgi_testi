# seed_questions.py
from app.db.database import SessionLocal
from app.db import models  # noqa: F401  (model'lar import bo'lsin)

def main():
    db = SessionLocal()

    # 1) Qaysi model borligini aniqlab olamiz.
    # Agar sening model noming "Question" bo'lsa shu ishlaydi:
    Question = getattr(__import__("app.db.models", fromlist=["Question"]), "Question", None)

    if Question is None:
        print("❌ Question modeli topilmadi. app/db/models.py ichida model nomini tekshir.")
        return

    # 2) Agar oldin seed qilingan bo'lsa, qayta qo'shmaymiz
    exists = db.query(Question).first()
    if exists:
        print("✅ Savollar avvaldan bor ekan. Seed kerak emas.")
        return

    questions = [
        Question(text="Sevgan insoningiz uchun qaysi biri ko‘proq muhim?", option_a="Iliq so‘z va e’tibor", option_b="Amaliy yordam / ish"),
        Question(text="U xafa bo‘lsa, ko‘proq nimani kutadi?", option_a="Tinglash va tushunish", option_b="Ye­chim taklif qilish"),
        Question(text="Unga yoqadigan sovg‘a qaysi?", option_a="Mayda, lekin samimiy", option_b="Katta va ‘wow’"),
        Question(text="Birga vaqt o‘tkazishda u nimani yoqtiradi?", option_a="Sayr / tashqarida", option_b="Uyda sokin dam"),
        Question(text="U sizdan nimani ko‘proq sezadi?", option_a="Kayfiyatingiz va ohangingizni", option_b="Qilgan ishlaringizni"),
        Question(text="Surpriz masalasida u qaysi tomonga yaqin?", option_a="Kutilmagan kichik e’tibor", option_b="Oldindan rejalangan katta narsa"),
        Question(text="U bilan nizoda eng muhim narsa nima?", option_a="Hurmat bilan gaplashish", option_b="Tezda kelishib olish"),
        Question(text="U sizdan nimani ko‘proq qadrlaydi?", option_a="Doimiy e’tibor", option_b="Barqarorlik va ishonch"),
    ]

    db.add_all(questions)
    db.commit()
    db.close()
    print("✅ Savollar DB ga qo‘shildi!")

if __name__ == "__main__":
    main()
