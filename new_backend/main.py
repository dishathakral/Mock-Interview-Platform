# ==================== FASTAPI APPLICATION ====================
# Main server — port of server.js (Express + WebSocket) to FastAPI
# Run with: uvicorn main:app --reload --port 8000

import logging
import json
from datetime import datetime, timezone
from typing import Any
from contextlib import asynccontextmanager

import httpx
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from config import settings, supabase, ULTRAVOX_API_URL, INTERVIEW_SYSTEM_PROMPT, INTERVIEW_PROMPTS
from models import (
    ScheduleInterviewRequest,
    StartVoiceSessionRequest,
    CreateCallRequest,
    CallEndedWebhook,
    SaveEvaluationRequest,
    StopInterviewRequest,
    SaveTranscriptRequest,
    EvaluateInterviewRequest,
    UpdateInterviewRequest,
    HealthResponse,
)
from database import (
    create_interview_session,
    update_interview_session,
    save_interview_transcript,
    save_evaluation_score,
)
from groq_integration import evaluate_interview_with_llama
from ultravox_client import UltravoxWebSocketClient

# ==================== LOGGING ====================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ==================== LIFESPAN ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"✅ Interview Platform API running on port {settings.port}")
    logger.info(f"📞 Ultravox API Key configured: {'Yes' if settings.ultravox_api_key else 'No'}")
    logger.info(f"🗄️  Database configured: {'Yes' if settings.supabase_url else 'No'}")
    logger.info(f"🤖 Groq API Key configured: {'Yes' if settings.groq_api_key else 'No'}")
    yield
    # Shutdown (if needed)


# ==================== APP ====================

app = FastAPI(
    title="Interview Platform API",
    description="Backend API for AI-powered interview platform using Ultravox",
    version="1.0.0",
    lifespan=lifespan,
)

# ==================== MIDDLEWARE ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ACTIVE SESSIONS ====================

active_sessions: dict[int, dict[str, Any]] = {}


# ==================== HELPER FUNCTIONS ====================


def _now_iso() -> str:
    """Current UTC timestamp as ISO string."""
    return datetime.now(timezone.utc).isoformat()


async def _create_ultravox_call(system_prompt: str, candidate_name: str) -> dict:
    """Call Ultravox API to create a new voice call (legacy helper)."""
    payload = {
        "systemPrompt": system_prompt,
        "model": "fixie-ai/ultravox",
        "voice": "Mark",
        "temperature": 0.3,
        "maxDuration": 1800,  # 30 minutes max
        "templateContext": {
            "candidateName": candidate_name,
        },
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            ULTRAVOX_API_URL,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": settings.ultravox_api_key,
            },
            timeout=30.0,
        )

    if response.status_code < 200 or response.status_code >= 300:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Ultravox API error ({response.status_code}): {response.text}",
        )

    return response.json()


async def _get_call_transcript(call_id: str) -> dict:
    """Fetch messages/transcript for a completed Ultravox call."""
    url = f"{ULTRAVOX_API_URL}/{call_id}/messages"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers={"X-API-Key": settings.ultravox_api_key},
            timeout=30.0,
        )

    return response.json()


# ==================== API ENDPOINTS ====================


