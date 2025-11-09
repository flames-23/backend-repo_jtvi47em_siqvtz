import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import db, create_document, get_documents

app = FastAPI(title="BSSM Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Startup bootstrap: create demo accounts if empty ---
@app.on_event("startup")
def bootstrap_accounts():
    if db is None:
        return
    try:
        if db["account"].count_documents({}) == 0:
            db["account"].insert_many([
                {"nik": "1111111111111111", "name": "Warga Demo", "role": "warga", "password": "demo123", "active": True},
                {"nik": "2222222222222222", "name": "Pengurus Demo", "role": "pengurus", "password": "demo123", "active": True},
                {"nik": "9999999999999999", "name": "Admin Demo", "role": "admin", "password": "demo123", "active": True},
            ])
            db["account"].create_index("nik", unique=True)
    except Exception:
        # silent fail in bootstrap to avoid breaking server
        pass

class LoginRequest(BaseModel):
    nik: str
    password: str

class LoginResponse(BaseModel):
    nik: str
    name: str
    role: str
    token: str

@app.get("/")
def read_root():
    return {"message": "BSSM Backend Running"}

@app.get("/test")
def test_database():
    status = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "collections": []
    }
    try:
        if db is not None:
            status["database"] = "✅ Connected"
            status["collections"] = db.list_collection_names()
    except Exception as e:
        status["database"] = f"⚠️ {str(e)[:80]}"
    return status

@app.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    # Simple credential check from DB (Account collection)
    try:
        user = db["account"].find_one({"nik": payload.nik, "password": payload.password, "active": True})
    except Exception:
        raise HTTPException(status_code=500, detail="Database connection error")

    if not user:
        raise HTTPException(status_code=401, detail="NIK atau kata sandi salah")

    token = f"demo-{user['_id']}"  # demo token
    return {"nik": user["nik"], "name": user["name"], "role": user["role"], "token": token}

class TransactionIn(BaseModel):
    date: str
    customer: str
    material: str
    weight: float
    price: float

class TransactionOut(TransactionIn):
    total: float

@app.post("/transactions", response_model=TransactionOut)
def create_transaction(data: TransactionIn):
    total = float(data.weight) * float(data.price)
    doc = data.dict()
    doc["total"] = total
    _id = create_document("transaction", doc)
    doc["_id"] = _id
    return doc

@app.get("/transactions")
def list_transactions(limit: Optional[int] = 200):
    docs = get_documents("transaction", {}, limit)
    # Normalize
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs
