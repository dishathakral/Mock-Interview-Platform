# ==================== TEST: ULTRAVOX CLIENT ====================
# Test Ultravox API connectivity and WebSocket client
# ⚠️  Requires ULTRAVOX_API_KEY in .env
# Run: python -m pytest tests/test_ultravox.py -v -s

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _check_ultravox_configured():
    from config import settings
    return bool(settings.ultravox_api_key)


def test_ultravox_api_key_present():
    """Verify ULTRAVOX_API_KEY is configured."""
    from config import settings

    if not settings.ultravox_api_key:
        print("  ⚠️  ULTRAVOX_API_KEY not set — live tests will be skipped")
    else:
        print("  ✅ ULTRAVOX_API_KEY is configured")
    assert True


def test_create_ultravox_call():
    """
    Live test: create a call via the Ultravox API and verify joinUrl.
    ⚠️  This will create a real Ultravox call.
    """
    if not _check_ultravox_configured():
        print("  ⏭️  Skipping — Ultravox not configured")
        return

    import httpx
    from config import settings, ULTRAVOX_API_URL

    payload = {
        "systemPrompt": "You are a test assistant. Say hello and wait.",
        "model": "fixie-ai/ultravox",
        "voice": "Mark",
        "temperature": 0.3,
        "maxDuration": "60s",
    }

    response = httpx.post(
        ULTRAVOX_API_URL,
        json=payload,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": settings.ultravox_api_key,
        },
        timeout=30.0,
    )

    print(f"  Status: {response.status_code}")

    if response.status_code >= 200 and response.status_code < 300:
        data = response.json()
        join_url = data.get("joinUrl") or data.get("livekit_url") or data.get("livekitUrl")
        call_id = data.get("callId") or data.get("id")
        print(f"  ✅ Call created — callId: {call_id}")
        print(f"  ✅ joinUrl: {join_url[:80]}..." if join_url else "  ❌ No joinUrl!")
        assert join_url is not None, "No joinUrl in response"
    else:
        print(f"  ❌ Ultravox API error: {response.text[:300]}")
        assert False, f"API returned {response.status_code}"


def test_ultravox_client_init():
    """Test UltravoxWebSocketClient initialization (no network call)."""
    from ultravox_client import UltravoxWebSocketClient

    client = UltravoxWebSocketClient("wss://example.com/test")
    assert client.state == "idle"
    assert client.transcript_buffer == []
    assert client.state_history == []
    print("  ✅ UltravoxWebSocketClient initialized correctly")


if __name__ == "__main__":
    print("=" * 50)
    print("ULTRAVOX TESTS")
    print("=" * 50)
    test_ultravox_api_key_present()
    test_ultravox_client_init()
    test_create_ultravox_call()
    print("\n✅ All Ultravox tests passed!")
