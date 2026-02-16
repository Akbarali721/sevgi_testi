# app/routers/quiz.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services import quiz_service
from app.services.invite_service import open_invite, get_invite_by_token_or_404

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# ✅ PROD domen (Render)
BASE_URL = "https://sevgi-testi-7jd2.onrender.com"


@router.get("/i/{token}", response_class=HTMLResponse)
def quiz_page(request: Request, token: str, db: Session = Depends(get_db)):
    inv = open_invite(db, token)

    questions = quiz_service.get_quiz_questions(db)
    print("QUESTIONS COUNT =", len(questions))

    return templates.TemplateResponse(
        "quiz.html",
        {"request": request, "invite": inv, "questions": questions},
    )


@router.post("/i/{token}")
async def quiz_submit(request: Request, token: str, db: Session = Depends(get_db)):
    form = await request.form()

    try:
        quiz_service.submit_quiz_by_token(db, token, form)
    except Exception as e:
        # xatoni muloyim qilib qaytaramiz
        inv = get_invite_by_token_or_404(db, token)
        questions = quiz_service.get_quiz_questions(db)
        return templates.TemplateResponse(
            "quiz.html",
            {"request": request, "invite": inv, "questions": questions, "error": str(e)},
        )

    # ✅ Natija faqat yigitga boradi — shuning uchun link to‘liq bo‘lsin
    return RedirectResponse(
        url=f"{BASE_URL}/result/{token}",
        status_code=303,
    )
