from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

import shutil

if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/smartexam.db"
    orig_db = os.path.join(os.path.dirname(__file__), "..", "..", "smartexam.db")
    if os.path.exists(orig_db) and not os.path.exists(DB_PATH):
        try:
            shutil.copy2(orig_db, DB_PATH)
        except Exception as e:
            print(f"Note copying DB to /tmp: {e}")
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "smartexam.db")

DATABASE_URL = f"sqlite:///{os.path.abspath(DB_PATH)}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
