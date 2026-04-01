-- =============================================================
-- COMP3161 Final Project
-- Database: Course Management System
-- File: create.sql
-- Description: Creates all tables in dependency order
-- =============================================================


-- =============================================================
-- EXTENSIONS
-- =============================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- for password hashing support


-- =============================================================
-- LAYER 1: No dependencies
-- =============================================================

CREATE TABLE Account (
    acc_id      SERIAL PRIMARY KEY,
    name        VARCHAR(100)  NOT NULL,
    email       VARCHAR(255)  NOT NULL UNIQUE,
    password    VARCHAR(255)  NOT NULL,
    created_at  TIMESTAMP     NOT NULL DEFAULT NOW(),
    status      VARCHAR(10)   NOT NULL DEFAULT 'active'
                CHECK (status IN ('active', 'inactive'))
);

CREATE TABLE Course (
    course_code VARCHAR(10)  PRIMARY KEY,
    course_name VARCHAR(150) NOT NULL,
    description TEXT
);


-- =============================================================
-- LAYER 2: Depend only on Account
-- =============================================================

CREATE TABLE Student (
    acc_id      INT          PRIMARY KEY REFERENCES Account(acc_id) ON DELETE CASCADE,
    student_no  VARCHAR(20)  NOT NULL UNIQUE,
    program     VARCHAR(100) NOT NULL,
    year        INT          NOT NULL CHECK (year BETWEEN 1 AND 6)
);

CREATE TABLE Lecturer (
    acc_id      INT          PRIMARY KEY REFERENCES Account(acc_id) ON DELETE CASCADE,
    staff_id    VARCHAR(20)  NOT NULL UNIQUE,
    department  VARCHAR(100) NOT NULL
);

CREATE TABLE Admin (
    acc_id      INT PRIMARY KEY REFERENCES Account(acc_id) ON DELETE CASCADE
);


-- =============================================================
-- LAYER 3: Depend on Account + Course
-- =============================================================

CREATE TABLE Enroll (
    student_id    INT          NOT NULL REFERENCES Student(acc_id) ON DELETE CASCADE,
    course_code   VARCHAR(10)  NOT NULL REFERENCES Course(course_code) ON DELETE CASCADE,
    grade         NUMERIC(5,2) CHECK (grade BETWEEN 0 AND 100),
    date_enrolled DATE         NOT NULL DEFAULT CURRENT_DATE,
    PRIMARY KEY (student_id, course_code)
);

CREATE TABLE Teach (
    lecturer_id   INT         NOT NULL REFERENCES Lecturer(acc_id) ON DELETE CASCADE,
    course_code   VARCHAR(10) NOT NULL REFERENCES Course(course_code) ON DELETE CASCADE,
    PRIMARY KEY (lecturer_id, course_code)
);

CREATE TABLE Section (
    sec_no        INT         NOT NULL,
    course_code   VARCHAR(10) NOT NULL REFERENCES Course(course_code) ON DELETE CASCADE,
    title         VARCHAR(200) NOT NULL,
    PRIMARY KEY (sec_no, course_code)
);

CREATE TABLE Assignment (
    ass_id        SERIAL      PRIMARY KEY,
    course_code   VARCHAR(10) NOT NULL REFERENCES Course(course_code) ON DELETE CASCADE,
    title         VARCHAR(200) NOT NULL,
    description   TEXT,
    due_date      TIMESTAMP   NOT NULL
);

