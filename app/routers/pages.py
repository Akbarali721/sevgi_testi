# app/routers/pages.py
from __future__ import annotations

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.invite_service import CreateInviteDTO
from app.services import invite_service
from app.services.zodiac_service import zodiac_compatibility

# ✅ Yangi: 2-blokli profil generator
from app.profiles import get_profile  # yoki get_profile_dict

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# ✅ PROD domen (hozir Render)
BASE_URL = "https://sevgi-testi-7jd2.onrender.com"


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ---------- BOY (User1) ----------
@router.get("/start", response_class=HTMLResponse)
def boy_form(request: Request):
    return templates.TemplateResponse("boy_form.html", {"request": request})


@router.post("/start")
def boy_submit(
    request: Request,
    boy_name: str = Form(...),
    boy_age: int = Form(...),
    boy_zodiac: str = Form(...),
    message: str | None = Form(None),
    db: Session = Depends(get_db),
):
    # Invite yaratamiz (token avtomatik)
    inv = invite_service.create_invite(
        db,
        CreateInviteDTO(
            boy_name=boy_name,
            boy_age=boy_age,
            boy_zodiac=boy_zodiac,
            message=message,
        ),
    )

    # User1 ga "share link" sahifa chiqaramiz (linkni qizga yuboradi)
    return RedirectResponse(url=f"/share/{inv.token}", status_code=303)


# ---------- SHARE (User1 linkni ko'chirib yuboradi) ----------
@router.get("/share/{token}", response_class=HTMLResponse)
def share_page(request: Request, token: str, db: Session = Depends(get_db)):
    inv = invite_service.get_invite_by_token_or_404(db, token)

    # ✅ Qizga yuboriladigan to‘liq link (absolute)
    girl_link = f"{BASE_URL}/girl/{token}"

    return templates.TemplateResponse(
        "share.html",
        {
            "request": request,
            "invite": inv,
            "girl_link": girl_link,
        },
    )


# ---------- GIRL (User2) ----------
@router.get("/girl/{token}", response_class=HTMLResponse)
def girl_form(request: Request, token: str, db: Session = Depends(get_db)):
    inv = invite_service.get_invite_by_token_or_404(db, token)
    return templates.TemplateResponse(
        "girl_form.html",
        {"request": request, "invite": inv},
    )


@router.post("/girl/{token}")
def girl_submit(
    request: Request,
    token: str,
    girl_name: str = Form(...),
    girl_age: int = Form(...),
    girl_zodiac: str = Form(...),
    db: Session = Depends(get_db),
):
    invite_service.set_girl_profile(
        db,
        token=token,
        girl_name=girl_name,
        girl_age=girl_age,
        girl_zodiac=girl_zodiac,
    )

    # Qiz endi quizga o'tadi (router/quiz.py: GET /i/{token})
    return RedirectResponse(url=f"/i/{token}", status_code=303)


# ---------- RESULT (User1 ko'radi) ----------
@router.get("/result/{token}", response_class=HTMLResponse)
def result(request: Request, token: str, db: Session = Depends(get_db)):
    inv = invite_service.get_invite_by_token_or_404(db, token)

    # ✅ Yangi: 2 ta blokli natija (romantika + ishonch/amal)
    profile = get_profile(inv.boy_zodiac, inv.girl_zodiac or "")

    # Burj mosligi (boy_zodiac + girl_zodiac)
    z = zodiac_compatibility(inv.boy_zodiac, inv.girl_zodiac or "")

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "invite": inv,  # oldingi "session" o'rniga "invite"
            "profile": profile,
            "zodiac": z,
        },
    )
