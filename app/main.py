from fastapi import FastAPI
from pathlib import Path
from fastapi.staticfiles import StaticFiles

from app.routers.pages import router as pages_router
from app.routers.payments import router as payments_router
from app.routers.quiz import router as quiz_router
from app.routers import api
app = FastAPI(title="Sevgi Testi")

BASE_DIR = Path(__file__).resolve().parent  # app/
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(pages_router)
app.include_router(payments_router)
app.include_router(quiz_router)
app.include_router(api.router)