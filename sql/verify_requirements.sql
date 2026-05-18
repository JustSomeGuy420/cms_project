-- =============================================================
-- COMP3161 Final Project
-- File: verify_requirements.sql
-- Description: Verifies all data population requirements
--              are met. Each query prints PASS or FAIL.
-- =============================================================

-- Requirement 1: At least 100,000 students
SELECT
    'Requirement 1: At least 100,000 students'  AS requirement,
    COUNT(*)                                     AS actual,
    100000                                       AS minimum,
    CASE WHEN COUNT(*) >= 100000 THEN 'PASS' ELSE 'FAIL' END AS result
FROM Student;

-- Requirement 2: At least 200 courses
SELECT
    'Requirement 2: At least 200 courses'       AS requirement,
    COUNT(*)                                     AS actual,
    200                                          AS minimum,
    CASE WHEN COUNT(*) >= 200 THEN 'PASS' ELSE 'FAIL' END AS result
FROM Course;

-- Requirement 3: No student enrolled in more than 6 courses
SELECT
    'Requirement 3: No student in more than 6 courses' AS requirement,
    MAX(course_count)                                   AS max_courses_any_student,
    6                                                   AS maximum,
    CASE WHEN MAX(course_count) <= 6 THEN 'PASS' ELSE 'FAIL' END AS result
FROM (
    SELECT student_id, COUNT(*) AS course_count
    FROM Enroll
    GROUP BY student_id
) counts;

-- Requirement 4: Every student enrolled in at least 3 courses
SELECT
    'Requirement 4: Every student in at least 3 courses' AS requirement,
    MIN(course_count)                                     AS min_courses_any_student,
    3                                                     AS minimum,
    CASE WHEN MIN(course_count) >= 3 THEN 'PASS' ELSE 'FAIL' END AS result
FROM (
    SELECT student_id, COUNT(*) AS course_count
    FROM Enroll
    GROUP BY student_id
) counts;

-- Requirement 5: Each course has at least 10 enrolled students
SELECT
    'Requirement 5: Each course has at least 10 students' AS requirement,
    MIN(student_count)                                     AS min_students_any_course,
    10                                                     AS minimum,
    CASE WHEN MIN(student_count) >= 10 THEN 'PASS' ELSE 'FAIL' END AS result
FROM (
    SELECT course_code, COUNT(*) AS student_count
    FROM Enroll
    GROUP BY course_code
) counts;

-- Requirement 6: No lecturer teaches more than 5 courses
SELECT
    'Requirement 6: No lecturer teaches more than 5 courses' AS requirement,
    MAX(course_count)                                         AS max_courses_any_lecturer,
    5                                                         AS maximum,
    CASE WHEN MAX(course_count) <= 5 THEN 'PASS' ELSE 'FAIL' END AS result
FROM (
    SELECT lecturer_id, COUNT(*) AS course_count
    FROM Teach
    GROUP BY lecturer_id
) counts;

-- Requirement 7: Every lecturer teaches at least 1 course
SELECT
    'Requirement 7: Every lecturer teaches at least 1 course' AS requirement,
    MIN(course_count)                                          AS min_courses_any_lecturer,
    1                                                          AS minimum,
    CASE WHEN MIN(course_count) >= 1 THEN 'PASS' ELSE 'FAIL' END AS result
FROM (
    SELECT l.acc_id, COUNT(t.course_code) AS course_count
    FROM Lecturer l
    LEFT JOIN Teach t ON l.acc_id = t.lecturer_id
    GROUP BY l.acc_id
) counts;

-- Requirement 8: Each course has exactly 1 lecturer assigned
SELECT
    'Requirement 8: Each course has exactly 1 lecturer'  AS requirement,
    MAX(lecturer_count)                                   AS max_lecturers_any_course,
    1                                                     AS maximum,
    CASE WHEN MAX(lecturer_count) = 1 THEN 'PASS' ELSE 'FAIL' END AS result
FROM (
    SELECT course_code, COUNT(*) AS lecturer_count
    FROM Teach
    GROUP BY course_code
) counts;

-- ── Summary row counts ────────────────────────────────────────
SELECT '--- ROW COUNTS ---' AS summary, NULL AS value
UNION ALL SELECT 'Account',           COUNT(*)::TEXT FROM Account
UNION ALL SELECT 'Student',           COUNT(*)::TEXT FROM Student
UNION ALL SELECT 'Lecturer',          COUNT(*)::TEXT FROM Lecturer
UNION ALL SELECT 'Course',            COUNT(*)::TEXT FROM Course
UNION ALL SELECT 'Enroll',            COUNT(*)::TEXT FROM Enroll
UNION ALL SELECT 'Teach',             COUNT(*)::TEXT FROM Teach
UNION ALL SELECT 'Section',           COUNT(*)::TEXT FROM Section
UNION ALL SELECT 'Section_Item',      COUNT(*)::TEXT FROM Section_Item
UNION ALL SELECT 'Assignment',        COUNT(*)::TEXT FROM Assignment
UNION ALL SELECT 'Submission',        COUNT(*)::TEXT FROM Submission
UNION ALL SELECT 'SSA',               COUNT(*)::TEXT FROM SSA
UNION ALL SELECT 'Discussion_Forum',  COUNT(*)::TEXT FROM Discussion_Forum
UNION ALL SELECT 'Discussion_Thread', COUNT(*)::TEXT FROM Discussion_Thread
UNION ALL SELECT 'Calendar_Event',    COUNT(*)::TEXT FROM Calendar_Event;
