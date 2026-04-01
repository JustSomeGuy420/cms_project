from fastapi import APIRouter, Depends

from api.db import get_cursor
from api.dependencies import get_db, get_current_user
from api import cache

router = APIRouter(prefix="/reports", tags=["Reports"])

# Reports are expensive aggregation queries — cache for 10 minutes
REPORT_TTL = 600


@router.get("/courses-50-plus")
def courses_50_plus(conn=Depends(get_db), user=Depends(get_current_user)):
    cached = cache.get("reports:courses_50_plus")
    if cached:
        return cached

    cur = get_cursor(conn)
    cur.execute("SELECT * FROM view_courses_50_plus_students")
    result = [dict(r) for r in cur.fetchall()]

    cache.set("reports:courses_50_plus", result, ttl=REPORT_TTL)
    return result


@router.get("/students-5-plus")
def students_5_plus(conn=Depends(get_db), user=Depends(get_current_user)):
    cached = cache.get("reports:students_5_plus")
    if cached:
        return cached

    cur = get_cursor(conn)
    cur.execute("SELECT * FROM view_students_5_plus_courses")
    result = [dict(r) for r in cur.fetchall()]

    cache.set("reports:students_5_plus", result, ttl=REPORT_TTL)
    return result


@router.get("/lecturers-3-plus")
def lecturers_3_plus(conn=Depends(get_db), user=Depends(get_current_user)):
    cached = cache.get("reports:lecturers_3_plus")
    if cached:
        return cached

    cur = get_cursor(conn)
    cur.execute("SELECT * FROM view_lecturers_3_plus_courses")
    result = [dict(r) for r in cur.fetchall()]

    cache.set("reports:lecturers_3_plus", result, ttl=REPORT_TTL)
    return result


@router.get("/top-10-courses")
def top_10_courses(conn=Depends(get_db), user=Depends(get_current_user)):
    cached = cache.get("reports:top_10_courses")
    if cached:
        return cached

    cur = get_cursor(conn)
    cur.execute("SELECT * FROM view_top_10_enrolled_courses")
    result = [dict(r) for r in cur.fetchall()]

    cache.set("reports:top_10_courses", result, ttl=REPORT_TTL)
    return result


@router.get("/top-10-students")
def top_10_students(conn=Depends(get_db), user=Depends(get_current_user)):
    cached = cache.get("reports:top_10_students")
    if cached:
        return cached

    cur = get_cursor(conn)
    cur.execute("SELECT * FROM view_top_10_students_by_average")
    result = [dict(r) for r in cur.fetchall()]

    cache.set("reports:top_10_students", result, ttl=REPORT_TTL)
    return result