CREATE TABLE Discussion_Forum (
    df_id         SERIAL       PRIMARY KEY,
    course_code   VARCHAR(10)  NOT NULL REFERENCES Course(course_code) ON DELETE CASCADE,
    created_by    INT          NOT NULL REFERENCES Account(acc_id),
    title         VARCHAR(200) NOT NULL,
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE Calendar_Event (
    ev_id         SERIAL       PRIMARY KEY,
    course_code   VARCHAR(10)  NOT NULL REFERENCES Course(course_code) ON DELETE CASCADE,
    title         VARCHAR(200) NOT NULL,
    description   TEXT,
    event_date    TIMESTAMP    NOT NULL
);


-- =============================================================
-- LAYER 4: Depend on Section, Assignment
-- =============================================================

CREATE TABLE Section_Item (
    item_id       SERIAL       PRIMARY KEY,
    sec_no        INT          NOT NULL,
    course_code   VARCHAR(10)  NOT NULL,
    title         VARCHAR(200) NOT NULL,
    type          VARCHAR(20)  NOT NULL
                  CHECK (type IN ('link', 'file', 'video', 'document', 'slide')),
    content_url   TEXT         NOT NULL,
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW(),
    FOREIGN KEY (sec_no, course_code) REFERENCES Section(sec_no, course_code) ON DELETE CASCADE
);

CREATE TABLE Submission (
    sub_id        SERIAL       PRIMARY KEY,
    submitted_at  TIMESTAMP    NOT NULL DEFAULT NOW(),
    file_url      TEXT         NOT NULL,
    grade         NUMERIC(5,2) CHECK (grade BETWEEN 0 AND 100),
    feedback      TEXT
);


-- =============================================================
-- LAYER 5: Depend on Student, Submission, Assignment
-- =============================================================

CREATE TABLE SSA (
    student_id    INT NOT NULL REFERENCES Student(acc_id)     ON DELETE CASCADE,
    submission_id INT NOT NULL REFERENCES Submission(sub_id)  ON DELETE CASCADE,
    assignment_id INT NOT NULL REFERENCES Assignment(ass_id)  ON DELETE CASCADE,
    PRIMARY KEY (student_id, submission_id, assignment_id)
);


-- =============================================================
-- LAYER 6: Discussion_Thread (standalone entity)
-- =============================================================

CREATE TABLE Discussion_Thread (
    dt_id         SERIAL       PRIMARY KEY,
    title         VARCHAR(200) NOT NULL,
    content       TEXT         NOT NULL,
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);


-- =============================================================
-- LAYER 7: Depend on Account + Discussion_Thread + Discussion_Forum
-- =============================================================

-- Links an account and a thread to a forum (who posted what where)
CREATE TABLE DDA (
    account_id    INT NOT NULL REFERENCES Account(acc_id)           ON DELETE CASCADE,
    thread_id     INT NOT NULL REFERENCES Discussion_Thread(dt_id)  ON DELETE CASCADE,
    forum_id      INT NOT NULL REFERENCES Discussion_Forum(df_id)   ON DELETE CASCADE,
    PRIMARY KEY (account_id, thread_id, forum_id)
);

-- Links a child thread (reply) to its parent thread
CREATE TABLE Reply_To (
    child_id      INT NOT NULL PRIMARY KEY REFERENCES Discussion_Thread(dt_id) ON DELETE CASCADE,
    parent_id     INT NOT NULL             REFERENCES Discussion_Thread(dt_id) ON DELETE CASCADE,
    -- A thread cannot be a reply to itself
    CHECK (child_id <> parent_id)
);


-- =============================================================
-- INDEXES
-- =============================================================

-- Account: fast login lookup by email
CREATE INDEX idx_account_email       ON Account(email);

-- Enroll: fast lookup by course and by student
CREATE INDEX idx_enroll_course       ON Enroll(course_code);
CREATE INDEX idx_enroll_student      ON Enroll(student_id);

-- Teach: fast lookup by course and by lecturer
CREATE INDEX idx_teach_course        ON Teach(course_code);
CREATE INDEX idx_teach_lecturer      ON Teach(lecturer_id);

-- Section_Item: fast retrieval of all items in a section
CREATE INDEX idx_section_item        ON Section_Item(sec_no, course_code);

-- Assignment: fast lookup of assignments per course
CREATE INDEX idx_assignment_course   ON Assignment(course_code);

-- SSA: fast lookup of all submissions by a student or for an assignment
CREATE INDEX idx_ssa_student         ON SSA(student_id);
CREATE INDEX idx_ssa_assignment      ON SSA(assignment_id);

-- Discussion_Forum: fast lookup of forums per course
CREATE INDEX idx_forum_course        ON Discussion_Forum(course_code);

-- DDA: fast lookup of all threads in a forum
CREATE INDEX idx_dda_forum           ON DDA(forum_id);

-- Reply_To: fast lookup of all replies to a given parent thread
CREATE INDEX idx_reply_parent        ON Reply_To(parent_id);

-- Calendar_Event: fast lookup by course and by date (used in student calendar query)
CREATE INDEX idx_calendar_course     ON Calendar_Event(course_code);
CREATE INDEX idx_calendar_date       ON Calendar_Event(event_date);
