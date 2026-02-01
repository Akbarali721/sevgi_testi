# app/routers/api.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.invite_service import CreateInviteDTO
from app.services import invite_service, quiz_service

router = APIRouter(prefix="/api", tags=["api"])


# -------- Schemas --------
class InviteCreateIn(BaseModel):
    boy_name: str = Field(..., min_length=2, max_length=80)
    boy_age: int = Field(..., ge=14, le=99)
    boy_zodiac: str = Field(..., min_length=2, max_length=30)
    message: str | None = Field(default=None, max_length=500)


class InviteOut(BaseModel):
    token: str
    status: str
    boy_name: str
    boy_age: int
    boy_zodiac: str
    girl_name: str | None = None
    girl_age: int | None = None
    girl_zodiac: str | None = None


# -------- Endpoints --------
@router.post("/invites", response_model=InviteOut)
def api_create_invite(payload: InviteCreateIn, db: Session = Depends(get_db)):
    inv = invite_service.create_invite(
        db,
        CreateInviteDTO(
            boy_name=payload.boy_name,
            boy_age=payload.boy_age,
            boy_zodiac=payload.boy_zodiac,
            message=payload.message,
        ),
    )
    return InviteOut(
        token=inv.token,
        status=inv.status.value,
        boy_name=inv.boy_name,
        boy_age=inv.boy_age,
        boy_zodiac=inv.boy_zodiac,
        girl_name=inv.girl_name,
        girl_age=inv.girl_age,
        girl_zodiac=inv.girl_zodiac,
    )


@router.get("/invites/{token}", response_model=InviteOut)
def api_get_invite(token: str, db: Session = Depends(get_db)):
    try:
        inv = invite_service.get_invite_by_token_or_404(db, token)
    except Exception:
        raise HTTPException(status_code=404, detail="Invite topilmadi")

    return InviteOut(
        token=inv.token,
        status=inv.status.value,
        boy_name=inv.boy_name,
        boy_age=inv.boy_age,
        boy_zodiac=inv.boy_zodiac,
        girl_name=inv.girl_name,
        girl_age=inv.girl_age,
        girl_zodiac=inv.girl_zodiac,
    )


@router.get("/result/{token}")
def api_get_result(token: str, db: Session = Depends(get_db)):
    """
    JSON natija (bot/frontend uchun qulay).
    profile = scoring_service.build_profile(...) dan keladi.
    """
    try:
        inv = invite_service.get_invite_by_token_or_404(db, token)
    except Exception:
        raise HTTPException(status_code=404, detail="Invite topilmadi")

    profile = quiz_service.get_profile_for_invite(db, token)
    return {
        "token": inv.token,
        "status": inv.status.value,
        "boy": {"name": inv.boy_name, "age": inv.boy_age, "zodiac": inv.boy_zodiac},
        "girl": {"name": inv.girl_name, "age": inv.girl_age, "zodiac": inv.girl_zodiac},
        "profile": profile,  # summary + bullets + tip
    }
