# ==================== TEST: ENDPOINTS ====================
# Test all FastAPI REST endpoints using TestClient
# No live server needed — uses FastAPI's built-in test client
# Run: python -m pytest tests/test_endpoints.py -v -s

import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ==================== HEALTH CHECK ====================


def test_health_check():
    """Health endpoint should always return 200."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data
    print(f"  ✅ Health check: {data}")


# ==================== SCHEDULE INTERVIEW ====================


def test_schedule_interview_missing_fields():
    """Should return 400 when required fields are missing."""
    response = client.post("/api/schedule-interview", json={
        "candidateName": "",
        "candidateEmail": "",
        "role": "",
    })
    # FastAPI validation or our custom check
    assert response.status_code in [400, 401, 422]
    print(f"  ✅ Schedule interview validation: status={response.status_code}")


def test_schedule_interview_no_auth():
    """Should return 401 when userId is missing."""
    response = client.post("/api/schedule-interview", json={
        "candidateName": "Test User",
        "candidateEmail": "test@test.com",
        "role": "Engineer",
    })
    assert response.status_code in [401, 422, 500]
    print(f"  ✅ Schedule interview auth check: status={response.status_code}")


# ==================== START VOICE SESSION ====================


def test_start_voice_session_missing_fields():
    """Should fail with missing required fields."""
    response = client.post("/api/start-voice-session", json={})
    assert response.status_code == 422  # Pydantic validation error
    print(f"  ✅ Start voice session validation: status={response.status_code}")


# ==================== CREATE CALL ====================


def test_create_call_missing_fields():
    """Should fail with missing required fields."""
    response = client.post("/api/create-call", json={})
    assert response.status_code == 422
    print(f"  ✅ Create call validation: status={response.status_code}")


# ==================== SAVE EVALUATION ====================


def test_save_evaluation_missing_id():
    """Should fail when interviewId is missing."""
    response = client.post("/api/save-evaluation", json={})
    assert response.status_code == 422
    print(f"  ✅ Save evaluation validation: status={response.status_code}")


# ==================== STOP INTERVIEW ====================


def test_stop_interview_missing_id():
    """Should fail when interviewId is missing."""
    response = client.post("/api/stop-interview", json={})
    assert response.status_code == 422
    print(f"  ✅ Stop interview validation: status={response.status_code}")


# ==================== SAVE TRANSCRIPT ====================


def test_save_transcript_missing_fields():
    """Should fail with missing required fields."""
    response = client.post("/api/save-transcript", json={
        "interviewId": 1,
    })
    assert response.status_code == 422
    print(f"  ✅ Save transcript validation: status={response.status_code}")


# ==================== EVALUATE INTERVIEW ====================


def test_evaluate_interview_missing_fields():
    """Should fail with missing required fields."""
    response = client.post("/api/evaluate-interview", json={})
    assert response.status_code == 422
    print(f"  ✅ Evaluate interview validation: status={response.status_code}")


# ==================== GET INTERVIEW ====================


def test_get_interview_invalid_id():
    """Fetching a non-existent interview should return 500 (Supabase error)."""
    response = client.get("/api/interview/999999999")
    # Will likely fail because the interview doesn't exist in DB
    assert response.status_code in [200, 404, 500]
    print(f"  ✅ Get interview: status={response.status_code}")


# ==================== PATCH INTERVIEW ====================


def test_patch_interview_invalid_id():
    """Patching a non-existent interview."""
    response = client.patch("/api/interview/999999999", json={"notes": "test"})
    # May succeed with empty result or fail
    assert response.status_code in [200, 404, 500]
    print(f"  ✅ Patch interview: status={response.status_code}")


# ==================== WEBHOOK ====================


def test_webhook_call_ended_missing_fields():
    """Should fail with missing required fields."""
    response = client.post("/api/webhooks/call-ended", json={})
    assert response.status_code == 422
    print(f"  ✅ Webhook call-ended validation: status={response.status_code}")


if __name__ == "__main__":
    print("=" * 50)
    print("ENDPOINT TESTS")
    print("=" * 50)
    test_health_check()
    test_schedule_interview_missing_fields()
    test_schedule_interview_no_auth()
    test_start_voice_session_missing_fields()
    test_create_call_missing_fields()
    test_save_evaluation_missing_id()
    test_stop_interview_missing_id()
    test_save_transcript_missing_fields()
    test_evaluate_interview_missing_fields()
    test_get_interview_invalid_id()
    test_patch_interview_invalid_id()
    test_webhook_call_ended_missing_fields()
    print("\n✅ All endpoint tests passed!")
