from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime

from api.db import get_cursor
from api.dependencies import get_db, get_current_user, require_lecturer

router = APIRouter(tags=["Calendar"])


class CreateEventRequest(BaseModel):
    title:       str
    description: str | None = None
    event_date:  datetime


@router.get("/courses/{course_code}/events")
def get_events_for_course(
    course_code: str,
    conn=Depends(get_db),
    user=Depends(get_current_user)
):
    cur = get_cursor(conn)
    cur.execute("SELECT 1 FROM Course WHERE course_code = %s", (course_code,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Course not found.")

    cur.execute("""
        SELECT ev_id, course_code, title, description, event_date
        FROM Calendar_Event
        WHERE course_code = %s
        ORDER BY event_date
    """, (course_code,))
    return [dict(r) for r in cur.fetchall()]


@router.get("/students/{student_id}/events")
def get_events_for_student(
    student_id: int,
    date: str,          # query param: ?date=YYYY-MM-DD
    conn=Depends(get_db),
    user=Depends(get_current_user)
):
    cur = get_cursor(conn)
    cur.execute("SELECT 1 FROM Student WHERE acc_id = %s", (student_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Student not found.")

    cur.execute("""
        SELECT ce.ev_id, ce.course_code, c.course_name,
               ce.title, ce.description, ce.event_date
        FROM Calendar_Event ce
        JOIN Enroll e ON ce.course_code = e.course_code
        JOIN Course c ON ce.course_code = c.course_code
        WHERE e.student_id = %s
          AND DATE(ce.event_date) = %s
        ORDER BY ce.event_date
    """, (student_id, date))
    return [dict(r) for r in cur.fetchall()]


@router.post("/courses/{course_code}/events", status_code=201)
def create_event(
    course_code: str,
    body: CreateEventRequest,
    conn=Depends(get_db),
    user=Depends(require_lecturer)
):
    cur = get_cursor(conn)

    cur.execute("SELECT 1 FROM Course WHERE course_code = %s", (course_code,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Course not found.")

    # Verify this lecturer teaches this course
    cur.execute("""
        SELECT 1 FROM Teach WHERE lecturer_id = %s AND course_code = %s
    """, (user["acc_id"], course_code))
    if not cur.fetchone():
        raise HTTPException(status_code=403,
                            detail="You are not the lecturer for this course.")

    cur.execute("""
        INSERT INTO Calendar_Event (course_code, title, description, event_date)
        VALUES (%s, %s, %s, %s)
        RETURNING ev_id
    """, (course_code, body.title, body.description, body.event_date))

    ev_id = cur.fetchone()["ev_id"]
    return {"message": "Event created.", "ev_id": ev_id}