# 0. Start Voice Session — Returns joinUrl for Ultravox SDK
@app.post("/api/start-voice-session")
async def start_voice_session(req: StartVoiceSessionRequest):
    logger.info(
        f"[API] start-voice-session request: interviewId={req.interviewId}, "
        f"candidateName={req.candidateName}, interviewType={req.interviewType}"
    )

    try:
        # Get interview details to fetch agentName and companyName
        interview_result = (
            supabase.table("interviews")
            .select("agent_name, company_name")
            .eq("id", req.interviewId)
            .single()
            .execute()
        )
        interview_data = interview_result.data if interview_result.data else {}

        agent_name = interview_data.get("agent_name") or req.agentName or "Alex"
        company_name = interview_data.get("company_name") or req.companyName or "our company"

        # Build system prompt based on interview type with RAG context (resume)
        system_prompt = INTERVIEW_SYSTEM_PROMPT

        # Use appropriate prompt template for interview type
        if req.interviewType and req.interviewType in INTERVIEW_PROMPTS:
            prompt_template = INTERVIEW_PROMPTS[req.interviewType]
            system_prompt = (
                prompt_template
                .replace("{role}", req.role or "the open position")
                .replace("{resume}", req.resume or "No resume provided")
                .replace("{customInstructions}", req.customInstructions or "")
                .replace("{agentName}", agent_name)
                .replace("{companyName}", company_name)
            )
        else:
            # Default Technical interview prompt with resume RAG context
            system_prompt = (
                INTERVIEW_SYSTEM_PROMPT
                .replace("{candidateName}", req.candidateName)
                .replace("{role}", req.role or "Senior Software Engineer")
                .replace("{resume}", req.resume or "No resume provided")
            )

        logger.info(f"[API] Using interview type: {req.interviewType}")
        logger.info(f"[API] Resume context length: {len(req.resume) if req.resume else 0}")
        logger.info(f"[API] System prompt preview: {system_prompt[:200]}...")

        # Create Ultravox call with all metadata (voice is fixed to Mark)
        call_payload = {
            "systemPrompt": system_prompt,
            "model": "fixie-ai/ultravox",
            "voice": "Mark",  # Fixed voice
            "temperature": 0.3,
            "maxDuration": "600s",

            "metadata": {
                "candidateName": str(req.candidateName or ""),
                "candidateEmail": str(req.candidateEmail or ""),
                "role": str(req.role or ""),
                "interviewType": str(req.interviewType or "Technical"),
                "agentName": str(agent_name or "Alex"),
                "companyName": str(company_name or "our company"),
                "resume": "provided" if req.resume else "not_provided",
                "interviewId": str(req.interviewId),
            },
        }


        logger.info(f"[API] Ultravox Payload: {json.dumps(call_payload, indent=2)}")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                ULTRAVOX_API_URL,
                json=call_payload,
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": str(settings.ultravox_api_key),
                },
                timeout=30.0,
            )

        logger.info(f"[API] Ultravox response status: {response.status_code}")
        logger.info(f"[API] Ultravox raw response: {response.text}")

        if response.status_code < 200 or response.status_code >= 300:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"API error {response.status_code}: {response.text}",
            )

        call_response = response.json()
        logger.info(f"[API] Ultravox parsed response: {json.dumps(call_response, indent=2)}")

        # Handle multiple possible field names from Ultravox API
        join_url = (
            call_response.get("joinUrl")
            or call_response.get("livekit_url")
            or call_response.get("livekitUrl")
        )
        call_id = call_response.get("callId") or call_response.get("id")

        logger.info(f"[API] Call created successfully.")
        logger.info(f"[API] Extracted joinUrl: {join_url}")
        logger.info(f"[API] Extracted callId: {call_id}")

        if not join_url:
            logger.error(f"[API] ERROR: No joinUrl found in response: {call_response}")
            raise HTTPException(
                status_code=500,
                detail=f"Ultravox API did not return a joinUrl. Response: {json.dumps(call_response)}",
            )

        logger.info(f"[API] Call ID: {call_id}")

        # Update interview to in_progress
        await update_interview_session(req.interviewId, {
            "status": "in_progress",
            "call_id": call_id,
            "started_at": _now_iso(),
        })

        # Return the joinUrl — let frontend use official UltravoxSession SDK
        return {
            "success": True,
            "joinUrl": join_url,
            "callId": call_id,
        }

    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"[API] Error in voice session: {error}")
        raise HTTPException(status_code=500, detail=str(error))


# ==================== LEGACY API ENDPOINTS ====================


# 1. Schedule Interview
@app.post("/api/schedule-interview")
async def schedule_interview(req: ScheduleInterviewRequest):
    try:
        if not req.candidateName or not req.candidateEmail or not req.role:
            raise HTTPException(status_code=400, detail="Missing required fields")


        # Commenting out for guest development
        # if not req.userId:
        #     raise HTTPException(status_code=401, detail="User authentication required")

        interview = await create_interview_session(
            candidate_name=req.candidateName,
            candidate_email=req.candidateEmail,
            role=req.role,
            notes=req.notes or "",
            user_id=req.userId, # Pass as is, DB will be updated to handle null
            metadata={
                "interviewType": req.interviewType or "Technical",
                "agentName": req.agentName or "Alex",
                "companyName": req.companyName,
                "resume": req.resume,
                "customInstructions": req.customInstructions,
            },
        )

        return {
            "success": True,
            "interviewId": interview[0]["id"],
            "message": "Interview scheduled successfully",
        }
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"Error scheduling interview: {error}")
        raise HTTPException(status_code=500, detail=str(error))


