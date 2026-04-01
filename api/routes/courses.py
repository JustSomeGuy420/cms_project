from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.db import get_cursor
from api.dependencies import get_db, get_current_user, require_admin, require_student
from api import cache

router = APIRouter(prefix="/courses", tags=["Courses"])


# ── Request models ────────────────────────────────────────────

class CreateCourseRequest(BaseModel):
    course_code: str
    course_name: str
    description: str | None = None


class AssignLecturerRequest(BaseModel):
    lecturer_id: int


class EnrollRequest(BaseModel):
    student_id: int


# ── Courses ───────────────────────────────────────────────────

@router.get("")
def get_all_courses(
    conn=Depends(get_db),
    user=Depends(get_current_user)
):
    cached = cache.get("courses:all")
    if cached:
        return cached

    cur = get_cursor(conn)
    cur.execute("SELECT course_code, course_name, description FROM Course ORDER BY course_code")
    courses = [dict(r) for r in cur.fetchall()]

    cache.set("courses:all", courses)
    return courses


@router.post("", status_code=status.HTTP_201_CREATED)
def create_course(
    body: CreateCourseRequest,
    conn=Depends(get_db),
    user=Depends(require_admin)
):
    cur = get_cursor(conn)
    cur.execute("SELECT 1 FROM Course WHERE course_code = %s", (body.course_code,))
    if cur.fetchone():
        raise HTTPException(status_code=409, detail="Course code already exists.")

    cur.execute("""
        INSERT INTO Course (course_code, course_name, description)
        VALUES (%s, %s, %s)
    """, (body.course_code, body.course_name, body.description))

    cache.invalidate("courses:all")
    return {"message": "Course created.", "course_code": body.course_code}


@router.get("/student/{student_id}")
def get_courses_for_student(
    student_id: int,
    conn=Depends(get_db),
    user=Depends(get_current_user)
):
    cur = get_cursor(conn)
    cur.execute("SELECT 1 FROM Student WHERE acc_id = %s", (student_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Student not found.")

    cur.execute("""
        SELECT c.course_code, c.course_name, c.description,
               e.grade, e.date_enrolled
        FROM Course c
        JOIN Enroll e ON c.course_code = e.course_code
        WHERE e.student_id = %s
        ORDER BY e.date_enrolled DESC
    """, (student_id,))
    return [dict(r) for r in cur.fetchall()]


@router.get("/lecturer/{lecturer_id}")
def get_courses_for_lecturer(
    lecturer_id: int,
    conn=Depends(get_db),
    user=Depends(get_current_user)
):
    cur = get_cursor(conn)
    cur.execute("SELECT 1 FROM Lecturer WHERE acc_id = %s", (lecturer_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Lecturer not found.")

    cur.execute("""
        SELECT c.course_code, c.course_name, c.description
        FROM Course c
        JOIN Teach t ON c.course_code = t.course_code
        WHERE t.lecturer_id = %s
        ORDER BY c.course_code
    """, (lecturer_id,))
    return [dict(r) for r in cur.fetchall()]


@router.get("/{course_code}")
def get_course(
    course_code: str,
    conn=Depends(get_db),
    user=Depends(get_current_user)
):
    cur = get_cursor(conn)
    cur.execute("""
        SELECT c.course_code, c.course_name, c.description,
               a.name AS lecturer_name, a.acc_id AS lecturer_id
        FROM Course c
        LEFT JOIN Teach    t ON c.course_code  = t.course_code
        LEFT JOIN Lecturer l ON t.lecturer_id  = l.acc_id
        LEFT JOIN Account  a ON l.acc_id       = a.acc_id
        WHERE c.course_code = %s
    """, (course_code,))
    course = cur.fetchone()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
    return dict(course)


# ── Membership ────────────────────────────────────────────────

@router.post("/{course_code}/assign-lecturer")
def assign_lecturer(
    course_code: str,
    body: AssignLecturerRequest,
    conn=Depends(get_db),
    user=Depends(require_admin)
):
    cur = get_cursor(conn)

    cur.execute("SELECT 1 FROM Course WHERE course_code = %s", (course_code,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Course not found.")

    cur.execute("SELECT 1 FROM Lecturer WHERE acc_id = %s", (body.lecturer_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Lecturer not found.")

    # Enforce: only one lecturer per course
    cur.execute("SELECT 1 FROM Teach WHERE course_code = %s", (course_code,))
    if cur.fetchone():
        raise HTTPException(status_code=409,
                            detail="Course already has a lecturer assigned.")

    # Enforce: lecturer teaches at most 5 courses
    cur.execute("SELECT COUNT(*) AS cnt FROM Teach WHERE lecturer_id = %s", (body.lecturer_id,))
    if cur.fetchone()["cnt"] >= 5:
        raise HTTPException(status_code=409,
                            detail="Lecturer already teaches 5 courses (maximum).")

    cur.execute("INSERT INTO Teach (lecturer_id, course_code) VALUES (%s, %s)",
                (body.lecturer_id, course_code))
    return {"message": "Lecturer assigned to course."}


@router.post("/{course_code}/enroll")
def enroll_student(
    course_code: str,
    body: EnrollRequest,
    conn=Depends(get_db),
    user=Depends(get_current_user)
):
    cur = get_cursor(conn)

    cur.execute("SELECT 1 FROM Course WHERE course_code = %s", (course_code,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Course not found.")

    cur.execute("SELECT 1 FROM Student WHERE acc_id = %s", (body.student_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Student not found.")

    # Enforce: max 6 courses per student
    cur.execute("SELECT COUNT(*) AS cnt FROM Enroll WHERE student_id = %s", (body.student_id,))
    if cur.fetchone()["cnt"] >= 6:
        raise HTTPException(status_code=409,
                            detail="Student is already enrolled in 6 courses (maximum).")

    cur.execute("""
        SELECT 1 FROM Enroll WHERE student_id = %s AND course_code = %s
    """, (body.student_id, course_code))
    if cur.fetchone():
        raise HTTPException(status_code=409,
                            detail="Student is already enrolled in this course.")

    cur.execute("""
        INSERT INTO Enroll (student_id, course_code, date_enrolled)
        VALUES (%s, %s, CURRENT_DATE)
    """, (body.student_id, course_code))

    cache.invalidate(f"courses:{course_code}:members")
    return {"message": "Student enrolled successfully."}


@router.get("/{course_code}/members")
def get_course_members(
    course_code: str,
    conn=Depends(get_db),
    user=Depends(get_current_user)
):
    cache_key = f"courses:{course_code}:members"
    cached = cache.get(cache_key)
    if cached:
        return cached

    cur = get_cursor(conn)
    cur.execute("SELECT 1 FROM Course WHERE course_code = %s", (course_code,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Course not found.")

    cur.execute("""
        SELECT a.acc_id, a.name, a.email, s.student_no,
               s.program, s.year, e.grade, e.date_enrolled
        FROM Account a
        JOIN Student s ON a.acc_id   = s.acc_id
        JOIN Enroll  e ON s.acc_id   = e.student_id
        WHERE e.course_code = %s
        ORDER BY a.name
    """, (course_code,))

    members = [dict(r) for r in cur.fetchall()]
    cache.set(cache_key, members)
    return members
