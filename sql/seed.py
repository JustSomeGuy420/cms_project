#!/usr/bin/env python3
"""
COMP3161 Final Project — Database Seed Script
Populates the database with all required data satisfying project constraints.

Constraints satisfied:
  - 100,000+ students
  - 200+ courses
  - Each student enrolled in 3–6 courses
  - Each course has at least 10 enrolled students
  - Each course taught by exactly 1 lecturer
  - Each lecturer teaches 1–5 courses
"""

import psycopg2
import psycopg2.extras
import random
import hashlib
from datetime import datetime, timedelta

# ============================================================
# CONFIGURATION — change only these values
# ============================================================

DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "cms_db",
    "user":     "cms_user",
    "password": "cms_password"
}

NUM_STUDENTS  = 100_000
NUM_LECTURERS = 60
NUM_COURSES   = 200
BATCH_SIZE    = 5_000

# ============================================================
# REFERENCE DATA
# ============================================================

PROGRAMS = [
    "Computer Science", "Information Technology", "Software Engineering",
    "Mathematics", "Physics", "Chemistry", "Biology",
    "Economics", "Business Administration", "History",
    "English Literature", "Psychology", "Electrical Engineering",
    "Mechanical Engineering", "Sociology"
]

DEPARTMENTS = [
    "Computer Science", "Mathematics", "Physics",
    "Chemistry", "Biology", "Economics",
    "Humanities", "Engineering"
]

# Maps department → course code prefix
DEPT_PREFIXES = {
    "Computer Science": "COMP",
    "Mathematics":      "MATH",
    "Physics":          "PHYS",
    "Chemistry":        "CHEM",
    "Biology":          "BIOL",
    "Economics":        "ECON",
    "Humanities":       "HUMN",
    "Engineering":      "ENGR"
}

COURSE_NAME_TEMPLATES = [
    "Introduction to {}", "Advanced {}", "Fundamentals of {}",
    "Applied {}", "Topics in {}", "Principles of {}",
    "Special Topics in {}", "{} Theory", "{} Practice",
    "Research Methods in {}"
]

SUBJECTS = [
    "Programming", "Data Structures", "Algorithms", "Database Systems",
    "Operating Systems", "Computer Networks", "Software Engineering",
    "Artificial Intelligence", "Machine Learning", "Calculus",
    "Linear Algebra", "Statistics", "Differential Equations",
    "Thermodynamics", "Quantum Mechanics", "Organic Chemistry",
    "Cell Biology", "Genetics", "Microeconomics", "Macroeconomics",
    "Literature", "Philosophy", "Psychology", "Sociology",
    "Circuit Analysis", "Signal Processing"
]

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael",
    "Linda", "William", "Barbara", "David", "Susan", "Richard", "Jessica",
    "Joseph", "Sarah", "Thomas", "Karen", "Charles", "Lisa", "Mark", "Nancy",
    "Donald", "Betty", "George", "Margaret", "Kenneth", "Sandra", "Steven",
    "Ashley", "Edward", "Dorothy", "Brian", "Kimberly", "Ronald", "Emily"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Wilson", "Martinez", "Anderson", "Taylor", "Thomas", "Moore",
    "Jackson", "Martin", "Lee", "Thompson", "White", "Harris", "Lewis",
    "Clark", "Robinson", "Walker", "Young", "Hall", "Allen", "King",
    "Wright", "Scott", "Green", "Adams", "Baker", "Nelson", "Carter", "Hill"
]

ITEM_TYPES     = ["link", "file", "video", "document", "slide"]
SECTION_TITLES = ["Introduction", "Core Concepts", "Advanced Topics",
                  "Practical Applications", "Review and Assessment"]

# ============================================================
# HELPERS
# ============================================================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def random_past_date(max_days_ago: int = 730) -> datetime:
    return datetime.now() - timedelta(days=random.randint(30, max_days_ago))

def random_future_date(max_days_ahead: int = 180) -> datetime:
    return datetime.now() + timedelta(days=random.randint(7, max_days_ahead))

