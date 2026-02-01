# app/db/init_db.py
from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.database import engine, SessionLocal
from app.db.models import Base, Question


SEED_QUESTIONS = [
    # tag: attention / care / trust / romance / space / communication
    {
        "text": "Qaysi holatda o‘zingizni ko‘proq qadrlangan his qilasiz?",
        "option_a": "Yaqin inson tinglab, tushunishga harakat qilsa",
        "option_b": "Yaqin inson amalda yordam berib, yelka bo‘lsa",
        "tag": "care",
        "a_score": 2,
        "b_score": 2,
    },
    {
        "text": "Sizga qaysi biri ko‘proq yoqadi?",
        "option_a": "Oddiy, lekin samimiy gaplar (iliq so‘zlar)",
        "option_b": "Kichkina bo‘lsa ham, kutilmagan sovg‘a yoki e’tibor",
        "tag": "romance",
        "a_score": 2,
        "b_score": 2,
    },
    {
        "text": "Munosabatda siz uchun eng muhim narsa qaysi?",
        "option_a": "Hurmat va muloyim muomala",
        "option_b": "Ishonch va sodiqlik",
        "tag": "trust",
        "a_score": 2,
        "b_score": 2,
    },
    {
        "text": "Norozi bo‘lib qolsangiz, qaysi yo‘l sizga yaqin?",
        "option_a": "Muloyim gaplashib, hammasini tushuntirib olish",
        "option_b": "Biroz jim bo‘lib, keyin tinchgach gaplashish",
        "tag": "communication",
        "a_score": 2,
        "b_score": 2,
    },
    {
        "text": "Sizni xursand qilish uchun qaysi biri ko‘proq ishlaydi?",
        "option_a": "E’tiborli savol: “Qalbing qanday?”",
        "option_b": "Amaliy ish: muammo bo‘lsa, hal qilib berish",
        "tag": "attention",
        "a_score": 2,
        "b_score": 2,
    },
    {
        "text": "Siz uchun “yaqinlik” nimaga o‘xshaydi?",
        "option_a": "Ko‘proq suhbat, dardlashish, birga vaqt",
        "option_b": "Xotirjamlik: yoningda bo‘lish va ishonch",
        "tag": "trust",
        "a_score": 2,
        "b_score": 2,
    },
    {
        "text": "Qaysi uslub sizga mosroq?",
        "option_a": "Ko‘proq romantika: iliq gap, kichik surprizlar",
        "option_b": "Ko‘proq barqarorlik: reja, mas’uliyat, tayanch",
        "tag": "romance",
        "a_score": 2,
        "b_score": 2,
    },
    {
        "text": "Sizga qanday e’tibor yoqadi?",
        "option_a": "Tez-tez hol so‘rash, “nima bo‘ldi?” deb qiziqish",
        "option_b": "Ko‘p bezovta qilmasdan, ishonib qo‘yish",
        "tag": "space",
        "a_score": 2,
        "b_score": 2,
    },
    {
        "text": "Janjalga yaqin vaziyatda siz nimani xohlaysiz?",
        "option_a": "Darrov muloyim gaplashib, muammoni yopish",
        "option_b": "Bir oz vaqt, keyin xotirjam gaplashish",
        "tag": "communication",
        "a_score": 2,
        "b_score": 2,
    },
    {
        "text": "Siz uchun “e’tibor” nimani anglatadi?",
        "option_a": "So‘z bilan tasdiqlash: “Seni qadrlayman”",
        "option_b": "Harakat bilan tasdiqlash: yordam, vaqt, g‘amxo‘rlik",
        "tag": "care",
        "a_score": 2,
        "b_score": 2,
    },
    {
        "text": "Sizga qaysi biri ko‘proq yoqadi?",
        "option_a": "Birga rejalar tuzish va kelajakni muhokama qilish",
        "option_b": "Shu bugun yaxshi kayfiyat va yengil suhbat",
        "tag": "communication",
        "a_score": 2,
        "b_score": 2,
    },
    {
        "text": "Sizni ko‘proq nima xafa qiladi?",
        "option_a": "E’tiborsizlik va sovuq muomala",
        "option_b": "Va’dada turmaslik va beqarorlik",
        "tag": "trust",
        "a_score": 2,
        "b_score": 2,
    },
]


def seed_questions(db: Session) -> int:
    """Agar questions bo'sh bo'lsa, SEED_QUESTIONS ni qo'shadi."""
    exists = db.query(Question).count()
    if exists > 0:
        return 0

    objects = []
    for q in SEED_QUESTIONS:
        objects.append(
            Question(
                text=q["text"],
                option_a=q["option_a"],
                option_b=q["option_b"],
                tag=q["tag"],
                a_score=q.get("a_score", 1),
                b_score=q.get("b_score", 1),
                is_active=True,
            )
        )

    db.add_all(objects)
    db.commit()
    return len(objects)


def init_db(drop_all: bool = False) -> None:
    """
    drop_all=False: normal ishga tushirish.
    drop_all=True: barcha jadvallarni o'chirib, qayta yaratadi (DEV uchun).
    """
    if drop_all:
        Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        added = seed_questions(db)
        if added:
            print(f"✅ {added} ta savol qo‘shildi (seed).")
        else:
            print("ℹ️ Savollar allaqachon mavjud, seed qilinmadi.")

    print("✅ DB init tugadi.")


if __name__ == "__main__":
    # DEVda tozalab qayta yaratmoqchi bo'lsang: init_db(drop_all=True)
    init_db(drop_all=False)
