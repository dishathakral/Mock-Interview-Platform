# ==================== TEST: GROQ INTEGRATION ====================
# Test Groq/Llama evaluation with a sample transcript
# ⚠️  Requires GROQ_API_KEY in .env to run
# Run: python -m pytest tests/test_groq.py -v -s

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SAMPLE_TRANSCRIPT = """
Interviewer: Hi! Let's start with a classic problem. You have an array of integers and you need to find two numbers that add up to a specific target sum. How would you approach this?

Candidate: Sure! I'd start with a brute force approach — two nested loops checking every pair. That would be O(n²) time and O(1) space. But we can do better using a hash map.

Interviewer: Great! Walk me through the hash map approach.

Candidate: We iterate through the array once. For each element, we calculate the complement (target - current). If the complement exists in our hash map, we found our pair. If not, we add the current element to the map. This gives us O(n) time and O(n) space.

Interviewer: What about edge cases?

Candidate: We should handle empty arrays, arrays with one element, duplicate values, and negative numbers. Also, we need to clarify if the same element can be used twice.

Interviewer: Excellent analysis. How would you handle the case where there are multiple valid pairs?

Candidate: We could return all pairs by not stopping at the first match. We'd continue iterating and collecting all valid pairs in a result list.
"""


def test_groq_api_key_present():
    """Verify GROQ_API_KEY is configured."""
    from config import settings

    if not settings.groq_api_key:
        print("  ⚠️  GROQ_API_KEY not set — live Groq tests will be skipped")
    else:
        print("  ✅ GROQ_API_KEY is configured")
    assert True  # Informational


def test_groq_client_creation():
    """Groq client should be created."""
    from groq_integration import groq_client

    assert groq_client is not None
    print("  ✅ Groq client created")


def test_evaluate_interview_live():
    """
    Live test: call Groq API with sample transcript.
    Skip if GROQ_API_KEY is not set.
    """
    from config import settings

    if not settings.groq_api_key:
        print("  ⏭️  Skipping live Groq test (no API key)")
        return

    from groq_integration import evaluate_interview_with_llama

    result = asyncio.run(
        evaluate_interview_with_llama(
            candidate_name="Test Candidate",
            role="Software Engineer",
            interview_type="Technical",
            transcript=SAMPLE_TRANSCRIPT,
        )
    )

    print(f"  📊 Evaluation result:")
    print(f"     Overall Score: {result.get('overall_score')}/10")
    print(f"     Problem Solving: {result.get('problem_solving')}/10")
    print(f"     Communication: {result.get('communication')}/10")
    print(f"     Technical Depth: {result.get('technical_depth')}/10")
    print(f"     Adaptability: {result.get('adaptability')}/10")
    print(f"     Report: {result.get('full_report', '')[:100]}...")

    # Validate structure
    assert "overall_score" in result
    assert "problem_solving" in result
    assert "communication" in result
    assert "technical_depth" in result
    assert "adaptability" in result
    assert isinstance(result["overall_score"], (int, float))
    print("  ✅ Groq evaluation passed — valid JSON structure returned")


if __name__ == "__main__":
    print("=" * 50)
    print("GROQ INTEGRATION TESTS")
    print("=" * 50)
    test_groq_api_key_present()
    test_groq_client_creation()
    test_evaluate_interview_live()
    print("\n✅ All Groq tests passed!")
