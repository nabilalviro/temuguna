from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL database SQLite (akan membuat file sql_app.db di root folder backend)
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# Untuk SQLite, connect_args diperlukan agar sesi database bisa bekerja dengan banyak thread
# (penting untuk FastAPI yang asynchronous)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# SesionLocal adalah class yang akan digunakan untuk membuat sesi database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base akan digunakan untuk membuat model ORM SQLAlchemy
Base = declarative_base()

# Dependency untuk mendapatkan sesi database (akan digunakan di endpoint FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()