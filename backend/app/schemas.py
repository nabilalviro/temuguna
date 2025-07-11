from pydantic import BaseModel, EmailStr, field_validator
import re
from typing import Optional, ClassVar # <-- TAMBAHKAN ClassVar di sini

class UserCreate(BaseModel):
    identifier: str # Ini bisa email atau nomor HP
    password: str

    # Regex untuk nomor HP Indonesia (mulai dengan 08 atau +628, 9-13 digit setelah 08/+628)
    PHONE_NUMBER_REGEX: ClassVar[re.Pattern] = re.compile(r"^(?:\+62|08)[1-9][0-9]{7,11}$") # <-- Tambahkan : ClassVar[re.Pattern]

    # Regex untuk email (tetap hanya .com)
    EMAIL_REGEX: ClassVar[re.Pattern] = re.compile(r"^[^\s@]+@[^\s@]+\.com$") # <-- Tambahkan : ClassVar[re.Pattern]


    @field_validator('identifier')
    @classmethod
    def validate_identifier_type(cls, v: str) -> str:
        is_email = cls.EMAIL_REGEX.fullmatch(v)
        is_phone = cls.PHONE_NUMBER_REGEX.fullmatch(v)

        if not is_email and not is_phone:
            raise ValueError('Identifier harus berupa email (.com) atau nomor HP Indonesia (08/ +628...) yang valid.')
        return v

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password minimal 8 karakter')
        if not re.search(r"[A-Z]", v):
            raise ValueError('Password harus mengandung setidaknya satu huruf kapital')
        if not re.search(r"[a-z]", v):
            raise ValueError('Password harus mengandung setidaknya satu huruf kecil')
        if not re.search(r"\d", v):
            raise ValueError('Password harus mengandung setidaknya satu angka')
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", v): # Contoh karakter spesial
            raise ValueError('Password harus mengandung setidaknya satu karakter spesial')
        return v

class UserResponse(BaseModel):
    id: int
    email: Optional[EmailStr] # Bisa null sekarang
    phone_number: Optional[str] # Bisa null sekarang
    is_active: bool

    class Config:
        from_attributes = True

class UserListResponse(BaseModel): # Opsional, jika ingin membungkus daftar
    users: list[UserResponse]