# 2. Create Call (Start Interview) — legacy
@app.post("/api/create-call")
async def create_call(req: CreateCallRequest):
    try:
        # Create Ultravox call
        call_data = await _create_ultravox_call(INTERVIEW_SYSTEM_PROMPT, req.candidateName)

        # Update interview status
        await update_interview_session(req.interviewId, {
            "status": "in_progress",
            "call_id": call_data.get("callId"),
            "started_at": _now_iso(),
        })

        return {
            "success": True,
            "callId": call_data.get("callId"),
            "joinUrl": call_data.get("joinUrl"),
            "message": "Call created successfully",
        }
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"Error creating call: {error}")
        raise HTTPException(status_code=500, detail=str(error))


# 3. Webhook: Call Ended
@app.post("/api/webhooks/call-ended")
async def webhook_call_ended(req: CallEndedWebhook):
    try:
        # Get transcript from Ultravox
        messages = await _get_call_transcript(req.callId)

        # Build transcript from messages
        transcript = ""
        summary = ""

        msg_list = messages.get("messages", [])
        if isinstance(msg_list, list) and msg_list:
            transcript = "\n".join(
                f"{msg.get('role', '')}: {msg.get('text', '')}" for msg in msg_list
            )
            # Last message is usually the summary
            last_message = msg_list[-1]
            summary = last_message.get("text", "")

        # Save transcript
        await save_interview_transcript(req.interviewId, req.callId, transcript, summary)

        # Update interview status
        await update_interview_session(req.interviewId, {
            "status": "completed",
            "ended_at": _now_iso(),
            "end_reason": req.endReason,
        })

        return {"success": True, "message": "Call ended and transcript saved"}
    except Exception as error:
        logger.error(f"Error processing call end: {error}")
        raise HTTPException(status_code=500, detail=str(error))


# 4. Save Evaluation Score
@app.post("/api/save-evaluation")
async def save_evaluation(req: SaveEvaluationRequest):
    try:
        evaluation = await save_evaluation_score(
            interview_id=req.interviewId,
            problem_solving=req.problemSolving or 0,
            communication=req.communication or 0,
            technical_depth=req.technicalDepth or 0,
            adaptability=req.adaptability or 0,
            notes=req.notes or "",
        )

        # Update interview with evaluation status
        await update_interview_session(req.interviewId, {"status": "evaluated"})

        return {
            "success": True,
            "evaluation": evaluation[0] if evaluation else None,
            "message": "Evaluation saved successfully",
        }
    except Exception as error:
        logger.error(f"Error saving evaluation: {error}")
        raise HTTPException(status_code=500, detail=str(error))


# 5. Stop Interview
@app.post("/api/stop-interview")
async def stop_interview(req: StopInterviewRequest, background_tasks: BackgroundTasks):
    try:
        # Get and stop the active session
        session_data = active_sessions.get(req.interviewId)
        if session_data:
            ws_client = session_data.get("wsClient")
            if ws_client:
                await ws_client.stop()
            audio_ws = session_data.get("audioWs")
            if audio_ws:
                await audio_ws.close()
            del active_sessions[req.interviewId]
            logger.info(f"[API] Interview session stopped: {req.interviewId}")

        # Update interview status to processing
        await update_interview_session(req.interviewId, {
            "status": "processing",
            "ended_at": _now_iso(),
        })

        # Trigger background processing task
        background_tasks.add_task(process_interview_background_task, req.interviewId)

        return {"success": True, "message": "Interview stopped and processing started"}
    except Exception as error:
        logger.error(f"Error stopping interview: {error}")
        raise HTTPException(status_code=500, detail=str(error))


# 5b. Get Interview Details
@app.get("/api/interview/{interview_id}")
async def get_interview(interview_id: int):
    try:
        # Get interview
        interview_result = (
            supabase.table("interviews")
            .select("*")
            .eq("id", interview_id)
            .single()
            .execute()
        )
        interview = interview_result.data

        # Get transcripts
        transcript_result = (
            supabase.table("transcripts")
            .select("*")
            .eq("interview_id", interview_id)
            .order("created_at", desc=False)
            .execute()
        )
        transcripts = transcript_result.data or []

        # Get evaluation (optional — may not exist)
        evaluation_result = (
            supabase.table("evaluations")
            .select("*")
            .eq("interview_id", interview_id)
            .execute()
        )
        evaluations = evaluation_result.data or []
        evaluation = evaluations[0] if evaluations else None

        return {
            "interview": interview,
            "transcripts": transcripts,
            "evaluation": evaluation,
        }
    except Exception as error:
        logger.error(f"Error fetching interview: {error}")
        raise HTTPException(status_code=500, detail=str(error))

