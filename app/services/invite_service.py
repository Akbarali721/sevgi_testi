# app/services/invite_service.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import secrets
from typing import Optional

from sqlalchemy.orm import Session

from app.db import crud
from app.db.models import Invite, InviteStatus


# ----------------------------
# Errors (toza xatoliklar)
# ----------------------------
class InviteError(Exception):
    pass


class InviteNotFound(InviteError):
    pass


class InviteAlreadyFinished(InviteError):
    pass


class InviteInvalidStatus(InviteError):
    pass


# ----------------------------
# DTO (ixtiyoriy, lekin qulay)
# ----------------------------
@dataclass
class CreateInviteDTO:
    boy_name: str
    boy_age: int
    boy_zodiac: str
    message: Optional[str] = None


# ----------------------------
# Token generator
# ----------------------------
def generate_unique_token(db: Session, length_hint: int = 22, max_tries: int = 8) -> str:
    """
    Token: link uchun unikal string.
    secrets.token_urlsafe(n) -> URL-safe token qaytaradi.
    """
    for _ in range(max_tries):
        token = secrets.token_urlsafe(length_hint)[:80]  # DB column String(80)
        exists = crud.get_invite_by_token(db, token)
        if not exists:
            return token
    raise InviteError("Token yaratib bo'lmadi (unique). Qayta urinib ko'ring.")


# ----------------------------
# Status flow helpers
# ----------------------------
def _ensure_not_finished(inv: Invite) -> None:
    if inv.status == InviteStatus.finished:
        raise InviteAlreadyFinished("Invite allaqachon yakunlangan.")


def _touch(inv: Invite) -> None:
    inv.updated_at = datetime.utcnow()


# ----------------------------
# Public API (routerlar shuni chaqiradi)
# ----------------------------
def create_invite(db: Session, data: CreateInviteDTO) -> Invite:
    """
    User1: taklif yaratadi -> token + InviteStatus.created
    """
    token = generate_unique_token(db)
    inv = crud.create_invite(
        db=db,
        boy_name=data.boy_name,
        boy_age=data.boy_age,
        boy_zodiac=data.boy_zodiac,
        token=token,
        message=data.message,
    )
    return inv


def get_invite_by_token_or_404(db: Session, token: str) -> Invite:
    inv = crud.get_invite_by_token(db, token)
    if not inv:
        raise InviteNotFound("Invite topilmadi.")
    return inv


def open_invite(db: Session, token: str) -> Invite:
    """
    User2 linkni ochdi: status created/paid bo'lsa -> opened
    """
    inv = get_invite_by_token_or_404(db, token)
    _ensure_not_finished(inv)

    # Status flow: created/paid -> opened
    if inv.status in (InviteStatus.created, InviteStatus.paid):
        inv = crud.mark_invite_opened(db, inv.id)
    # opened bo'lsa - o'zgarmaydi
    # boshqa holat bo'lsa ham hozircha jim (masalan: future: expired)
    return inv


def set_girl_profile(db: Session, token: str, girl_name: str, girl_age: int, girl_zodiac: str) -> Invite:
    """
    User2 profilini kiritadi (ixtiyoriy bosqich).
    """
    inv = get_invite_by_token_or_404(db, token)
    _ensure_not_finished(inv)

    inv = crud.set_girl_data_by_token(
        db=db,
        token=token,
        girl_name=girl_name,
        girl_age=girl_age,
        girl_zodiac=girl_zodiac,
    )
    return inv


def finish_invite(
    db: Session,
    invite_id: int,
    result_summary: Optional[str] = None,
    zodiac_score: Optional[int] = None,
) -> Invite:
    """
    Javoblar saqlangandan keyin invite finished bo'ladi.
    """
    inv = crud.get_invite(db, invite_id)
    if not inv:
        raise InviteNotFound("Invite topilmadi.")

    _ensure_not_finished(inv)

    inv = crud.mark_invite_finished(
        db=db,
        invite_id=invite_id,
        result_summary=result_summary,
        zodiac_score=zodiac_score,
    )
    return inv


def can_view_full_summary(inv: Invite) -> bool:
    """
    Paywall bo'lsa: faqat paid bo'lganda to'liq xulosa.
    Hozir MVP: agar paywall ishlatmasang, True qilib qo'yish mumkin.
    """
    # Variant A: har doim ruxsat (MVP)
    # return True

    # Variant B: faqat paid bo'lsa
    return inv.status in (InviteStatus.paid, InviteStatus.opened, InviteStatus.finished)