def batch_execute(cur, query: str, data: list, batch_size: int = BATCH_SIZE) -> None:
    """Insert data in batches using execute_values. No RETURNING."""
    total = len(data)
    for i in range(0, total, batch_size):
        psycopg2.extras.execute_values(cur, query, data[i:i + batch_size])
        done = min(i + batch_size, total)
        print(f"    {done:,} / {total:,}", end="\r")
    print(f"    {total:,} / {total:,} ✓")

def batch_execute_returning(cur, query: str, data: list,
                            batch_size: int = BATCH_SIZE) -> list:
    """
    Insert data in batches using RETURNING to capture generated IDs.
    Returns a flat list of the returned values in insertion order.

    IMPORTANT: page_size must equal len(batch) so execute_values issues ONE
    SQL statement per batch. The default page_size=100 silently splits each
    batch into sub-pages, and cur.fetchall() only captures the last sub-page.
    """
    results = []
    total = len(data)
    for i in range(0, total, batch_size):
        batch = data[i:i + batch_size]
        psycopg2.extras.execute_values(cur, query, batch, page_size=len(batch))
        results.extend(row[0] for row in cur.fetchall())
        done = min(i + batch_size, total)
        print(f"    {done:,} / {total:,}", end="\r")
    print(f"    {total:,} / {total:,} ✓")
    return results

# ============================================================
# SEED FUNCTIONS
# ============================================================

def seed_admin(cur) -> int:
    """Create the one admin account."""
    cur.execute("""
        INSERT INTO Account (name, email, password, status)
        VALUES ('System Admin', 'admin@university.edu', %s, 'active')
        RETURNING acc_id
    """, (hash_password("admin123"),))
    admin_id = cur.fetchone()[0]
    cur.execute("INSERT INTO Admin (acc_id) VALUES (%s)", (admin_id,))
    print(f"    Admin created (acc_id={admin_id})")
    return admin_id


def seed_lecturers(cur) -> list[int]:
    """Create NUM_LECTURERS lecturer accounts and lecturer records."""
    account_rows = [
        (
            f"Lecturer {i}",
            f"lecturer{i}@university.edu",
            hash_password(f"lect{i}pass"),
            "active"
        )
        for i in range(1, NUM_LECTURERS + 1)
    ]

    lecturer_ids = batch_execute_returning(
        cur,
        "INSERT INTO Account (name, email, password, status) VALUES %s RETURNING acc_id",
        account_rows
    )

    lecturer_rows = [
        (acc_id, f"STAFF{i:04d}", random.choice(DEPARTMENTS))
        for i, acc_id in enumerate(lecturer_ids, start=1)
    ]
    batch_execute(cur,
        "INSERT INTO Lecturer (acc_id, staff_id, department) VALUES %s",
        lecturer_rows
    )
    return lecturer_ids


def seed_students(cur) -> list[int]:
    """Create NUM_STUDENTS student accounts and student records."""
    account_rows = [
        (
            f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            f"student{i}@university.edu",
            hash_password(f"stud{i}pass"),
            "active"
        )
        for i in range(1, NUM_STUDENTS + 1)
    ]

    student_ids = batch_execute_returning(
        cur,
        "INSERT INTO Account (name, email, password, status) VALUES %s RETURNING acc_id",
        account_rows
    )

    student_rows = [
        (acc_id, f"S{i:07d}", random.choice(PROGRAMS), random.randint(1, 4))
        for i, acc_id in enumerate(student_ids, start=1)
    ]
    batch_execute(cur,
        "INSERT INTO Student (acc_id, student_no, program, year) VALUES %s",
        student_rows
    )
    return student_ids


def seed_courses(cur) -> list[str]:
    """Create NUM_COURSES courses with realistic codes and names."""
    course_rows = []
    used_codes  = set()
    depts       = list(DEPT_PREFIXES.keys())

    for i in range(NUM_COURSES):
        dept   = depts[i % len(depts)]
        prefix = DEPT_PREFIXES[dept]
        level  = random.choice([1000, 2000, 3000, 4000])

        # Guarantee a unique code
        code = f"{prefix}{level + random.randint(1, 99)}"
        while code in used_codes:
            code = f"{prefix}{level + random.randint(1, 99)}"
        used_codes.add(code)

        subject  = SUBJECTS[i % len(SUBJECTS)]
        template = COURSE_NAME_TEMPLATES[i % len(COURSE_NAME_TEMPLATES)]
        name     = template.format(subject)
        course_rows.append((code, name, f"This course covers {name.lower()}."))

    batch_execute(cur,
        "INSERT INTO Course (course_code, course_name, description) VALUES %s",
        course_rows
    )
    return [row[0] for row in course_rows]


