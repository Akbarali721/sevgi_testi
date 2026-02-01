# app/db/models.py
from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    String, Integer, DateTime, ForeignKey, Text,
    Enum, Boolean, UniqueConstraint
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship
)
import enum


# ----------------------------
# Base
# ----------------------------
class Base(DeclarativeBase):
    pass


# ----------------------------
# Enums
# ----------------------------
class InviteStatus(str, enum.Enum):
    created = "created"    # user1 taklif yaratdi (hali to'lov bo'lmasligi mumkin)
    paid = "paid"          # to'lov bo'ldi (agar paywall bo'lsa)
    opened = "opened"      # user2 linkni ochdi
    finished = "finished"  # user2 savollarga javob berdi, xulosa tayyor


class PaymentStatus(str, enum.Enum):
    created = "created"
    paid = "paid"
    failed = "failed"


class PaymentProvider(str, enum.Enum):
    demo = "demo"      # MVP
    payme = "payme"    # keyin
    click = "click"    # keyin


class AnswerChoice(str, enum.Enum):
    A = "A"
    B = "B"


# ----------------------------
# Models
# ----------------------------
class Invite(Base):
    """
    Endi markaziy obyekt: Invite (taklif).
    user1 -> invite yaratadi -> link/token -> user2 javob beradi -> summary user1 ga.
    """
    __tablename__ = "invites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Link/token orqali user2 kiradi
    token: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)

    status: Mapped[InviteStatus] = mapped_column(
        Enum(InviteStatus, name="invite_status"),
        default=InviteStatus.created,
        nullable=False
    )

    # User1 (yigit) ma'lumotlari
    boy_name: Mapped[str] = mapped_column(String(80), nullable=False)
    boy_age: Mapped[int] = mapped_column(Integer, nullable=False)
    boy_zodiac: Mapped[str] = mapped_column(String(30), nullable=False)

    # Optional: user1 tomonidan yoziladigan muloyim xabar
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # User2 (qiz) ma'lumotlari (link ochganda yoki testdan oldin to'ldiriladi)
    girl_name: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    girl_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    girl_zodiac: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    # Results cache (MVPda natijani shu yerga yozib qo'yish mumkin)
    result_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    zodiac_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    answers: Mapped[List["Answer"]] = relationship(
        back_populates="invite",
        cascade="all, delete-orphan"
    )

    payments: Mapped[List["Payment"]] = relationship(
        back_populates="invite",
        cascade="all, delete-orphan"
    )


class Question(Base):
    """
    A/B savollar banki.
    tag - scoring uchun.
    """
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    text: Mapped[str] = mapped_column(Text, nullable=False)
    option_a: Mapped[str] = mapped_column(String(255), nullable=False)
    option_b: Mapped[str] = mapped_column(String(255), nullable=False)

    # Masalan: "attention", "trust", "romance", "space", "care"
    tag: Mapped[str] = mapped_column(String(40), nullable=False, index=True)

    # scoring: A va B bosilganda qancha ball
    a_score: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    b_score: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    answers: Mapped[List["Answer"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan"
    )


class Answer(Base):
    """
    Har bir invite uchun savolga berilgan javob.
    Bitta invite’da bitta question bir marta javoblanishi kerak.
    """
    __tablename__ = "answers"
    __table_args__ = (
        UniqueConstraint("invite_id", "question_id", name="uq_invite_question"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    invite_id: Mapped[int] = mapped_column(ForeignKey("invites.id", ondelete="CASCADE"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)

    choice: Mapped[AnswerChoice] = mapped_column(
        Enum(AnswerChoice, name="answer_choice"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    invite: Mapped["Invite"] = relationship(back_populates="answers")
    question: Mapped["Question"] = relationship(back_populates="answers")


class Payment(Base):
    """
    To'lovlar jadvali: demo/payme/click
    Endi to'lov invite (taklif) ga ulanadi.
    """
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    invite_id: Mapped[int] = mapped_column(ForeignKey("invites.id", ondelete="CASCADE"), nullable=False)

    provider: Mapped[PaymentProvider] = mapped_column(
        Enum(PaymentProvider, name="payment_provider"),
        default=PaymentProvider.demo,
        nullable=False
    )

    amount: Mapped[int] = mapped_column(Integer, nullable=False, default=14999)

    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status"),
        default=PaymentStatus.created,
        nullable=False
    )

    # gateway transaction id (payme/click uchun keyin kerak bo'ladi)
    provider_txn_id: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    invite: Mapped["Invite"] = relationship(back_populates="payments")
