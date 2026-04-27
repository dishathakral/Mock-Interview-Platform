"use client";
import React, { useEffect, useState } from "react";
import {
  Mic,
  Type as TypeIcon,
  PhoneOff,
  Timer as TimerIcon,
  MessageSquare,
  Headphones,
  Sparkles,
} from "lucide-react";


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


export default function Page() {
  const [mode, setMode] = useState<"audio" | "text">("audio");
  const [draft, setDraft] = useState("");
  const { label: elapsed } = useStopwatch(true);

  const question = "What job experience level are you targeting?";

  const aiMessages = ["Welcome! Let’s begin with a warm-up question."] as const;
  const userMessages: string[] = [];

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
                  TECHNICAL INTERVIEW
                </div>
                <div className="inline-flex items-center gap-2 rounded-full bg-white/5 px-4 py-2 text-sm text-slate-200 ring-1 ring-white/10">
                  <MessageSquare size={16} /> Whatever Role
                </div>
                <div className="inline-flex items-center gap-2 rounded-full bg-white/5 px-4 py-2 text-sm text-slate-200 ring-1 ring-white/10">
                  <Headphones size={16} /> {mode === "audio" ? "Audio mode" : "Text mode"}
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 text-sm">
            <span className="inline-flex items-center gap-1 rounded-full bg-white/5 px-3 py-1 ring-1 ring-white/10">
              <TimerIcon size={14} /> {elapsed}
            </span>
            <DangerButton onClick={() => alert("Ending call")}>
              <PhoneOff size={16} /> End Call
            </DangerButton>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="mx-auto grid max-w-6xl grid-cols-1 gap-1 px-4 py-6 lg:grid-cols-2">

        {/*AI panel*/}
      <Card className="relative overflow-hidden min-h-[380px] p-4 scale-[0.95] lg:scale-[0.9]">
      <video
      src="/184365-873181583_small.mp4" 
      autoPlay
      muted
      loop
      playsInline
      className="absolute inset-0 w-full h-full object-cover z-0 pointer-events-none"
    />

    <div className="absolute inset-0 bg-black/45 z-10 pointer-events-none" />
    <div className="relative z-20 flex flex-col justify-between h-full">
      {/* Header*/}
      <div className="flex items-center justify-between">
        <div className="text-base font-semibold text-slate-100 drop-shadow">
          AI Interviewer
        </div>
        <div className="inline-flex items-center gap-2 rounded-full border border-indigo-600/40
                        bg-indigo-900/70 px-3 py-1.5 text-xs font-semibold uppercase
                        tracking-wide text-indigo-100 ring-1 ring-white/10">
          AI
        </div>
      </div>

      {/* Message box*/}
      <div className="flex flex-col items-center w-full">
        <div className="h-15 w-[95%] overflow-auto rounded-2xl bg-black/55 p-3
                        ring-1 ring-white/10 backdrop-blur-sm">
          {aiMessages.map((t, i) => (
            <p key={i} className="mb-3 font-sans text-m text-slate-200/90">
              {t}
            </p>
          ))}
        </div>
      </div>
    </div>
  </Card>

        {/*Candidate panel*/}
      <Card className="relative overflow-hidden min-h-[380px] p-4 scale-[0.95] lg:scale-[0.9]">
        <img
          src="/d033526e749db075c7054be80a555a16.jpg"  
          alt="candidate"
          className="absolute inset-0 w-full h-full object-cover z-0 pointer-events-none"
        />
        <div className="absolute inset-0 bg-black/45 z-10 pointer-events-none" />
        <div className="relative z-20 flex flex-col justify-between h-full">
          {/*Header*/}
          <div className="flex items-center justify-between">
            <div className="text-base font-semibold text-slate-100 drop-shadow">
              You
            </div>
            <div className="inline-flex items-center gap-2 rounded-full border border-slate-600/40 
                            bg-black/60 px-3 py-1.5 text-xs font-semibold uppercase tracking-wide 
                            text-slate-100 ring-1 ring-white/10 backdrop-blur-[1px]">
              Candidate
            </div>
          </div>

          {/* Message box */}
          <div className="flex flex-col items-center w-full">
            <div className="h-15 w-[95%] overflow-auto rounded-2xl bg-black/55 p-3 
                            ring-1 ring-white/10 backdrop-blur-sm">
              {userMessages.length === 0 ? (
                <p className="text-m font-sans text-slate-300 mb-3 color-slate-400/80">
                  Your responses will appear here…
                </p>
              ) : (
                userMessages.map((t, i) => (
                  <p key={i} className="mb-3 font-sans text-m text-slate-200/90">
                    {t}
                  </p>
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
              <span className="text-sm">Current question</span>
            </div>

            <div className="mt-2 rounded-2xl bg-black/30 px-4 py-3 text-base font-medium ring-1 ring-white/10">
              {question}
            </div>

            {/* Controls */}
            <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <IconButton onClick={() => setMode((m) => (m === "audio" ? "text" : "audio"))}>
                  {mode === "audio" ? (
                    <>
                      <TypeIcon size={16} className="mr-2" /> Switch to Text
                    </>
                  ) : (
                    <>
                      <Mic size={16} className="mr-2" /> Switch to Audio
                    </>
                  )}
                </IconButton>
              </div>
              <div className="text-xs text-slate-400">
                Choose one mode only: Text or Audio.
              </div>
            </div>

            {/* Mode */}
            {mode === "audio" ? (
              <div className="mt-5 flex flex-col items-center gap-3 rounded-3xl bg-gradient-to-b from-indigo-500/10 to-indigo-900/10 p-6 ring-1 ring-inset ring-indigo-400/20">
                <button className="group relative isolate inline-flex h-20 w-20 items-center justify-center rounded-full bg-indigo-600 shadow-xl shadow-indigo-900/30 ring-1 ring-white/10 transition active:scale-95">
                  <Mic className="drop-shadow" />
                  <div className="absolute -inset-1 -z-10 rounded-full bg-indigo-600/30 blur-lg opacity-60 group-hover:opacity-80" />
                </button>
                <div className="text-sm text-slate-300">Tap to answer via audio</div>
              </div>
            ) : (
              <div className="mt-5 rounded-3xl bg-black/30 p-4 ring-1 ring-white/10">
                <div className="flex items-center gap-2">
                  <input
                    value={draft}
                    onChange={(e) => setDraft(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && draft.trim() && setDraft("")}
                    placeholder="Type your answer here…"
                    className="flex-1 rounded-2xl bg-slate-950/80 px-4 py-3 text-sm placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                  <PrimaryButton onClick={() => setDraft("")}>
                    <TypeIcon size={16} /> Send
                  </PrimaryButton>
                </div>
              </div>
            )}
          </Card>
        </div>
      </main>

      {/* Bottom Section */}
      <footer className="mx-auto mb-10 mt-2 flex max-w-6xl items-center justify-center px-4">
        <DangerButton onClick={() => alert("Ending call")}>
          <PhoneOff size={18} /> End Call
        </DangerButton>
      </footer>
    </div>
  );
}
