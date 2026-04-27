# ==================== GROQ INTEGRATION ====================
# Using free Llama model via Groq API
# Get your free API key at: https://console.groq.com

import re
import json
import logging

from groq import Groq
from config import settings

logger = logging.getLogger(__name__)

# ==================== GROQ CLIENT ====================

if not settings.groq_api_key:
    logger.error("[Groq] GROQ_API_KEY not found in environment variables")

groq_client = Groq(api_key=settings.groq_api_key)


async def evaluate_interview_with_llama(
    candidate_name: str,
    role: str,
    interview_type: str,
    transcript: str,
) -> dict:
    """
    Evaluate an interview transcript using Groq's Llama 3.3 model.
    Returns a dict with scores and feedback.
    """
    try:
        logger.info(f"[Groq] Evaluating interview for {candidate_name}")

        if not settings.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY not configured. "
                "Please set up Groq API key at https://console.groq.com"
            )

        evaluation_prompt = f"""You are an expert interview evaluator. Analyze this interview transcript and provide a structured evaluation.

CANDIDATE: {candidate_name}
ROLE: {role}
INTERVIEW TYPE: {interview_type}

TRANSCRIPT:
{transcript}

Provide a JSON response with EXACTLY this structure (no additional text, just JSON):
{{
  "overall_score": 7.5,
  "problem_solving": 7,
  "communication": 8,
  "technical_depth": 7,
  "adaptability": 8,
  "full_report": "Candidate demonstrated solid problem-solving skills...",
  "groq_feedback": "Strengths: Clear communication, good technical understanding. Areas: Could explore more edge cases."
}}

Score Interpretation:
- 0-3: Poor
- 4-5: Below Average
- 6-7: Good
- 8-9: Excellent
- 10: Outstanding

Evaluate based on:
1. Problem-solving approach
2. Technical knowledge and depth
3. Communication clarity
4. Ability to adapt and improve based on feedback
5. Overall fit for the role"""

        logger.info("[Groq] Calling Groq API with Llama model...")

        completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": evaluation_prompt,
                }
            ],
            model="llama-3.3-70b-versatile",  # Free Llama model on Groq
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
        )

        response_text = completion.choices[0].message.content or ""
        logger.info("[Groq] Received response from Groq API")

        # Extract JSON from response
        json_match = re.search(r"\{[\s\S]*\}", response_text)
        if not json_match:
            logger.error(
                f"[Groq] Could not extract JSON from response: {response_text[:200]}"
            )
            raise ValueError(
                "Failed to parse AI evaluation response. "
                "The AI did not return valid JSON."
            )

        evaluation = json.loads(json_match.group(0))

        logger.info(f"[Groq] Evaluation complete: {evaluation.get('overall_score')}/10")
        return evaluation

    except Exception as error:
        logger.error(f"[Groq] Evaluation error: {error}")
        # Re-raise the error — no hardcoded fallbacks
        raise
