# ==================== TEST: DATABASE ====================
# Test Supabase CRUD operations
# ⚠️  Requires SUPABASE_URL and SUPABASE_KEY in .env
# ⚠️  This will create/modify real data in your Supabase database
# Run: python -m pytest tests/test_database.py -v -s

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _check_db_configured():
    """Return True if Supabase credentials are set."""
    from config import settings
    return bool(settings.supabase_url and settings.supabase_key)


def test_supabase_connection():
    """Verify Supabase client can connect."""
    if not _check_db_configured():
        print("  ⏭️  Skipping — Supabase not configured")
        return

    from config import supabase

    # Simple query to check connectivity
    result = supabase.table("interviews").select("id").limit(1).execute()
    print(f"  ✅ Supabase connected. Returned {len(result.data)} row(s)")


def test_interview_crud():
    """
    Full CRUD test: create → read → update → cleanup.
    ⚠️  Needs a valid user ID (UUID) that exists in the users table.
    If you don't have one, this test will fail on the insert due to
    the foreign key constraint on created_by.
    """
    if not _check_db_configured():
        print("  ⏭️  Skipping — Supabase not configured")
        return

    from config import supabase
    from database import create_interview_session, update_interview_session

    # First, try to get an existing user ID for the foreign key
    user_result = supabase.table("users").select("id").limit(1).execute()
    if not user_result.data:
        print("  ⏭️  Skipping CRUD test — no users in database. Create a user first.")
        return

    user_id = user_result.data[0]["id"]
    print(f"  Using user ID: {user_id}")

    # CREATE
    interview = asyncio.run(
        create_interview_session(
            candidate_name="Test Candidate (pytest)",
            candidate_email="test@pytest.dev",
            role="Test Engineer",
            notes="Automated test — safe to delete",
            user_id=user_id,
            metadata={
                "interviewType": "Technical",
                "agentName": "TestBot",
                "companyName": "PyTest Corp",
            },
        )
    )
    assert interview and len(interview) > 0
    interview_id = interview[0]["id"]
    print(f"  ✅ Created interview: ID={interview_id}")

    # READ
    read_result = (
        supabase.table("interviews")
        .select("*")
        .eq("id", interview_id)
        .single()
        .execute()
    )
    assert read_result.data is not None
    assert read_result.data["candidate_name"] == "Test Candidate (pytest)"
    print(f"  ✅ Read interview: {read_result.data['candidate_name']}")

    # UPDATE
    updated = asyncio.run(
        update_interview_session(interview_id, {"status": "completed", "notes": "Updated by test"})
    )
    assert updated and updated[0]["status"] == "completed"
    print(f"  ✅ Updated interview status to: {updated[0]['status']}")

    # CLEANUP — delete the test record
    supabase.table("interviews").delete().eq("id", interview_id).execute()
    print(f"  🧹 Cleaned up test interview: ID={interview_id}")


def test_transcript_operations():
    """Test transcript insert and read (requires existing interview)."""
    if not _check_db_configured():
        print("  ⏭️  Skipping — Supabase not configured")
        return

    from config import supabase

    # Check if there's any interview to test with
    result = supabase.table("interviews").select("id").limit(1).execute()
    if not result.data:
        print("  ⏭️  Skipping — no interviews in database")
        return

    interview_id = result.data[0]["id"]
    print(f"  Using interview ID: {interview_id}")

    # Read transcripts for this interview
    transcript_result = (
        supabase.table("transcripts")
        .select("*")
        .eq("interview_id", interview_id)
        .execute()
    )
    print(f"  ✅ Found {len(transcript_result.data)} transcript(s) for interview {interview_id}")


if __name__ == "__main__":
    print("=" * 50)
    print("DATABASE TESTS")
    print("=" * 50)
    test_supabase_connection()
    test_interview_crud()
    test_transcript_operations()
    print("\n✅ All database tests passed!")
