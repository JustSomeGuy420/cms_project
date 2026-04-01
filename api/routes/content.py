from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.db import get_cursor
from api.dependencies import get_db, get_current_user, require_lecturer

router = APIRouter(tags=["Course Content"])

VALID_ITEM_TYPES = {"link", "file", "video", "document", "slide"}


# ── Request models ────────────────────────────────────────────

class CreateSectionRequest(BaseModel):
    sec_no: int
    title:  str


class CreateItemRequest(BaseModel):
    title:       str
    type:        str
    content_url: str


# ── Endpoints ─────────────────────────────────────────────────

@router.get("/courses/{course_code}/content")
def get_course_content(
    course_code: str,
    conn=Depends(get_db),
    user=Depends(get_current_user)
):
    cur = get_cursor(conn)
    cur.execute("SELECT 1 FROM Course WHERE course_code = %s", (course_code,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Course not found.")

    cur.execute("""
        SELECT
            s.sec_no,
            s.title         AS section_title,
            si.item_id,
            si.title        AS item_title,
            si.type,
            si.content_url,
            si.created_at
        FROM Section s
        LEFT JOIN Section_Item si
               ON s.sec_no      = si.sec_no
              AND s.course_code = si.course_code
        WHERE s.course_code = %s
        ORDER BY s.sec_no, si.item_id
    """, (course_code,))

    # Group items under their sections
    sections: dict = {}
    for row in cur.fetchall():
        row = dict(row)
        sec_no = row["sec_no"]
        if sec_no not in sections:
            sections[sec_no] = {
                "sec_no":        sec_no,
                "section_title": row["section_title"],
                "items":         []
            }
        if row["item_id"] is not None:
            sections[sec_no]["items"].append({
                "item_id":     row["item_id"],
                "title":       row["item_title"],
                "type":        row["type"],
                "content_url": row["content_url"],
                "created_at":  str(row["created_at"]),
            })

    return list(sections.values())


@router.post("/courses/{course_code}/sections", status_code=status.HTTP_201_CREATED)
def create_section(
    course_code: str,
    body: CreateSectionRequest,
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
        SELECT 1 FROM Section WHERE sec_no = %s AND course_code = %s
    """, (body.sec_no, course_code))
    if cur.fetchone():
        raise HTTPException(status_code=409, detail="Section number already exists for this course.")

    cur.execute("""
        INSERT INTO Section (sec_no, course_code, title)
        VALUES (%s, %s, %s)
    """, (body.sec_no, course_code, body.title))

    return {"message": "Section created.", "sec_no": body.sec_no, "course_code": course_code}


@router.post("/sections/{sec_no}/{course_code}/items", status_code=status.HTTP_201_CREATED)
def create_section_item(
    sec_no: int,
    course_code: str,
    body: CreateItemRequest,
    conn=Depends(get_db),
    user=Depends(require_lecturer)
):
    if body.type not in VALID_ITEM_TYPES:
        raise HTTPException(status_code=400,
                            detail=f"type must be one of: {', '.join(VALID_ITEM_TYPES)}")

    cur = get_cursor(conn)

    cur.execute("""
        SELECT 1 FROM Section WHERE sec_no = %s AND course_code = %s
    """, (sec_no, course_code))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Section not found.")

    cur.execute("""
        SELECT 1 FROM Teach WHERE lecturer_id = %s AND course_code = %s
    """, (user["acc_id"], course_code))
    if not cur.fetchone():
        raise HTTPException(status_code=403,
                            detail="You are not the lecturer for this course.")

    cur.execute("""
        INSERT INTO Section_Item (sec_no, course_code, title, type, content_url, created_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        RETURNING item_id
    """, (sec_no, course_code, body.title, body.type, body.content_url))

    item_id = cur.fetchone()["item_id"]
    return {"message": "Item added.", "item_id": item_id}