def seed_teach(cur, lecturer_ids: list[int], course_codes: list[str]) -> None:
    """
    Assign exactly one lecturer per course.
    Distribution: round-robin gives each lecturer 3–4 courses (within 1–5 limit).
    """
    shuffled_courses = course_codes.copy()
    random.shuffle(shuffled_courses)

    teach_rows = [
        (lecturer_ids[i % len(lecturer_ids)], course)
        for i, course in enumerate(shuffled_courses)
    ]
    batch_execute(cur,
        "INSERT INTO Teach (lecturer_id, course_code) VALUES %s",
        teach_rows
    )


def seed_enroll(cur, student_ids: list[int], course_codes: list[str]) -> None:
    """
    Enroll each student in 3–6 randomly chosen courses.
    With 100k students and 200 courses, every course will have thousands
    of students (well above the minimum of 10).
    """
    enroll_rows = []
    for sid in student_ids:
        num_courses = random.randint(3, 6)
        chosen      = random.sample(course_codes, num_courses)
        for code in chosen:
            # 80% of enrollments have a grade (rest are still in progress)
            grade = round(random.uniform(40, 100), 2) if random.random() < 0.80 else None
            date  = random_past_date(500).date()
            enroll_rows.append((sid, code, grade, date))

    print(f"    Total enrollments: {len(enroll_rows):,}")
    batch_execute(cur,
        "INSERT INTO Enroll (student_id, course_code, grade, date_enrolled) VALUES %s",
        enroll_rows
    )


def seed_sections(cur, course_codes: list[str]) -> list[tuple]:
    """Create 3–5 sections per course. Returns list of (sec_no, course_code)."""
    section_rows = []
    for code in course_codes:
        num_sections = random.randint(3, 5)
        for sec_no in range(1, num_sections + 1):
            title = SECTION_TITLES[sec_no - 1] if sec_no <= len(SECTION_TITLES) else f"Section {sec_no}"
            section_rows.append((sec_no, code, title))

    batch_execute(cur,
        "INSERT INTO Section (sec_no, course_code, title) VALUES %s",
        section_rows
    )
    return [(row[0], row[1]) for row in section_rows]


def seed_section_items(cur, sections: list[tuple]) -> None:
    """Create 2–5 items per section."""
    item_rows = []
    for sec_no, course_code in sections:
        for j in range(1, random.randint(2, 5) + 1):
            item_type = random.choice(ITEM_TYPES)
            item_rows.append((
                sec_no,
                course_code,
                f"{item_type.capitalize()} Resource {j}",
                item_type,
                f"https://university.edu/content/{course_code}/s{sec_no}/{j}",
                random_past_date(400)
            ))

    batch_execute(cur, """
        INSERT INTO Section_Item (sec_no, course_code, title, type, content_url, created_at)
        VALUES %s
    """, item_rows)


def seed_assignments(cur, course_codes: list[str]) -> list[tuple]:
    """
    Create 2–4 assignments per course.
    Returns list of (ass_id, course_code).
    """
    assignment_rows = [
        (
            code,
            f"Assignment {j}",
            f"Complete all tasks for Assignment {j} of {code}.",
            random_future_date(120)
        )
        for code in course_codes
        for j in range(1, random.randint(2, 4) + 1)
    ]

    ass_ids = batch_execute_returning(cur, """
        INSERT INTO Assignment (course_code, title, description, due_date)
        VALUES %s RETURNING ass_id
    """, assignment_rows)

    # Return (ass_id, course_code) pairs
    return list(zip(ass_ids, [row[0] for row in assignment_rows]))


