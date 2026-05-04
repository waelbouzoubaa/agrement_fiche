import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agrement.db")
UPLOADS_DIR = os.getenv("UPLOADS_DIR", "./uploads")

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    from lib import models  # noqa: F401
    from sqlalchemy import text
    Base.metadata.create_all(engine)
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    # Migrations : ajout des colonnes manquantes
    with engine.connect() as conn:
        migrations = [
            ("agrements",  "datasheet_url"),
            ("products",   "datasheet_url"),
        ]
        for table, col in migrations:
            try:
                if "postgresql" in DATABASE_URL:
                    conn.execute(text(
                        f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} VARCHAR(500)"
                    ))
                else:
                    conn.execute(text(
                        f"ALTER TABLE {table} ADD COLUMN {col} VARCHAR(500)"
                    ))
                conn.commit()
            except Exception:
                pass  # colonne déjà présente
