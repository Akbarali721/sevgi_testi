import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Question

DATA_PATH = Path(__file__).parent / "questions.json"


def load_questions() -> list[dict]:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("questions.json list bo‘lishi kerak")
    return data


def upsert_question(db: Session, q: dict) -> bool:
    """
    Dublikat bo'lmasin: text bo'yicha tekshiramiz.
    Qaytaradi: True (qo'shildi) / False (bor edi)
    """
    text = q["text"].strip()
    exists = db.query(Question).filter(Question.text == text).first()
    if exists:
        return False

    obj = Question(
        text=text,
        option_a=q["option_a"].strip(),
        option_b=q["option_b"].strip(),
        tag=q["tag"].strip(),
        a_score=int(q.get("a_score", 1)),
        b_score=int(q.get("b_score", 1)),
        is_active=bool(q.get("is_active", True))
    )
    db.add(obj)
    return True


def main():
    questions = load_questions()
    db = SessionLocal()

    added = 0
    skipped = 0
    try:
        for q in questions:
            ok = upsert_question(db, q)
            if ok:
                added += 1
            else:
                skipped += 1

        db.commit()
        print(f"✅ Seed tugadi. Added: {added}, Skipped: {skipped}")
    except Exception as e:
        db.rollback()
        print("❌ Xatolik:", e)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
