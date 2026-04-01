from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime

from api.db import get_cursor
from api.dependencies import get_db, get_current_user, require_lecturer, require_student

router = APIRouter(tags=["Assignments"])


# ── Request models ────────────────────────────────────────────

class CreateAssignmentRequest(BaseModel):
    title:       str
    description: str | None = None
    due_date:    datetime


class SubmitAssignmentRequest(BaseModel):
    student_id: int
    file_url:   str


class GradeSubmissionRequest(BaseModel):
    grade:    float
    feedback: str | None = None


# ── Assignments ───────────────────────────────────────────────

@router.get("/courses/{course_code}/assignments")
def get_assignments(
    course_code: str,
    conn=Depends(get_db),
    user=Depends(get_current_user)
):
    cur = get_cursor(conn)
    cur.execute("SELECT 1 FROM Course WHERE course_code = %s", (course_code,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Course not found.")

    cur.execute("""
        SELECT ass_id, course_code, title, description, due_date
        FROM Assignment
        WHERE course_code = %s
        ORDER BY due_date
    """, (course_code,))
    return [dict(r) for r in cur.fetchall()]


@router.post("/courses/{course_code}/assignments", status_code=status.HTTP_201_CREATED)
def create_assignment(
    course_code: str,
    body: CreateAssignmentRequest,
    conn=Depends(get_db),
    user=Depends(require_lecturer)
):
    cur = get_cursor(conn)

    cur.execute("SELECT 1 FROM Course WHERE course_code = %s", (course_code,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Course not found.")

    cur.execute("""
        SELECT 1 FROM Teach WHERE lecturer_id = %s AND course_code = %s
    """, (user["acc_id"], course_code))
    if not cur.fetchone():
        raise HTTPException(status_code=403,
                            detail="You are not the lecturer for this course.")

    cur.execute("""
        INSERT INTO Assignment (course_code, title, description, due_date)
        VALUES (%s, %s, %s, %s)
        RETURNING ass_id
    """, (course_code, body.title, body.description, body.due_date))

    ass_id = cur.fetchone()["ass_id"]
    return {"message": "Assignment created.", "ass_id": ass_id}


# ── Submissions ───────────────────────────────────────────────

@router.post("/assignments/{ass_id}/submit", status_code=status.HTTP_201_CREATED)
def submit_assignment(
    ass_id: int,
    body: SubmitAssignmentRequest,
    conn=Depends(get_db),
    user=Depends(require_student)
):
    cur = get_cursor(conn)

    # Confirm assignment exists and get its course
    cur.execute("SELECT course_code FROM Assignment WHERE ass_id = %s", (ass_id,))
    assignment = cur.fetchone()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")

    course_code = assignment["course_code"]

    # Confirm student is enrolled in that course
    cur.execute("""
        SELECT 1 FROM Enroll WHERE student_id = %s AND course_code = %s
    """, (body.student_id, course_code))
    if not cur.fetchone():
        raise HTTPException(status_code=403,
                            detail="Student is not enrolled in this course.")

    # Insert submission
    cur.execute("""
        INSERT INTO Submission (submitted_at, file_url)
        VALUES (NOW(), %s)
        RETURNING sub_id
    """, (body.file_url,))
    sub_id = cur.fetchone()["sub_id"]

    # Link via SSA
    cur.execute("""
        INSERT INTO SSA (student_id, submission_id, assignment_id)
        VALUES (%s, %s, %s)
    """, (body.student_id, sub_id, ass_id))

    return {"message": "Assignment submitted.", "sub_id": sub_id}


@router.put("/submissions/{sub_id}/grade")
def grade_submission(
    sub_id: int,
    body: GradeSubmissionRequest,
    conn=Depends(get_db),
    user=Depends(require_lecturer)
):
    if not (0 <= body.grade <= 100):
        raise HTTPException(status_code=400, detail="Grade must be between 0 and 100.")

    cur = get_cursor(conn)

    # Confirm submission exists and get linked student + course
    cur.execute("""
        SELECT ssa.student_id, a.course_code
        FROM SSA ssa
        JOIN Assignment a ON ssa.assignment_id = a.ass_id
        WHERE ssa.submission_id = %s
    """, (sub_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Submission not found.")

    student_id  = row["student_id"]
    course_code = row["course_code"]

    # Confirm this lecturer teaches that course
    cur.execute("""
        SELECT 1 FROM Teach WHERE lecturer_id = %s AND course_code = %s
    """, (user["acc_id"], course_code))
    if not cur.fetchone():
        raise HTTPException(status_code=403,
                            detail="You are not the lecturer for this course.")

    # Grade the submission
    cur.execute("""
        UPDATE Submission SET grade = %s, feedback = %s WHERE sub_id = %s
    """, (body.grade, body.feedback, sub_id))

    # Recalculate and update the student's overall grade for this course
    # Uses the average of all graded submissions for this student in this course
    cur.execute("""
        UPDATE Enroll SET grade = (
            SELECT ROUND(AVG(sub.grade)::NUMERIC, 2)
            FROM SSA ssa
            JOIN Submission sub ON ssa.submission_id = sub.sub_id
            JOIN Assignment  a  ON ssa.assignment_id = a.ass_id
            WHERE ssa.student_id  = %s
              AND a.course_code   = %s
              AND sub.grade IS NOT NULL
        )
        WHERE student_id = %s AND course_code = %s
    """, (student_id, course_code, student_id, course_code))

    return {"message": "Submission graded and course average updated."}
