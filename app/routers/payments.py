from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import crud

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/pay/{session_id}", response_class=HTMLResponse)
def pay_page(request: Request, session_id: int, db: Session = Depends(get_db)):
    s = crud.get_session(db, session_id)
    if not s:
        return templates.TemplateResponse("success.html", {"request": request, "message": "Session topilmadi"})

    return templates.TemplateResponse("pay.html", {"request": request, "session": s, "amount": 14999})


@router.post("/pay/{session_id}")
def pay_submit(request: Request, session_id: int, db: Session = Depends(get_db)):
    p = crud.create_payment(db, session_id=session_id, amount=14999, provider="demo")
    crud.mark_payment_paid(db, p.id)
    return RedirectResponse(url=f"/girl/{session_id}", status_code=303)
