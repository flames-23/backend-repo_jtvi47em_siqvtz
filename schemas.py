"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Class name lowercased becomes collection name.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date

class Account(BaseModel):
    """Collection: account
    Basic user record for simple role-based access. In real apps, store password hashes.
    """
    nik: str = Field(..., description="Nomor Induk Kependudukan")
    name: str = Field(..., description="Nama lengkap")
    role: Literal['warga', 'pengurus', 'admin'] = Field('warga', description="Peran pengguna")
    password: str = Field(..., description="Kata sandi polos untuk demo")
    active: bool = Field(True, description="Status aktif")

class Transaction(BaseModel):
    """Collection: transaction
    Satu baris transaksi setoran bank sampah.
    """
    date: str = Field(..., description="Tanggal (YYYY-MM-DD)")
    customer: str = Field(..., description="Nama penyetor")
    material: str = Field(..., description="Jenis material")
    weight: float = Field(..., ge=0, description="Berat (kg)")
    price: float = Field(..., ge=0, description="Harga per kg")
    total: float = Field(..., ge=0, description="Nilai total (price * weight)")
