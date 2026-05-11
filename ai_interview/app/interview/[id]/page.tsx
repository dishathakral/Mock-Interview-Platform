
"use client";
import React, { useEffect, useState, useRef, use } from "react";
import {
    Mic,
    Type as TypeIcon,
    PhoneOff,
    Timer as TimerIcon,
    MessageSquare,
    Headphones,
    Sparkles,
    Loader2,
} from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { UltravoxSession, UltravoxSessionStatus } from "ultravox-client";
import { toast } from "sonner";


// --- UI Components (reused) ---

type BtnProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
    children: React.ReactNode;
};

function IconButton({ children, className = "", ...props }: BtnProps) {
    return (
        <button
            className={`cursor-pointer inline-flex items-center justify-center rounded-2xl px-4 py-2 font-semibold shadow-sm ring-1 ring-white/10 hover:bg-white/10 active:scale-[.98] transition ${className}`}
            {...props}
        >
            {children}
        </button>
    );
}

function PrimaryButton({ children, className = "", ...props }: BtnProps) {
    return (
        <button
            className={`inline-flex items-center justify-center gap-2 rounded-2xl bg-indigo-600 px-5 py-2.5 font-semibold text-white shadow-lg shadow-indigo-900/30 hover:bg-indigo-500 active:scale-[.98] transition ${className}`}
            {...props}
        >
            {children}
        </button>
    );
}

function DangerButton({ children, className = "", ...props }: BtnProps) {
    return (
        <button
            className={`cursor-pointer inline-flex items-center justify-center gap-2 rounded-2xl bg-rose-600 px-6 py-3 font-semibold text-white shadow-lg shadow-rose-900/30 hover:bg-rose-500 active:scale-[.98] transition ${className}`}
            {...props}
        >
            {children}
        </button>
    );
}

function Card({
    children,
    className = "",
}: {
    children: React.ReactNode;
    className?: string;
}) {
    return (
        <div
            className={`rounded-3xl bg-gradient-to-b from-slate-800/70 to-slate-900/70 p-6 lg:p-8 ring-1 ring-white/10 shadow-xl ${className}`}
        >
            {children}
        </div>
    );
}

function useStopwatch(running = true) {
    const [seconds, setSeconds] = useState(0);
    useEffect(() => {
        if (!running) return;
        const id = setInterval(() => setSeconds((s) => s + 1), 1000);
        return () => clearInterval(id);
    }, [running]);
    const hh = String(Math.floor(seconds / 3600)).padStart(2, "0");
    const mm = String(Math.floor((seconds % 3600) / 60)).padStart(2, "0");
    const ss = String(seconds % 60).padStart(2, "0");
    return { label: `${hh}:${mm}:${ss}` };
}