from typing import Optional

# 5c. Get All Interviews (For Dashboard)
@app.get("/api/interviews")
async def get_all_interviews(userId: Optional[str] = None):
    try:
        query = supabase.table("interview_summaries").select("*").order("created_at", desc=True)
        if userId:
            query = query.eq("created_by", userId)
            
        result = query.execute()
        return {"interviews": result.data or []}
    except Exception as error:
        logger.error(f"Error fetching interviews: {error}")
        raise HTTPException(status_code=500, detail=str(error))

# 6. Save Transcript Entry
@app.post("/api/save-transcript")
async def save_transcript(req: SaveTranscriptRequest):
    try:
        logger.info(
            f"[API] Saving transcript: interviewId={req.interviewId}, "
            f"speaker={req.speaker}, textLength={len(req.transcript) if req.transcript else 0}"
        )

        if not req.interviewId or not req.speaker or not req.transcript:
            raise HTTPException(status_code=400, detail="Missing required fields")

        result = (
            supabase.table("transcripts")
            .insert(
                {
                    "interview_id": req.interviewId,
                    "call_id": req.callId or "",
                    "speaker": req.speaker,
                    "transcript": req.transcript,
                    "timestamp": req.timestamp or _now_iso(),
                    "created_at": _now_iso(),
                }
            )
            .execute()
        )

        data = result.data
        if not data:
            raise Exception("Failed to save transcript")

        logger.info(f"[API] Transcript saved successfully, ID: {data[0].get('id')}")

        return {"success": True, "transcript": data[0]}
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"[API] Error saving transcript: {error}")
        raise HTTPException(status_code=500, detail=str(error))


# 7. Evaluate Interview (AI evaluation via Groq)
@app.post("/api/evaluate-interview")
async def evaluate_interview(req: EvaluateInterviewRequest):
    try:
        if not req.interview_id or not req.transcript:
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: interview_id and transcript",
            )

        logger.info(f"[API] Evaluating interview: {req.interview_id}")

        evaluation = await evaluate_interview_with_llama(
            candidate_name=req.candidate_name or "Candidate",
            role=req.role or "Position",
            interview_type=req.interview_type or "Technical",
            transcript=req.transcript,
        )

        logger.info(f"[API] Evaluation result: {evaluation}")

        # Save evaluation to database (upsert on interview_id)
        result = (
            supabase.table("evaluations")
            .upsert(
                {
                    "interview_id": req.interview_id,
                    "problem_solving": evaluation.get("problem_solving"),
                    "communication": evaluation.get("communication"),
                    "technical_depth": evaluation.get("technical_depth"),
                    "adaptability": evaluation.get("adaptability"),
                    "overall_score": evaluation.get("overall_score"),
                    "full_report": evaluation.get("full_report"),
                    "groq_feedback": json.dumps(evaluation.get("groq_feedback")) if isinstance(evaluation.get("groq_feedback"), dict) else evaluation.get("groq_feedback"),
                    "created_at": _now_iso(),
                    "updated_at": _now_iso(),
                },
                on_conflict="interview_id",
            )
            .execute()
        )

        data = result.data
        return {
            "success": True,
            "evaluation": data[0] if data else None,
        }
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"[API] Error evaluating interview: {error}")
        raise HTTPException(status_code=500, detail=str(error))


# 8. Update Interview (PATCH)
@app.patch("/api/interview/{interview_id}")
async def update_interview(interview_id: int, req: UpdateInterviewRequest):
    try:
        logger.info(f"[API] Updating interview: {interview_id}")

        # Build updates dict from non-None fields
        updates = {k: v for k, v in req.model_dump().items() if v is not None}
        updates["updated_at"] = _now_iso()

        result = (
            supabase.table("interviews")
            .update(updates)
            .eq("id", interview_id)
            .execute()
        )

        data = result.data

        return {"success": True, "interview": data[0] if data else None}
    except Exception as error:
        logger.error(f"[API] Error in PATCH interview: {error}")
        raise HTTPException(status_code=500, detail=str(error))


# 9. Health Check
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "timestamp": _now_iso()}


# ==================== BACKGROUND TASKS ====================

