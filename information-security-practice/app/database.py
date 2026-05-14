from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm import Session

DATABASE_URL = "sqlite:///./data/university.db"

class Base(DeclarativeBase):
    pass

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db():
    """Генератор сесій бази даних для Dependency Injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
