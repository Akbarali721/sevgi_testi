# app/services/quiz_service.py
from __future__ import annotations

from typing import Dict, List, Tuple, Any

from sqlalchemy.orm import Session

from app.db import crud
from app.db.models import Invite, InviteStatus
from app.services.invite_service import get_invite_by_token_or_404, open_invite, finish_invite
from app.services.scoring_service import build_profile


class QuizError(Exception):
    pass


def get_quiz_questions(db: Session) -> list:
    """
    MVP: bazadan random 12 ta savol.
    """
    return crud.get_12_questions(db)


def parse_answers_map(form: Any) -> Dict[int, str]:
    """
    form: request.form() (starlette)
    HTML input name: q_{question_id}
    value: "A" / "B"
    """
    answers_map: Dict[int, str] = {}

    for key, value in form.items():
        if not str(key).startswith("q_"):
            continue

        qid = str(key).replace("q_", "").strip()
        if not qid.isdigit():
            continue

        choice = str(value).upper().strip()
        if choice not in ("A", "B"):
            continue

        answers_map[int(qid)] = choice

    return answers_map


def _get_invite_answers_letters(db: Session, invite_id: int) -> List[str]:
    """
    DBdan shu invite uchun javoblarni chiqarib,
    ['A','B',...] ko'rinishga keltiramiz.
    """
    pairs: List[Tuple[Any, Any]] = crud.get_answers_with_questions(db, invite_id)
    # pairs: [(Answer, Question), ...]
    letters: List[str] = []
    for ans, _q in pairs:
        letters.append(str(ans.choice))
    return letters


def submit_quiz_by_token(db: Session, token: str, form: Any) -> Invite:
    """
    User2 token link orqali kirib javob beradi:
    - invite opened bo'ladi (agar oldin bo'lmasa)
    - answers saqlanadi
    - scoring qilinadi (build_profile)
    - invite finished (result_summary cache ixtiyoriy)
    """
    # 1) invite mavjudligini tekshiramiz + opened statusga o'tkazamiz
    inv = get_invite_by_token_or_404(db, token)
    if inv.status == InviteStatus.finished:
        # qayta submit bo'lishini hozircha bloklaymiz
        raise QuizError("Bu suhbat allaqachon yakunlangan.")

    open_invite(db, token)

    # 2) answers_map yig'amiz va DBga yozamiz
    answers_map = parse_answers_map(form)
    if not answers_map:
        raise QuizError("Javoblar topilmadi. Iltimos, savollarga javob bering.")

    crud.save_answers(db, invite_id=inv.id, answers_map=answers_map)

    # 3) scoring (A/B) -> profile
    letters = _get_invite_answers_letters(db, inv.id)
    profile = build_profile(letters)  # {'key','summary','bullets','tip'} :contentReference[oaicite:2]{index=2}

    # 4) invite finished + summary cache (MVP uchun qulay)
    # result_summary ni hozircha faqat summary matn sifatida saqlaymiz
    inv = finish_invite(
        db,
        invite_id=inv.id,
        result_summary=profile.get("summary"),
        zodiac_score=inv.zodiac_score,  # agar boshqa joyda hisoblanayotgan bo'lsa
    )
    return inv


def get_profile_for_invite(db: Session, token: str) -> dict:
    """
    Result sahifasi uchun: invite token -> answers -> build_profile
    """
    inv = get_invite_by_token_or_404(db, token)
    letters = _get_invite_answers_letters(db, inv.id)
    if not letters:
        return {}

    return build_profile(letters)
