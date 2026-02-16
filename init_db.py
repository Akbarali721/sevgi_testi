# init_db.py
from app.db.database import engine
from app.db.models import Base
from app.db import models  # noqa: F401  (model'lar ro'yxatdan o'tsin)

def main():
    Base.metadata.create_all(bind=engine)
    print("✅ DB tables created successfully")

if __name__ == "__main__":
    main()