async def process_interview_background_task(interview_id: int):
    try:
        logger.info(f"[Process] Starting background processing for interview {interview_id}")
        
        # Fetch interview details
        interview_result = supabase.table("interviews").select("*").eq("id", interview_id).single().execute()
        interview = interview_result.data
        if not interview or not interview.get("call_id"):
            logger.error(f"[Process] Interview {interview_id} not found or no call_id")
            await update_interview_session(interview_id, {"status": "completed"})
            return
            
        call_id = interview["call_id"]
        
        # Wait a bit for Ultravox to finish finalizing transcript
        await asyncio.sleep(4)
        
        # Fetch transcript
        messages = await _get_call_transcript(call_id)
        transcript = ""
        summary = ""
        msg_list = messages.get("results", [])
        if isinstance(msg_list, list) and msg_list:
            transcript = "\n".join(f"{msg.get('role', '').replace('MESSAGE_ROLE_', '')}: {msg.get('text', '')}" for msg in msg_list)
            last_message = msg_list[-1]
            summary = last_message.get("text", "")
            
        # Save transcript
        if transcript:
            await save_interview_transcript(interview_id, call_id, transcript, summary)
            
            # Evaluate with Groq
            logger.info(f"[Process] Evaluating transcript for {interview_id}...")
            evaluation = await evaluate_interview_with_llama(
                candidate_name=interview.get("candidate_name", "Candidate"),
                role=interview.get("role", "Position"),
                interview_type=interview.get("interview_type", "Technical"),
                transcript=transcript
            )
            
            # Save evaluation
            supabase.table("evaluations").upsert({
                "interview_id": interview_id,
                "problem_solving": evaluation.get("problem_solving"),
                "communication": evaluation.get("communication"),
                "technical_depth": evaluation.get("technical_depth"),
                "adaptability": evaluation.get("adaptability"),
                "overall_score": evaluation.get("overall_score"),
                "full_report": evaluation.get("full_report"),
                "groq_feedback": json.dumps(evaluation.get("groq_feedback")) if isinstance(evaluation.get("groq_feedback"), dict) else evaluation.get("groq_feedback"),
                "created_at": _now_iso(),
                "updated_at": _now_iso()
            }, on_conflict="interview_id").execute()
            
            # Update status to evaluated
            await update_interview_session(interview_id, {"status": "evaluated"})
            logger.info(f"[Process] Evaluation complete and saved for {interview_id}.")
        else:
            logger.warning(f"[Process] No transcript found for interview {interview_id}")
            await update_interview_session(interview_id, {"status": "completed"})
            
    except Exception as e:
        logger.error(f"[Process] Background task failed for {interview_id}: {e}")
        # Mark as completed even if evaluation fails
        await update_interview_session(interview_id, {"status": "completed"})


# ==================== WEBSOCKET ENDPOINT ====================


@app.websocket("/api/audio-stream/{interview_id}")
async def audio_stream_websocket(websocket: WebSocket, interview_id: int):
    """WebSocket endpoint for bidirectional audio streaming with Ultravox."""
    await websocket.accept()
    logger.info(f"[WebSocket] Audio stream connected for interview: {interview_id}")

    try:
        # Store the WebSocket in active sessions
        session_data = active_sessions.get(interview_id, {})
        session_data["audioWs"] = websocket
        active_sessions[interview_id] = session_data

        while True:
            # Receive audio from the frontend
            audio_buffer = await websocket.receive_bytes()
            logger.info(
                f"[WebSocket] Received audio from frontend, size: {len(audio_buffer)} bytes"
            )

            # Forward audio to Ultravox WebSocket
            if interview_id in active_sessions:
                ws_client = active_sessions[interview_id].get("wsClient")
                if ws_client:
                    await ws_client.send_audio(audio_buffer)
                else:
                    logger.warning(
                        f"[WebSocket] No active session found for interview: {interview_id}"
                    )

    except WebSocketDisconnect:
        logger.info(f"[WebSocket] Audio stream closed for interview: {interview_id}")
    except Exception as error:
        logger.error(f"[WebSocket] Audio stream error: {error}")
    finally:
        # Clean up the session when WebSocket closes
        if interview_id in active_sessions:
            ws_client = active_sessions[interview_id].get("wsClient")
            if ws_client:
                await ws_client.stop()
            del active_sessions[interview_id]
            logger.info(f"[WebSocket] Session cleaned up for interview: {interview_id}")



