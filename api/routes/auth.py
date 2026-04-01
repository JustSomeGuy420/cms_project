from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from psycopg2.errors import UniqueViolation

from api.db import get_cursor
from api.auth import hash_password, verify_password, create_token
from api.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


# ── Request models ────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name:       str
    email:      EmailStr
    password:   str
    role:       str           # "student" | "lecturer" | "admin"
    # Student fields
    student_no: str | None = None
    program:    str | None = None
    year:       int | None = None
    # Lecturer fields
    staff_id:   str | None = None
    department: str | None = None


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


# ── Endpoints ─────────────────────────────────────────────────

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, conn=Depends(get_db)):
    if body.role not in ("student", "lecturer", "admin"):
        raise HTTPException(status_code=400, detail="Role must be student, lecturer, or admin.")

    cur = get_cursor(conn)

    # Insert base account
    try:
        cur.execute("""
            INSERT INTO Account (name, email, password, status)
            VALUES (%s, %s, %s, 'active')
            RETURNING acc_id
        """, (body.name, body.email, hash_password(body.password)))
    except UniqueViolation:
        raise HTTPException(status_code=409, detail="Email already registered.")

    acc_id = cur.fetchone()["acc_id"]

    # Insert role-specific record
    if body.role == "student":
        if not all([body.student_no, body.program, body.year]):
            raise HTTPException(status_code=400,
                                detail="student_no, program, and year are required for students.")
        cur.execute("""
            INSERT INTO Student (acc_id, student_no, program, year)
            VALUES (%s, %s, %s, %s)
        """, (acc_id, body.student_no, body.program, body.year))

    elif body.role == "lecturer":
        if not all([body.staff_id, body.department]):
            raise HTTPException(status_code=400,
                                detail="staff_id and department are required for lecturers.")
        cur.execute("""
            INSERT INTO Lecturer (acc_id, staff_id, department)
            VALUES (%s, %s, %s)
        """, (acc_id, body.staff_id, body.department))

    elif body.role == "admin":
        cur.execute("INSERT INTO Admin (acc_id) VALUES (%s)", (acc_id,))

    return {"message": "Account created successfully.", "acc_id": acc_id, "role": body.role}


@router.post("/login")
def login(body: LoginRequest, conn=Depends(get_db)):
    cur = get_cursor(conn)

    # Fetch account and determine role in one query
    cur.execute("""
        SELECT
            a.acc_id,
            a.password,
            a.status,
            CASE
                WHEN s.acc_id  IS NOT NULL THEN 'student'
                WHEN l.acc_id  IS NOT NULL THEN 'lecturer'
                WHEN ad.acc_id IS NOT NULL THEN 'admin'
            END AS role
        FROM Account a
        LEFT JOIN Student  s  ON a.acc_id = s.acc_id
        LEFT JOIN Lecturer l  ON a.acc_id = l.acc_id
        LEFT JOIN Admin    ad ON a.acc_id = ad.acc_id
        WHERE a.email = %s
    """, (body.email,))

    account = cur.fetchone()

    if not account:
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    if account["status"] != "active":
        raise HTTPException(status_code=403, detail="Account is inactive.")

    if not verify_password(body.password, account["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    token = create_token(account["acc_id"], account["role"])

    return {
        "access_token": token,
        "token_type":   "bearer",
        "acc_id":       account["acc_id"],
        "role":         account["role"],
    }
