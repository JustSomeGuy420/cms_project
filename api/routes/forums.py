from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.db import get_cursor
from api.dependencies import get_db, get_current_user, require_lecturer

router = APIRouter(tags=["Forums"])


# ── Request models ────────────────────────────────────────────

class CreateForumRequest(BaseModel):
    title: str


class CreateThreadRequest(BaseModel):
    title:   str
    content: str


class ReplyRequest(BaseModel):
    title:   str
    content: str


# ── Forums ────────────────────────────────────────────────────

@router.get("/courses/{course_code}/forums")
def get_forums(
    course_code: str,
    conn=Depends(get_db),
    user=Depends(get_current_user)
):
    cur = get_cursor(conn)
    cur.execute("SELECT 1 FROM Course WHERE course_code = %s", (course_code,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Course not found.")

    cur.execute("""
        SELECT df.df_id, df.course_code, df.title, df.created_at,
               a.name AS created_by_name, a.acc_id AS created_by_id
        FROM Discussion_Forum df
        JOIN Account a ON df.created_by = a.acc_id
        WHERE df.course_code = %s
        ORDER BY df.created_at
    """, (course_code,))
    return [dict(r) for r in cur.fetchall()]


@router.post("/courses/{course_code}/forums", status_code=status.HTTP_201_CREATED)
def create_forum(
    course_code: str,
    body: CreateForumRequest,
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
        INSERT INTO Discussion_Forum (course_code, created_by, title, created_at)
        VALUES (%s, %s, %s, NOW())
        RETURNING df_id
    """, (course_code, user["acc_id"], body.title))

    df_id = cur.fetchone()["df_id"]
    return {"message": "Forum created.", "df_id": df_id}


# ── Threads ───────────────────────────────────────────────────

@router.get("/forums/{forum_id}/threads")
def get_threads(
    forum_id: int,
    conn=Depends(get_db),
    user=Depends(get_current_user)
):
    cur = get_cursor(conn)
    cur.execute("SELECT 1 FROM Discussion_Forum WHERE df_id = %s", (forum_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Forum not found.")

    cur.execute("""
        SELECT
            dt.dt_id,
            dt.title,
            dt.content,
            dt.created_at,
            a.acc_id  AS author_id,
            a.name    AS author_name,
            rt.parent_id
        FROM Discussion_Thread dt
        JOIN DDA d         ON dt.dt_id    = d.thread_id
        JOIN Account a     ON d.account_id = a.acc_id
        LEFT JOIN Reply_To rt ON dt.dt_id  = rt.child_id
        WHERE d.forum_id = %s
        ORDER BY dt.created_at
    """, (forum_id,))
    return [dict(r) for r in cur.fetchall()]


@router.post("/forums/{forum_id}/threads", status_code=status.HTTP_201_CREATED)
def create_thread(
    forum_id: int,
    body: CreateThreadRequest,
    conn=Depends(get_db),
    user=Depends(get_current_user)
):
    cur = get_cursor(conn)
    cur.execute("SELECT 1 FROM Discussion_Forum WHERE df_id = %s", (forum_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Forum not found.")

    # Insert the thread
    cur.execute("""
        INSERT INTO Discussion_Thread (title, content, created_at)
        VALUES (%s, %s, NOW())
        RETURNING dt_id
    """, (body.title, body.content))
    dt_id = cur.fetchone()["dt_id"]

    # Link thread to forum and author via DDA
    cur.execute("""
        INSERT INTO DDA (account_id, thread_id, forum_id)
        VALUES (%s, %s, %s)
    """, (user["acc_id"], dt_id, forum_id))

    return {"message": "Thread created.", "dt_id": dt_id}


@router.post("/threads/{thread_id}/reply", status_code=status.HTTP_201_CREATED)
def reply_to_thread(
    thread_id: int,
    body: ReplyRequest,
    conn=Depends(get_db),
    user=Depends(get_current_user)
):
    cur = get_cursor(conn)

    # Confirm parent thread exists and find its forum
    cur.execute("""
        SELECT d.forum_id
        FROM Discussion_Thread dt
        JOIN DDA d ON dt.dt_id = d.thread_id
        WHERE dt.dt_id = %s
        LIMIT 1
    """, (thread_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Thread not found.")

    forum_id = row["forum_id"]

    # Insert the reply thread
    cur.execute("""
        INSERT INTO Discussion_Thread (title, content, created_at)
        VALUES (%s, %s, NOW())
        RETURNING dt_id
    """, (body.title, body.content))
    child_id = cur.fetchone()["dt_id"]

    # Link to forum and author via DDA
    cur.execute("""
        INSERT INTO DDA (account_id, thread_id, forum_id)
        VALUES (%s, %s, %s)
    """, (user["acc_id"], child_id, forum_id))

    # Record the parent-child relationship
    cur.execute("""
        INSERT INTO Reply_To (child_id, parent_id) VALUES (%s, %s)
    """, (child_id, thread_id))

    return {"message": "Reply posted.", "dt_id": child_id, "parent_id": thread_id}
