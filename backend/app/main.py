from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from . import models, schemas, database
import re # Import regex di main.py juga untuk helper

# Inisialisasi FastAPI
app = FastAPI()

# Konfigurasi CORS (PENTING untuk mengizinkan frontend berkomunikasi dengan backend)
origins = [
    "http://localhost",         # Sering dibutuhkan, karena browser mungkin menggunakan ini
    "http://localhost:8000",
    "http://127.0.0.1:8000",    # IP eksplisit untuk server FastAPI
    "http://localhost:5500",    # Port Live Server, menggunakan nama host
    "http://127.0.0.1:5500",    # Port Live Server, menggunakan IP
    "https://temuguna.vercel.app/",  # Ganti dengan URL frontend Anda jika sudah deploy
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Regex yang sama dengan di schemas.py untuk helper
EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.com$")
PHONE_NUMBER_REGEX = re.compile(r"^(?:\+62|08)[1-9][0-9]{7,11}$")

# --- Database Initialization ---
@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=database.engine)
    print("Database tables created/checked.")

# --- Endpoint Pendaftaran Pengguna ---
@app.post("/register/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_email = None
    db_phone = None

    if EMAIL_REGEX.fullmatch(user.identifier):
        db_email = user.identifier
        # Cek apakah email sudah terdaftar
        existing_user = db.query(models.User).filter(models.User.email == db_email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email sudah terdaftar"
            )
    elif PHONE_NUMBER_REGEX.fullmatch(user.identifier):
        db_phone = user.identifier
        # Cek apakah nomor HP sudah terdaftar
        existing_user = db.query(models.User).filter(models.User.phone_number == db_phone).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nomor HP sudah terdaftar"
            )
    else:
        # Ini seharusnya sudah divalidasi oleh Pydantic di schemas.py,
        # tapi sebagai fallback atau untuk pesan error yang lebih umum
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Identifier tidak valid (harus email .com atau nomor HP Indonesia)"
        )


    hashed_password = get_password_hash(user.password)

    new_user = models.User(
        email=db_email,          # Akan null jika daftar pakai nomor HP
        phone_number=db_phone,    # Akan null jika daftar pakai email
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.get("/")
def read_root():
    return {"message": "Selamat datang di API TemuGuna!"}

@app.get("/users/", response_model=list[schemas.UserResponse]) # Akan mengembalikan list UserResponse
def get_all_users(db: Session = Depends(database.get_db)):
    users = db.query(models.User).all() # Mengambil semua user dari database
    return users