def seed_submissions(cur, assignments: list[tuple]) -> None:
    """
    For each assignment, 20% of enrolled students submit.
    Inserts Submission rows and immediately captures sub_ids via RETURNING
    to correctly populate SSA.
    """
    # Build course_code → sorted list of student_ids from Enroll
    cur.execute("SELECT course_code, student_id FROM Enroll ORDER BY course_code")
    course_students: dict[str, list[int]] = {}
    for course_code, student_id in cur.fetchall():
        course_students.setdefault(course_code, []).append(student_id)

    # Build batches: each item is (submission_data, student_id, ass_id)
    sub_input_rows = []  # (submitted_at, file_url, grade, feedback)
    ssa_meta       = []  # (student_id, ass_id) — index matches sub_input_rows

    for ass_id, course_code in assignments:
        enrolled = course_students.get(course_code, [])
        if not enrolled:
            continue
        sample_size = max(1, int(len(enrolled) * 0.20))
        submitters  = random.sample(enrolled, min(sample_size, len(enrolled)))

        for student_id in submitters:
            grade    = round(random.uniform(40, 100), 2) if random.random() < 0.85 else None
            feedback = ("Well done!" if grade and grade >= 75
                        else "Satisfactory." if grade else None)
            sub_input_rows.append((
                random_past_date(300),
                f"https://files.university.edu/{ass_id}/{student_id}.pdf",
                grade,
                feedback
            ))
            ssa_meta.append((student_id, ass_id))

    print(f"    Total submissions to insert: {len(sub_input_rows):,}")

    # Insert submissions in batches, capturing sub_ids via RETURNING
    sub_ids = batch_execute_returning(cur, """
        INSERT INTO Submission (submitted_at, file_url, grade, feedback)
        VALUES %s RETURNING sub_id
    """, sub_input_rows)

    # Build and insert SSA using the real sub_ids
    ssa_rows = [
        (student_id, sub_id, ass_id)
        for (student_id, ass_id), sub_id in zip(ssa_meta, sub_ids)
    ]
    batch_execute(cur,
        "INSERT INTO SSA (student_id, submission_id, assignment_id) VALUES %s",
        ssa_rows
    )


def seed_forums(cur, course_codes: list[str],
                all_account_ids: list[int]) -> dict[int, list[int]]:
    """
    Create 1–2 forums per course.
    Returns {df_id: [thread_ids]} — built as threads are created.
    Actually returns {df_id: course_code} mapping; threads are seeded separately.
    Returns list of df_ids in order.
    """
    forum_rows = [
        (
            code,
            random.choice(all_account_ids),
            f"{code} — General Discussion" if j == 1 else f"{code} — Q&A",
            random_past_date(400)
        )
        for code in course_codes
        for j in range(1, random.randint(1, 2) + 1)
    ]

    df_ids = batch_execute_returning(cur, """
        INSERT INTO Discussion_Forum (course_code, created_by, title, created_at)
        VALUES %s RETURNING df_id
    """, forum_rows)

    return df_ids


def seed_threads(cur, forum_ids: list[int],
                 all_account_ids: list[int]) -> None:
    """
    Create 3–8 threads per forum, link via DDA.
    Then create Reply_To relationships for ~40% of non-first threads.
    """
    # Build thread data and track forum assignment
    thread_rows  = []  # (title, content, created_at)
    forum_map    = []  # parallel list: forum_id for each thread

    for df_id in forum_ids:
        num_threads = random.randint(3, 8)
        for k in range(1, num_threads + 1):
            thread_rows.append((
                f"Thread {k}: Discussion Topic",
                f"This is the opening post for thread {k} in forum {df_id}.",
                random_past_date(250)
            ))
            forum_map.append(df_id)

    dt_ids = batch_execute_returning(cur, """
        INSERT INTO Discussion_Thread (title, content, created_at)
        VALUES %s RETURNING dt_id
    """, thread_rows)

    # DDA: link each thread to its forum and a random account
    dda_rows = [
        (random.choice(all_account_ids), dt_id, forum_id)
        for dt_id, forum_id in zip(dt_ids, forum_map)
    ]
    batch_execute(cur,
        "INSERT INTO DDA (account_id, thread_id, forum_id) VALUES %s",
        dda_rows
    )

    # Reply_To: group threads by forum, make later threads reply to earlier ones
    forum_threads: dict[int, list[int]] = {}
    for dt_id, df_id in zip(dt_ids, forum_map):
        forum_threads.setdefault(df_id, []).append(dt_id)

    reply_rows = []
    for df_id, thread_list in forum_threads.items():
        # First thread in each forum is always top-level
        for k in range(1, len(thread_list)):
            if random.random() < 0.40:  # 40% chance of being a reply
                parent_id = random.choice(thread_list[:k])  # reply to an earlier thread
                child_id  = thread_list[k]
                reply_rows.append((child_id, parent_id))

    if reply_rows:
        batch_execute(cur,
            "INSERT INTO Reply_To (child_id, parent_id) VALUES %s",
            reply_rows
        )


