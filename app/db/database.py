from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Cek apakah menggunakan SQLite
if "sqlite" in settings.DATABASE_URL:
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        settings.DATABASE_URL, connect_args=connect_args
    )
else:
    engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()