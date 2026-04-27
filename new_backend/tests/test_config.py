# ==================== TEST: CONFIG ====================
# Verify environment loading and Supabase client initialization
# Run: python -m pytest tests/test_config.py -v

import sys
import os

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_settings_load():
    """Settings object should load without crashing."""
    from config import Settings

    s = Settings()
    assert isinstance(s.port, int)
    print(f"  ✅ Settings loaded. Port = {s.port}")


def test_env_vars_present():
    """Check that critical env vars are at least set (may be placeholder values)."""
    from config import settings

    print(f"  ULTRAVOX_API_KEY: {'set' if settings.ultravox_api_key else '❌ MISSING'}")
    print(f"  SUPABASE_URL:     {'set' if settings.supabase_url else '❌ MISSING'}")
    print(f"  SUPABASE_KEY:     {'set' if settings.supabase_key else '❌ MISSING'}")
    print(f"  GROQ_API_KEY:     {'set' if settings.groq_api_key else '❌ MISSING'}")

    # This test always passes — it's informational
    assert True


def test_supabase_client_initialized():
    """Supabase client should be created (may fail if URL/key are invalid)."""
    from config import supabase

    assert supabase is not None
    print("  ✅ Supabase client initialized")


def test_prompts_loaded():
    """Interview prompts should be available."""
    from config import INTERVIEW_SYSTEM_PROMPT, INTERVIEW_PROMPTS

    assert len(INTERVIEW_SYSTEM_PROMPT) > 100
    assert "Technical" in INTERVIEW_PROMPTS
    assert "HR" in INTERVIEW_PROMPTS
    assert "Behavioral" in INTERVIEW_PROMPTS
    assert "Other" in INTERVIEW_PROMPTS
    print(f"  ✅ System prompt loaded ({len(INTERVIEW_SYSTEM_PROMPT)} chars)")
    print(f"  ✅ {len(INTERVIEW_PROMPTS)} interview prompt templates loaded")


if __name__ == "__main__":
    print("=" * 50)
    print("CONFIG TESTS")
    print("=" * 50)
    test_settings_load()
    test_env_vars_present()
    test_supabase_client_initialized()
    test_prompts_loaded()
    print("\n✅ All config tests passed!")
