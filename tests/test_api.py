"""
Integration tests for the CMS API.
These run against a real PostgreSQL + Redis instance (provided by CI).
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# ── Helpers ───────────────────────────────────────────────────

def register(email, password, role, **kwargs):
    return client.post("/auth/register", json={
        "name": "Test User", "email": email,
        "password": password, "role": role, **kwargs
    })

def login(email, password):
    return client.post("/auth/login", json={"email": email, "password": password})

def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


# ── Auth tests ────────────────────────────────────────────────

def test_register_admin():
    r = register("admin_test@test.com", "pass123", "admin")
    assert r.status_code == 201
    assert "acc_id" in r.json()

def test_register_student():
    r = register("student_test@test.com", "pass123", "student",
                 student_no="S9999999", program="Computer Science", year=2)
    assert r.status_code == 201

def test_register_lecturer():
    r = register("lecturer_test@test.com", "pass123", "lecturer",
                 staff_id="STAFF9999", department="Computer Science")
    assert r.status_code == 201

def test_register_duplicate_email():
    register("dup@test.com", "pass123", "admin")
    r = register("dup@test.com", "pass123", "admin")
    assert r.status_code == 409

def test_login_success():
    register("login_test@test.com", "pass123", "admin")
    r = login("login_test@test.com", "pass123")
    assert r.status_code == 200
    assert "access_token" in r.json()

def test_login_wrong_password():
    register("wrong_pass@test.com", "pass123", "admin")
    r = login("wrong_pass@test.com", "wrongpass")
    assert r.status_code == 401

def test_protected_route_without_token():
    r = client.get("/courses")
    assert r.status_code == 403   # HTTPBearer returns 403 when no token


# ── Course tests ──────────────────────────────────────────────

def test_create_course_as_admin():
    register("admin2@test.com", "pass123", "admin")
    token = login("admin2@test.com", "pass123").json()["access_token"]
    r = client.post("/courses", json={
        "course_code": "TEST1001",
        "course_name": "Test Course",
        "description": "A test course"
    }, headers=auth_header(token))
    assert r.status_code == 201

def test_create_course_as_student_is_forbidden():
    register("stu2@test.com", "pass123", "student",
             student_no="S8888888", program="CS", year=1)
    token = login("stu2@test.com", "pass123").json()["access_token"]
    r = client.post("/courses", json={
        "course_code": "FAIL1001",
        "course_name": "Should Fail",
    }, headers=auth_header(token))
    assert r.status_code == 403

def test_get_all_courses():
    register("admin3@test.com", "pass123", "admin")
    token = login("admin3@test.com", "pass123").json()["access_token"]
    r = client.get("/courses", headers=auth_header(token))
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ── Health check ──────────────────────────────────────────────

def test_health_check():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
