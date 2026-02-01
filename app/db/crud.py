from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.models import (
    Invite, Question, Answer, Payment,
    InviteStatus, PaymentStatus, PaymentProvider, AnswerChoice
)


# -------- Invites --------
def create_invite(
    db: Session,
    boy_name: str,
    boy_age: int,
    boy_zodiac: str,
    token: str,
    message: str | None = None,
) -> Invite:
    """
    User1 (yigit) taklif yaratadi.
    token router/service qatlamida generatsiya qilinadi (uuid/secrets).
    """
    inv = Invite(
        boy_name=boy_name.strip(),
        boy_age=int(boy_age),
        boy_zodiac=boy_zodiac.strip(),
        token=token,
        message=message.strip() if message else None,
        status=InviteStatus.created,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


def get_invite(db: Session, invite_id: int) -> Invite | None:
    return db.get(Invite, invite_id)


def get_invite_by_token(db: Session, token: str) -> Invite | None:
    return (
        db.query(Invite)
        .filter(Invite.token == token.strip())
        .first()
    )


def mark_invite_opened(db: Session, invite_id: int) -> Invite:
    inv = db.get(Invite, invite_id)
    if not inv:
        raise ValueError("Invite topilmadi")

    if inv.status in (InviteStatus.created, InviteStatus.paid) and inv.opened_at is None:
        inv.status = InviteStatus.opened
        inv.opened_at = datetime.utcnow()
        inv.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(inv)

    return inv


def set_girl_data_by_token(
    db: Session,
    token: str,
    girl_name: str,
    girl_age: int,
    girl_zodiac: str,
) -> Invite:
    """
    User2 link/token orqali kirib, o'z ma'lumotini kiritadi.
    """
    inv = get_invite_by_token(db, token)
    if not inv:
        raise ValueError("Invite topilmadi")

    inv.girl_name = girl_name.strip()
    inv.girl_age = int(girl_age)
    inv.girl_zodiac = girl_zodiac.strip()
    inv.updated_at = datetime.utcnow()

    # agar invite hali created bo'lsa, openedga o'tkazamiz
    if inv.status in (InviteStatus.created, InviteStatus.paid):
        inv.status = InviteStatus.opened
        if inv.opened_at is None:
            inv.opened_at = datetime.utcnow()

    db.commit()
    db.refresh(inv)
    return inv


def mark_invite_finished(
    db: Session,
    invite_id: int,
    result_summary: str | None = None,
    zodiac_score: int | None = None,
) -> Invite:
    """
    User2 savollarni tugatdi: invite finished.
    """
    inv = db.get(Invite, invite_id)
    if not inv:
        raise ValueError("Invite topilmadi")

    inv.status = InviteStatus.finished
    inv.finished_at = datetime.utcnow()
    inv.updated_at = datetime.utcnow()

    if result_summary is not None:
        inv.result_summary = result_summary
    if zodiac_score is not None:
        inv.zodiac_score = int(zodiac_score)

    db.commit()
    db.refresh(inv)
    return inv


# -------- Questions --------
def get_12_questions(db: Session) -> list[Question]:
    # MVP: random 12
    return (
        db.query(Question)
        .filter(Question.is_active == True)
        .order_by(func.random())
        .limit(12)
        .all()
    )


# -------- Answers --------
def save_answers(db: Session, invite_id: int, answers_map: dict[int, str]) -> None:
    """
    answers_map: {question_id: "A"|"B"}
    """
    inv = db.get(Invite, invite_id)
    if not inv:
        raise ValueError("Invite topilmadi")

    for qid, choice in answers_map.items():
        choice = str(choice).upper().strip()
        if choice not in ("A", "B"):
            continue

        existing = (
            db.query(Answer)
            .filter(Answer.invite_id == invite_id, Answer.question_id == int(qid))
            .first()
        )

        if existing:
            existing.choice = AnswerChoice(choice)
        else:
            db.add(Answer(
                invite_id=invite_id,
                question_id=int(qid),
                choice=AnswerChoice(choice),
            ))

    # statusni opened qilib qo'yamiz (agar hali o‘tmagan bo‘lsa)
    if inv.status in (InviteStatus.created, InviteStatus.paid):
        inv.status = InviteStatus.opened
        if inv.opened_at is None:
            inv.opened_at = datetime.utcnow()
        inv.updated_at = datetime.utcnow()

    db.commit()


def get_answers_with_questions(db: Session, invite_id: int) -> list[tuple[Answer, Question]]:
    return (
        db.query(Answer, Question)
        .join(Question, Answer.question_id == Question.id)
        .filter(Answer.invite_id == invite_id)
        .all()
    )


# -------- Payments (MVP demo) --------
def create_payment(
    db: Session,
    invite_id: int,
    amount: int = 14999,
    provider: str = "demo"
) -> Payment:
    inv = db.get(Invite, invite_id)
    if not inv:
        raise ValueError("Invite topilmadi")

    p = Payment(
        invite_id=invite_id,
        amount=int(amount),
        provider=PaymentProvider(provider),
        status=PaymentStatus.created
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def mark_payment_paid(db: Session, payment_id: int) -> Payment:
    p = db.get(Payment, payment_id)
    if not p:
        raise ValueError("Payment topilmadi")

    p.status = PaymentStatus.paid
    p.paid_at = datetime.utcnow()
    db.commit()
    db.refresh(p)

    # Invite status ham paid bo'ladi (paywall ishlatilsa)
    inv = db.get(Invite, p.invite_id)
    if inv and inv.status == InviteStatus.created:
        inv.status = InviteStatus.paid
        inv.updated_at = datetime.utcnow()
        db.commit()

    return p