def seed_calendar_events(cur, course_codes: list[str]) -> None:
    """Create 2–5 calendar events per course."""
    event_types = ["Lecture", "Assignment Due", "Exam", "Lab Session", "Quiz"]
    event_rows  = [
        (
            code,
            f"{random.choice(event_types)} — Week {j}",
            f"Scheduled {event_types[j % len(event_types)].lower()} for {code}.",
            random_future_date(180)
        )
        for code in course_codes
        for j in range(1, random.randint(2, 5) + 1)
    ]

    batch_execute(cur, """
        INSERT INTO Calendar_Event (course_code, title, description, event_date)
        VALUES %s
    """, event_rows)


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        print("=" * 55)
        print("  COMP3161 Database Seed Script")
        print("=" * 55)

        print("\n[1/11] Admin account...")
        seed_admin(cur)

        print(f"\n[2/11] {NUM_LECTURERS} Lecturers...")
        lecturer_ids = seed_lecturers(cur)

        print(f"\n[3/11] {NUM_STUDENTS:,} Students...")
        student_ids = seed_students(cur)

        print(f"\n[4/11] {NUM_COURSES} Courses...")
        course_codes = seed_courses(cur)

        print("\n[5/11] Teach assignments (1 lecturer per course)...")
        seed_teach(cur, lecturer_ids, course_codes)

        print("\n[6/11] Enrollments (3–6 per student)...")
        seed_enroll(cur, student_ids, course_codes)

        print("\n[7/11] Sections...")
        sections = seed_sections(cur, course_codes)

        print("\n[8/11] Section items...")
        seed_section_items(cur, sections)

        print("\n[9/11] Assignments and submissions...")
        assignments = seed_assignments(cur, course_codes)
        seed_submissions(cur, assignments)

        print("\n[10/11] Discussion forums and threads...")
        all_account_ids = lecturer_ids + random.sample(student_ids, min(5_000, len(student_ids)))
        forum_ids = seed_forums(cur, course_codes, all_account_ids)
        seed_threads(cur, forum_ids, all_account_ids)

        print("\n[11/11] Calendar events...")
        seed_calendar_events(cur, course_codes)

        conn.commit()

        # ── Summary ──────────────────────────────────────────
        print("\n" + "=" * 55)
        print("  Seed complete. Verifying row counts...")
        print("=" * 55)
        checks = [
            ("Account",          "SELECT COUNT(*) FROM Account"),
            ("Student",          "SELECT COUNT(*) FROM Student"),
            ("Lecturer",         "SELECT COUNT(*) FROM Lecturer"),
            ("Course",           "SELECT COUNT(*) FROM Course"),
            ("Enroll",           "SELECT COUNT(*) FROM Enroll"),
            ("Teach",            "SELECT COUNT(*) FROM Teach"),
            ("Section",          "SELECT COUNT(*) FROM Section"),
            ("Section_Item",     "SELECT COUNT(*) FROM Section_Item"),
            ("Assignment",       "SELECT COUNT(*) FROM Assignment"),
            ("Submission",       "SELECT COUNT(*) FROM Submission"),
            ("SSA",              "SELECT COUNT(*) FROM SSA"),
            ("Discussion_Forum", "SELECT COUNT(*) FROM Discussion_Forum"),
            ("Discussion_Thread","SELECT COUNT(*) FROM Discussion_Thread"),
            ("DDA",              "SELECT COUNT(*) FROM DDA"),
            ("Reply_To",         "SELECT COUNT(*) FROM Reply_To"),
            ("Calendar_Event",   "SELECT COUNT(*) FROM Calendar_Event"),
        ]
        for label, query in checks:
            cur.execute(query)
            count = cur.fetchone()[0]
            print(f"  {label:<22} {count:>10,} rows")

        print("\n✅ Database ready.\n")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Seed failed: {e}")
        raise

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()