"use client";
import React, { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Loader2, ArrowRight, CheckCircle2, TrendingUp, MessageSquare, ShieldCheck, Sparkles, BarChart3, AlertCircle } from "lucide-react";

function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
    return (
        <div className={`rounded-3xl bg-gradient-to-b from-slate-800/70 to-slate-900/70 p-6 shadow-xl ring-1 ring-white/10 ${className}`}>
            {children}
        </div>
    );
}

function PrimaryButton({ children, className = "", ...props }: React.ButtonHTMLAttributes<HTMLButtonElement>) {
    return (
        <button
            className={`inline-flex items-center justify-center gap-2 rounded-2xl bg-indigo-600 px-6 py-3 font-semibold text-white shadow-lg shadow-indigo-900/30 hover:bg-indigo-500 active:scale-[.98] transition ${className}`}
            {...props}
        >
            {children}
        </button>
    );
}

export default function FeedbackPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = use(params);
    const router = useRouter();
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.getInterview(id).then((res) => {
            setData(res);
            setLoading(false);
        }).catch(err => {
            console.error(err);
            setLoading(false);
        });
    }, [id]);

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-950 text-white">
                <Loader2 className="animate-spin h-8 w-8 text-indigo-500" />
            </div>
        );
    }

    const evaluation = data?.evaluation;
    if (!evaluation) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-400">
                <p>No evaluation found. The interview might still be processing.</p>
            </div>
        );
    }

    let groqFeedback = evaluation.groq_feedback || {};
    if (typeof groqFeedback === 'string') {
        try {
            groqFeedback = JSON.parse(groqFeedback);
        } catch (e) {
            console.error("Failed to parse groq_feedback");
        }
    }

    return (
        <div className="min-h-screen w-full bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black text-slate-100 py-10 px-4">
            <div className="max-w-5xl mx-auto space-y-8">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                    <div>
                        <div className="inline-flex items-center gap-2 rounded-full border border-indigo-600/40 bg-indigo-900/40 px-4 py-2 text-sm font-semibold uppercase tracking-wide text-indigo-100 mb-4">
                            <Sparkles size={16} /> Evaluation Complete
                        </div>
                        <h1 className="text-4xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                            Interview Feedback
                        </h1>
                        <p className="text-slate-400 mt-2">
                            {data.interview?.candidate_name} • {data.interview?.role}
                        </p>
                    </div>
                    <PrimaryButton onClick={() => window.open("/dashboard", "_blank")}>
                        <BarChart3 size={18} /> View Progress Dashboard
                    </PrimaryButton>
                </div>

                {/* Score Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <Card className="flex flex-col items-center justify-center text-center p-6 bg-gradient-to-br from-indigo-900/40 to-slate-900/40 border-indigo-500/20">
                        <span className="text-sm text-slate-400 mb-2">Overall Score</span>
                        <span className="text-4xl font-bold text-white">{evaluation.overall_score}<span className="text-xl text-slate-500">/10</span></span>
                    </Card>
                    <Card className="flex flex-col items-center justify-center text-center p-6">
                        <span className="text-sm text-slate-400 mb-2">Problem Solving</span>
                        <span className="text-3xl font-bold text-slate-200">{evaluation.problem_solving}<span className="text-lg text-slate-500">/10</span></span>
                    </Card>
                    <Card className="flex flex-col items-center justify-center text-center p-6">
                        <span className="text-sm text-slate-400 mb-2">Communication</span>
                        <span className="text-3xl font-bold text-slate-200">{evaluation.communication}<span className="text-lg text-slate-500">/10</span></span>
                    </Card>
                    <Card className="flex flex-col items-center justify-center text-center p-6">
                        <span className="text-sm text-slate-400 mb-2">Technical Depth</span>
                        <span className="text-3xl font-bold text-slate-200">{evaluation.technical_depth}<span className="text-lg text-slate-500">/10</span></span>
                    </Card>
                </div>

                <div className="grid md:grid-cols-3 gap-6">
                    {/* Multi-Agent Feedback */}
                    <div className="md:col-span-2 space-y-6">
                        <Card>
                            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                                <MessageSquare className="text-indigo-400" size={20} /> Multi-Agent Analysis
                            </h3>
                            <div className="space-y-6">
                                <div className="bg-slate-950/50 rounded-2xl p-5 ring-1 ring-white/5">
                                    <div className="flex items-center gap-2 mb-2">
                                        <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                                        <h4 className="font-medium text-slate-200">Agent 1: Technical Depth</h4>
                                    </div>
                                    <p className="text-slate-400 text-sm leading-relaxed">
                                        {groqFeedback.agent_1_feedback || "No feedback provided."}
                                    </p>
                                </div>
                                <div className="bg-slate-950/50 rounded-2xl p-5 ring-1 ring-white/5">
                                    <div className="flex items-center gap-2 mb-2">
                                        <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                                        <h4 className="font-medium text-slate-200">Agent 2: Communication Clarity</h4>
                                    </div>
                                    <p className="text-slate-400 text-sm leading-relaxed">
                                        {groqFeedback.agent_2_feedback || "No feedback provided."}
                                    </p>
                                </div>
                                <div className="bg-slate-950/50 rounded-2xl p-5 ring-1 ring-white/5">
                                    <div className="flex items-center gap-2 mb-2">
                                        <div className="w-2 h-2 rounded-full bg-purple-500"></div>
                                        <h4 className="font-medium text-slate-200">Agent 3: Confidence & Delivery</h4>
                                    </div>
                                    <p className="text-slate-400 text-sm leading-relaxed">
                                        {groqFeedback.agent_3_feedback || "No feedback provided."}
                                    </p>
                                </div>
                            </div>
                        </Card>
                        
                        <Card>
                             <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                                <ShieldCheck className="text-indigo-400" size={20} /> Overall Report
                            </h3>
                            <p className="text-slate-300 leading-relaxed">
                                {evaluation.full_report}
                            </p>
                        </Card>
                    </div>

                    {/* Sidebar: Strengths & Improvements */}
                    <div className="space-y-6">
                        <Card className="bg-gradient-to-br from-emerald-900/20 to-slate-900/40 border-emerald-500/20">
                            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-emerald-400">
                                <CheckCircle2 size={18} /> Strengths
                            </h3>
                            <ul className="space-y-3">
                                {Array.isArray(groqFeedback.strengths) && groqFeedback.strengths.map((str: string, i: number) => (
                                    <li key={i} className="flex gap-3 text-sm text-slate-300">
                                        <span className="text-emerald-500 mt-0.5">•</span>
                                        <span>{str}</span>
                                    </li>
                                ))}
                            </ul>
                        </Card>

                        <Card className="bg-gradient-to-br from-rose-900/20 to-slate-900/40 border-rose-500/20">
                            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-rose-400">
                                <AlertCircle size={18} /> Areas to Improve
                            </h3>
                            <ul className="space-y-3">
                                {Array.isArray(groqFeedback.areas_of_improvement) && groqFeedback.areas_of_improvement.map((area: string, i: number) => (
                                    <li key={i} className="flex gap-3 text-sm text-slate-300">
                                        <span className="text-rose-500 mt-0.5">•</span>
                                        <span>{area}</span>
                                    </li>
                                ))}
                            </ul>
                        </Card>

                        <Card className="bg-gradient-to-br from-blue-900/20 to-slate-900/40 border-blue-500/20">
                            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-blue-400">
                                <TrendingUp size={18} /> Actionable Suggestions
                            </h3>
                            <ul className="space-y-3">
                                {Array.isArray(groqFeedback.actionable_suggestions) && groqFeedback.actionable_suggestions.map((sug: string, i: number) => (
                                    <li key={i} className="flex gap-3 text-sm text-slate-300">
                                        <span className="text-blue-500 mt-0.5"><ArrowRight size={14}/></span>
                                        <span>{sug}</span>
                                    </li>
                                ))}
                            </ul>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
}
