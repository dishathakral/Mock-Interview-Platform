# ==================== PYDANTIC MODELS ====================
# Request and response schemas for all API endpoints

from pydantic import BaseModel, Field
from typing import Optional, Any


# ==================== REQUEST MODELS ====================


class ScheduleInterviewRequest(BaseModel):
    candidateName: str
    candidateEmail: str
    role: str
    interviewType: Optional[str] = "Technical"
    agentName: Optional[str] = "Aarav"
    companyName: Optional[str] = None
    resume: Optional[str] = None
    customInstructions: Optional[str] = None
    notes: Optional[str] = ""
    userId: Optional[str] = None


class StartVoiceSessionRequest(BaseModel):
    interviewId: int
    candidateName: str
    candidateEmail: Optional[str] = None
    role: Optional[str] = None
    interviewType: Optional[str] = "Technical"
    voice: Optional[str] = "Mark"
    resume: Optional[str] = None
    customInstructions: Optional[str] = None
    notes: Optional[str] = None
    agentName: Optional[str] = "Alex"
    companyName: Optional[str] = "our company"


class CreateCallRequest(BaseModel):
    interviewId: int
    candidateName: str


class CallEndedWebhook(BaseModel):
    callId: str
    interviewId: int
    endReason: Optional[str] = None


class SaveEvaluationRequest(BaseModel):
    interviewId: int
    problemSolving: Optional[float] = 0
    communication: Optional[float] = 0
    technicalDepth: Optional[float] = 0
    adaptability: Optional[float] = 0
    notes: Optional[str] = ""


class StopInterviewRequest(BaseModel):
    interviewId: int


class SaveTranscriptRequest(BaseModel):
    interviewId: int
    callId: Optional[str] = ""
    speaker: str
    transcript: str
    timestamp: Optional[str] = None


class EvaluateInterviewRequest(BaseModel):
    interview_id: int
    candidate_name: Optional[str] = "Candidate"
    role: Optional[str] = "Position"
    interview_type: Optional[str] = "Technical"
    transcript: str


class UpdateInterviewRequest(BaseModel):
    """Allows partial updates — all fields optional."""
    status: Optional[str] = None
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    role: Optional[str] = None
    interview_type: Optional[str] = None
    agent_name: Optional[str] = None
    company_name: Optional[str] = None
    resume: Optional[str] = None
    custom_instructions: Optional[str] = None
    notes: Optional[str] = None
    call_id: Optional[str] = None
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    end_reason: Optional[str] = None
    duration_seconds: Optional[int] = None


# ==================== RESPONSE MODELS ====================


class SuccessResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None


class VoiceSessionResponse(SuccessResponse):
    joinUrl: str
    callId: str


class ScheduleInterviewResponse(SuccessResponse):
    interviewId: int


class CreateCallResponse(SuccessResponse):
    callId: str
    joinUrl: str


class SaveEvaluationResponse(SuccessResponse):
    evaluation: Optional[dict] = None


class InterviewDetailResponse(BaseModel):
    interview: Optional[dict] = None
    transcripts: list = []
    evaluation: Optional[dict] = None


class SaveTranscriptResponse(SuccessResponse):
    transcript: Optional[dict] = None


class EvaluateInterviewResponse(SuccessResponse):
    evaluation: Optional[dict] = None


class UpdateInterviewResponse(SuccessResponse):
    interview: Optional[dict] = None


class HealthResponse(BaseModel):
    status: str = "ok"
    timestamp: str


class ErrorResponse(BaseModel):
    error: str
