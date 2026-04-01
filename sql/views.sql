-- =============================================================
-- COMP3161 Final Project
-- File: views.sql
-- Description: Report views as required by the project spec
-- =============================================================


-- =============================================================
-- VIEW 1: All courses that have 50 or more students
-- =============================================================
-- Counts enrolled students per course and filters to those
-- with 50 or more. Includes course details for readability.
-- =============================================================

CREATE OR REPLACE VIEW view_courses_50_plus_students AS
SELECT
    c.course_code,
    c.course_name,
    COUNT(e.student_id)     AS student_count
FROM Course c
JOIN Enroll e ON c.course_code = e.course_code
GROUP BY c.course_code, c.course_name
HAVING COUNT(e.student_id) >= 50
ORDER BY student_count DESC;


-- =============================================================
-- VIEW 2: All students enrolled in 5 or more courses
-- =============================================================
-- Counts courses per student and filters to those doing 5+.
-- Includes account and student details for identification.
-- =============================================================

CREATE OR REPLACE VIEW view_students_5_plus_courses AS
SELECT
    a.acc_id,
    a.name,
    a.email,
    s.student_no,
    s.program,
    s.year,
    COUNT(e.course_code)    AS course_count
FROM Account a
JOIN Student s ON a.acc_id  = s.acc_id
JOIN Enroll e  ON s.acc_id  = e.student_id
GROUP BY a.acc_id, a.name, a.email, s.student_no, s.program, s.year
HAVING COUNT(e.course_code) >= 5
ORDER BY course_count DESC;


-- =============================================================
-- VIEW 3: All lecturers teaching 3 or more courses
-- =============================================================
-- Counts courses per lecturer and filters to those teaching 3+.
-- Includes staff details and department for identification.
-- =============================================================

CREATE OR REPLACE VIEW view_lecturers_3_plus_courses AS
SELECT
    a.acc_id,
    a.name,
    a.email,
    l.staff_id,
    l.department,
    COUNT(t.course_code)    AS course_count
FROM Account a
JOIN Lecturer l ON a.acc_id     = l.acc_id
JOIN Teach t    ON l.acc_id     = t.lecturer_id
GROUP BY a.acc_id, a.name, a.email, l.staff_id, l.department
HAVING COUNT(t.course_code) >= 3
ORDER BY course_count DESC;


-- =============================================================
-- VIEW 4: The 10 most enrolled courses
-- =============================================================
-- Ranks all courses by enrollment count and returns the top 10.
-- Also includes the lecturer assigned to each course.
-- =============================================================

CREATE OR REPLACE VIEW view_top_10_enrolled_courses AS
SELECT
    c.course_code,
    c.course_name,
    a.name                  AS lecturer_name,
    COUNT(e.student_id)     AS student_count
FROM Course c
JOIN Enroll e  ON c.course_code  = e.course_code
JOIN Teach t   ON c.course_code  = t.course_code
JOIN Lecturer l ON t.lecturer_id = l.acc_id
JOIN Account a  ON l.acc_id      = a.acc_id
GROUP BY c.course_code, c.course_name, a.name
ORDER BY student_count DESC
LIMIT 10;


-- =============================================================
-- VIEW 5: Top 10 students with the highest overall averages
-- =============================================================
-- Computes each student's average grade across all enrolled
-- courses (only counting graded enrollments where grade IS NOT
-- NULL). Returns the top 10 by average, descending.
-- =============================================================

CREATE OR REPLACE VIEW view_top_10_students_by_average AS
SELECT
    a.acc_id,
    a.name,
    a.email,
    s.student_no,
    s.program,
    COUNT(e.course_code)            AS graded_courses,
    ROUND(AVG(e.grade), 2)          AS overall_average
FROM Account a
JOIN Student s ON a.acc_id  = s.acc_id
JOIN Enroll e  ON s.acc_id  = e.student_id
WHERE e.grade IS NOT NULL
GROUP BY a.acc_id, a.name, a.email, s.student_no, s.program
ORDER BY overall_average DESC
LIMIT 10;


-- =============================================================
-- Quick test queries — run these to verify views work
-- =============================================================

-- SELECT * FROM view_courses_50_plus_students;
-- SELECT * FROM view_students_5_plus_courses;
-- SELECT * FROM view_lecturers_3_plus_courses;
-- SELECT * FROM view_top_10_enrolled_courses;
-- SELECT * FROM view_top_10_students_by_average;