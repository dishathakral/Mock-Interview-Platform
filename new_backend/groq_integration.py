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

        evaluation_prompt = f"""You are a Multi-Agent Interview Evaluation System consisting of three expert agents. Analyze this interview transcript and provide a structured, multi-dimensional evaluation.

CANDIDATE: {candidate_name}
ROLE: {role}
INTERVIEW TYPE: {interview_type}

TRANSCRIPT:
{transcript}

AGENT 1 (Technical Depth): Evaluates technical correctness, problem-solving quality, and understanding of concepts.
AGENT 2 (Communication Clarity): Evaluates explanation quality, structure, and clarity.
AGENT 3 (Confidence & Delivery): Evaluates tone, confidence, fluency, and hesitation.

Provide a JSON response with EXACTLY this structure (no additional text, just JSON):
{{
  "overall_score": 7.5,
  "problem_solving": 7,
  "communication": 8,
  "technical_depth": 7,
  "adaptability": 8,
  "full_report": "Overall summary of the candidate's performance...",
  "groq_feedback": {{
    "agent_1_feedback": "Agent 1 notes on technical correctness and depth...",
    "agent_2_feedback": "Agent 2 notes on communication structure and clarity...",
    "agent_3_feedback": "Agent 3 notes on delivery, fluency, and confidence...",
    "strengths": ["Strength 1", "Strength 2"],
    "areas_of_improvement": ["Area 1", "Area 2"],
    "actionable_suggestions": ["Suggestion 1", "Suggestion 2"]
  }}
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