export default function InterviewPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = use(params);
    const router = useRouter();
    const [mode, setMode] = useState<"audio" | "text">("audio");
    const [status, setStatus] = useState<UltravoxSessionStatus | "disconnected" | "connecting" | "processing">("disconnected");
    const [interview, setInterview] = useState<any>(null);
    const [transcripts, setTranscripts] = useState<any[]>([]);
    const sessionRef = useRef<UltravoxSession | null>(null);
    const isProcessingRef = useRef(false);

    const { label: elapsed } = useStopwatch(status === "speaking" || status === "listening" || status === "thinking");

    useEffect(() => {
        // Fetch interview details
        api.getInterview(id).then((data) => {
            setInterview(data.interview);
            // Pre-fill transcripts if any
            if (data.transcripts) {
                setTranscripts(data.transcripts.map((t: any) => ({
                    role: t.speaker === 'user' ? 'user' : 'agent',
                    text: t.transcript
                })));
            }
        }).catch(console.error);

        return () => {
            if (sessionRef.current) {
                sessionRef.current.leaveCall();
            }
        };
    }, [id]);

    // Polling fallback to ensure transcripts are always updated from session state
    useEffect(() => {
        if (status === "disconnected" || !sessionRef.current) return;

        const interval = setInterval(() => {
            if (sessionRef.current?.transcripts) {
                // Only update if length changed or we want to be safe
                setTranscripts([...sessionRef.current.transcripts]);
            }
        }, 1500);

        return () => clearInterval(interval);
    }, [status]);

    // Polling for processing completion
    useEffect(() => {
        if (status !== "processing") return;

        const interval = setInterval(async () => {
            try {
                const data = await api.getInterview(id);
                if (data.interview?.status === "evaluated" || data.interview?.status === "completed") {
                    clearInterval(interval);
                    router.push(`/interview/${id}/feedback`);
                }
            } catch (err) {
                console.error("Error polling interview status:", err);
            }
        }, 3000);

        return () => clearInterval(interval);
    }, [status, id, router]);

    const startCall = async () => {
        if (!interview) return;
        setStatus("connecting");

        try {
            // 1. Get join URL from backend
            const response = await api.startVoiceSession({
                interviewId: interview.id,
                candidateName: interview.candidate_name,
                interviewType: interview.interview_type,
                resume: interview.resume // If available
            });

            if (!response.joinUrl) {
                throw new Error("No join URL returned");
            }

            // 2. Initialize Ultravox Session
            const session = new UltravoxSession();
            sessionRef.current = session;

            // 3. Setup listeners
            session.addEventListener("status", () => {
                console.log("[Ultravox] Session status:", session.status);
                if (isProcessingRef.current) return; // Prevent overwriting our 'processing' state
                setStatus(session.status);
                // Sync transcripts on status change too
                if (session.transcripts) {
                    setTranscripts([...session.transcripts]);
                }
            });

            session.addEventListener("transcript", (event: any) => {
                // Ultravox SDK events can be CustomEvents with 'detail'
                const transcriptData = event.detail || event;
                console.log("[Ultravox] Transcript event received:", transcriptData);

                if (session.transcripts) {
                    console.log("[Ultravox] Current session transcripts:", session.transcripts);
                    setTranscripts([...session.transcripts]);
                } else {
                    console.warn("[Ultravox] session.transcripts is missing or empty.");
                }
            });

            session.addEventListener("error", (event: any) => {
                const errorData = (event as any).detail || event;
                console.error("[Ultravox] Session error:", errorData);
                toast.error("Connection error");
                setStatus("disconnected");
            });

            // 4. Join Call
            await session.joinCall(response.joinUrl);
            toast.success("Connected to AI Interviewer");

        } catch (error: any) {
            console.error("Failed to start call:", error);
            toast.error("Failed to start call: " + error.message);
            setStatus("disconnected");
        }
    };

    const endCall = async () => {
        console.log("End Call button clicked");
        toast.info("Ending call and starting evaluation...");
        isProcessingRef.current = true;
        setStatus("processing");
        
        try {
            if (sessionRef.current) {
                sessionRef.current.leaveCall();
            }
        } catch (e) {
            console.error("Error leaving call:", e);
        }
        
        try {
            await api.stopInterview(Number(id));
        } catch (e) {
            console.error("Error stopping interview:", e);
            toast.error("Failed to process interview. Backend error.");
            isProcessingRef.current = false;
            setStatus("disconnected");
        }
    };


    if (!interview) {
        return <div className="min-h-screen flex items-center justify-center bg-slate-950 text-white">
            <Loader2 className="animate-spin h-8 w-8" />
        </div>;
    }

    const aiMessages = transcripts
        .filter(t => {
            const s = (t.role || t.speaker || "").toLowerCase();
            return s === 'agent' || s === 'assistant' || s === 'ai';
        })
        .map(t => t.text || t.transcript || "");

    const userMessages = transcripts
        .filter(t => {
            const s = (t.role || t.speaker || "").toLowerCase();
            return s === 'user' || s === 'candidate';
        })
        .map(t => t.text || t.transcript || "");
    const lastAiMessage = aiMessages[aiMessages.length - 1] || "Hello! I'm your AI interviewer.";

    return (
        <div className="min-h-screen w-full bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black text-slate-100">
            {/* Top strip */}
            <header className="sticky top-0 z-10 border-b border-white/10 bg-black/40 backdrop-blur-sm">
                <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
                    <div className="flex items-center gap-3">
                        <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-indigo-600/80 ring-1 ring-white/20">
                            <Sparkles size={18} />
                        </span>

                        <div className="flex flex-col leading-tight">
                            <div className="flex flex-wrap items-center gap-2">
                                <div className="inline-flex items-center gap-2 rounded-full border border-indigo-600/40 bg-indigo-900/40 px-4 py-2 text-sm font-semibold uppercase tracking-wide text-indigo-100">
                                    {interview.interview_type || "Technical"} Interview
                                </div>
                                <div className="inline-flex items-center gap-2 rounded-full bg-white/5 px-4 py-2 text-sm text-slate-200 ring-1 ring-white/10">
                                    {status === "disconnected" ? "Not Started" : status}
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center gap-2 text-sm">
                        <span className="inline-flex items-center gap-1 rounded-full bg-white/5 px-3 py-1 ring-1 ring-white/10">
                            <TimerIcon size={14} /> {elapsed}
                        </span>
                        <DangerButton onClick={endCall}>
                            <PhoneOff size={16} /> End Call
                        </DangerButton>
                    </div>
                </div>
            </header>

            {/* Main content */}
            <main className="mx-auto grid max-w-6xl grid-cols-1 gap-1 px-4 py-6 lg:grid-cols-2">

                {/*AI panel*/}
                <Card className="relative overflow-hidden min-h-[380px] p-4 scale-[0.95] lg:scale-[0.9]">
                    <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/20 to-purple-900/20 z-0 pointer-events-none" />
                    <div className="relative z-20 flex flex-col justify-between h-full">
                        {/* Header*/}
                        <div className="flex items-center justify-between">
                            <div className="text-base font-semibold text-slate-100 drop-shadow">
                                AI Interviewer ({interview.agent_name || "Alex"})
                            </div>
                            <div className="inline-flex items-center gap-2 rounded-full border border-indigo-600/40
                        bg-indigo-900/70 px-3 py-1.5 text-xs font-semibold uppercase
                        tracking-wide text-indigo-100 ring-1 ring-white/10">
                                AI
                            </div>
                        </div>

                        {/* Message box*/}
                        <div className="flex flex-col items-center w-full mt-auto">
                            <div className="h-40 w-full overflow-y-auto rounded-2xl bg-black/55 p-4
                        ring-1 ring-white/10 backdrop-blur-sm scrollbar-thin scrollbar-thumb-indigo-600/50">
                                {aiMessages.length === 0 ? (
                                    <p className="text-slate-400 italic">Waiting for connection...</p>
                                ) : (
                                    aiMessages.map((msg, i) => (
                                        <p key={i} className="mb-2 text-slate-200 last:text-white last:font-medium">{msg}</p>
                                    ))
                                )}
                            </div>
                        </div>
                    </div>
                </Card>

                {/*Candidate panel*/}
                <Card className="relative overflow-hidden min-h-[380px] p-4 scale-[0.95] lg:scale-[0.9]">
                    <div className="absolute inset-0 bg-gradient-to-bl from-slate-800/20 to-black z-0 pointer-events-none" />
                    <div className="relative z-20 flex flex-col justify-between h-full">
                        {/*Header*/}
                        <div className="flex items-center justify-between">
                            <div className="text-base font-semibold text-slate-100 drop-shadow">
                                You ({interview.candidate_name})
                            </div>
                            <div className="inline-flex items-center gap-2 rounded-full border border-slate-600/40 
                            bg-black/60 px-3 py-1.5 text-xs font-semibold uppercase tracking-wide 
                            text-slate-100 ring-1 ring-white/10 backdrop-blur-[1px]">
                                Candidate
                            </div>
                        </div>

                        {/* Message box */}
                        <div className="flex flex-col items-center w-full mt-auto">
                            <div className="h-40 w-full overflow-y-auto rounded-2xl bg-black/55 p-4 
                            ring-1 ring-white/10 backdrop-blur-sm scrollbar-thin scrollbar-thumb-slate-600/50">
                                {userMessages.length === 0 ? (
                                    <p className="text-slate-400 italic">Your spoken text will appear here...</p>
                                ) : (
                                    userMessages.map((msg, i) => (
                                        <p key={i} className="mb-2 text-slate-200 last:text-white">{msg}</p>
                                    ))
                                )}
                            </div>
                        </div>
                    </div>
                </Card>

                {/*Question + controls */}
                <div className="lg:col-span-2">
                    <Card className="p-4 md:p-5">
                        <div className="flex items-center gap-2 text-slate-200/90">
                            <MessageSquare size={16} />
                            <span className="text-sm">Latest from AI</span>
                        </div>

                        <div className="mt-2 rounded-2xl bg-black/30 px-4 py-3 text-base font-medium ring-1 ring-white/10 min-h-[60px]">
                            {lastAiMessage}
                        </div>

                        {/* Controls */}
                        <div className="mt-6 flex flex-col items-center justify-center gap-4">

                            {status === "disconnected" ? (
                                <PrimaryButton onClick={startCall} className="px-8 py-4 text-lg">
                                    <Mic className="mr-2" /> Start Interview
                                </PrimaryButton>
                            ) : status === "processing" ? (
                                <div className="flex flex-col items-center gap-2">
                                    <Loader2 className="animate-spin h-8 w-8 text-indigo-500" />
                                    <p className="text-zinc-400">Processing your interview...</p>
                                </div>
                            ) : (
                                <div className="flex flex-col items-center gap-2">
                                    <div className={`rounded-full p-4 ${status === 'listening' ? 'bg-red-500/20 animate-pulse' : 'bg-indigo-600'}`}>
                                        <Mic className={`h-8 w-8 ${status === 'listening' ? 'text-red-400' : 'text-white'}`} />
                                    </div>
                                    <p className="text-zinc-400 capitalize">{status}...</p>
                                </div>
                            )}
                        </div>
                    </Card>
                </div>
            </main>
        </div>
    );
}
