# ==================== DATABASE FUNCTIONS ====================
# Supabase CRUD helper functions — direct port from server.js

from datetime import datetime, timezone
from config import supabase


def _now() -> str:
    """Return current UTC timestamp as ISO string."""
    return datetime.now(timezone.utc).isoformat()


async def create_interview_session(
    candidate_name: str,
    candidate_email: str,
    role: str,
    notes: str = "",
    user_id: str | None = None,
    metadata: dict | None = None,
) -> list[dict]:
    """Insert a new interview record into the database."""
    metadata = metadata or {}

    result = (
        supabase.table("interviews")
        .insert(
            {
                "candidate_name": candidate_name,
                "candidate_email": candidate_email,
                "role": role,
                "notes": notes,
                "interview_type": metadata.get("interviewType", "Technical"),
                "voice": "Mark",  # Fixed voice — always Mark
                "agent_name": metadata.get("agentName", "Alex"),
                "company_name": metadata.get("companyName"),
                "resume": metadata.get("resume"),
                "custom_instructions": metadata.get("customInstructions"),
                "status": "scheduled",
                "created_by": user_id,
                "created_at": _now(),
                "updated_at": _now(),
            }
        )
        .execute()
    )

    if hasattr(result, "error") and result.error:
        raise Exception(f"Database error: {result.error}")
    return result.data


async def update_interview_session(interview_id: int, updates: dict) -> list[dict]:
    """Update an existing interview record."""
    updates["updated_at"] = _now()

    result = (
        supabase.table("interviews")
        .update(updates)
        .eq("id", interview_id)
        .execute()
    )

    if hasattr(result, "error") and result.error:
        raise Exception(f"Database error: {result.error}")
    return result.data


async def save_interview_transcript(
    interview_id: int,
    call_id: str,
    transcript: str,
    summary: str,
) -> list[dict]:
    """Insert a transcript entry for a completed call."""
    result = (
        supabase.table("transcripts")
        .insert(
            {
                "interview_id": interview_id,
                "call_id": call_id,
                "transcript": transcript,
                "summary": summary,
                "created_at": _now(),
            }
        )
        .execute()
    )

    if hasattr(result, "error") and result.error:
        raise Exception(f"Database error: {result.error}")
    return result.data


async def save_evaluation_score(
    interview_id: int,
    problem_solving: float,
    communication: float,
    technical_depth: float,
    adaptability: float,
    notes: str,
) -> list[dict]:
    """Insert an evaluation score record."""
    overall_score = (problem_solving + communication + technical_depth + adaptability) / 4

    result = (
        supabase.table("evaluations")
        .insert(
            {
                "interview_id": interview_id,
                "problem_solving": problem_solving,
                "communication": communication,
                "technical_depth": technical_depth,
                "adaptability": adaptability,
                "overall_score": overall_score,
                "notes": notes,
                "created_at": _now(),
            }
        )
        .execute()
    )

    if hasattr(result, "error") and result.error:
        raise Exception(f"Database error: {result.error}")
    return result.data
