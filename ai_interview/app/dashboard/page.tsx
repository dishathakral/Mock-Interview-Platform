"use client";
import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Loader2, TrendingUp, BarChart3, Clock, Target, Calendar } from "lucide-react";
import Link from "next/link";

function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
    return (
        <div className={`rounded-3xl bg-gradient-to-b from-slate-800/70 to-slate-900/70 p-6 shadow-xl ring-1 ring-white/10 ${className}`}>
            {children}
        </div>
    );
}

export default function DashboardPage() {
    const [interviews, setInterviews] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetching all interviews (no userId supplied since auth is disabled for dev)
        api.getInterviews().then((data) => {
            setInterviews(data.interviews || []);
            setLoading(false);
        }).catch(err => {
            console.error(err);
            setLoading(false);
        });
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-950 text-white">
                <Loader2 className="animate-spin h-8 w-8 text-indigo-500" />
            </div>
        );
    }

    const completedInterviews = interviews.filter(i => i.overall_score > 0);
    const avgScore = completedInterviews.length > 0
        ? (completedInterviews.reduce((acc, curr) => acc + Number(curr.overall_score), 0) / completedInterviews.length).toFixed(1)
        : "0.0";

    return (
        <div className="min-h-screen w-full bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black text-slate-100 py-10 px-4">
            <div className="max-w-6xl mx-auto space-y-8">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                    <div>
                        <div className="inline-flex items-center gap-2 rounded-full border border-indigo-600/40 bg-indigo-900/40 px-4 py-2 text-sm font-semibold uppercase tracking-wide text-indigo-100 mb-4">
                            <BarChart3 size={16} /> Progress Dashboard
                        </div>
                        <h1 className="text-4xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                            Interview Performance
                        </h1>
                        <p className="text-slate-400 mt-2">
                            Track your historical performance and improvements over time.
                        </p>
                    </div>
                </div>

                {/* Stats Overview */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card className="flex flex-col p-6 bg-gradient-to-br from-indigo-900/40 to-slate-900/40 border-indigo-500/20">
                        <div className="flex items-center gap-2 text-slate-400 mb-2">
                            <Target size={18} />
                            <span className="text-sm font-medium uppercase tracking-wider">Average Score</span>
                        </div>
                        <span className="text-5xl font-bold text-white">{avgScore}<span className="text-2xl text-slate-500">/10</span></span>
                    </Card>
                    <Card className="flex flex-col p-6">
                        <div className="flex items-center gap-2 text-slate-400 mb-2">
                            <TrendingUp size={18} />
                            <span className="text-sm font-medium uppercase tracking-wider">Total Completed</span>
                        </div>
                        <span className="text-5xl font-bold text-slate-200">{completedInterviews.length}</span>
                    </Card>
                    <Card className="flex flex-col p-6">
                        <div className="flex items-center gap-2 text-slate-400 mb-2">
                            <Clock size={18} />
                            <span className="text-sm font-medium uppercase tracking-wider">Total Sessions</span>
                        </div>
                        <span className="text-5xl font-bold text-slate-200">{interviews.length}</span>
                    </Card>
                </div>

                {/* Interview History */}
                <Card className="p-0 overflow-hidden">
                    <div className="p-6 border-b border-white/10">
                        <h3 className="text-xl font-semibold flex items-center gap-2">
                            <Calendar className="text-indigo-400" size={20} /> Interview History
                        </h3>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-slate-900/50 border-b border-white/10 text-sm text-slate-400 uppercase tracking-wider">
                                    <th className="p-4 font-medium">Date</th>
                                    <th className="p-4 font-medium">Role</th>
                                    <th className="p-4 font-medium">Type</th>
                                    <th className="p-4 font-medium">Status</th>
                                    <th className="p-4 font-medium text-right">Score</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {interviews.length === 0 ? (
                                    <tr>
                                        <td colSpan={5} className="p-8 text-center text-slate-500">
                                            No interviews found.
                                        </td>
                                    </tr>
                                ) : (
                                    interviews.map((interview: any) => (
                                        <tr key={interview.id} className="hover:bg-white/5 transition group">
                                            <td className="p-4 text-slate-300">
                                                {new Date(interview.created_at).toLocaleDateString()}
                                            </td>
                                            <td className="p-4 font-medium text-slate-200">
                                                {interview.role}
                                            </td>
                                            <td className="p-4 text-slate-400">
                                                {interview.interview_type}
                                            </td>
                                            <td className="p-4">
                                                <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                                                    interview.status === 'evaluated' ? 'bg-emerald-500/10 text-emerald-400 ring-1 ring-emerald-500/20' :
                                                    interview.status === 'processing' ? 'bg-yellow-500/10 text-yellow-400 ring-1 ring-yellow-500/20' :
                                                    'bg-slate-500/10 text-slate-400 ring-1 ring-slate-500/20'
                                                }`}>
                                                    {interview.status}
                                                </span>
                                            </td>
                                            <td className="p-4 text-right">
                                                {interview.status === 'evaluated' ? (
                                                    <Link href={`/interview/${interview.id}/feedback`} className="inline-flex items-center gap-2 font-bold text-indigo-400 hover:text-indigo-300 transition">
                                                        {interview.overall_score}/10
                                                    </Link>
                                                ) : (
                                                    <span className="text-slate-600">-</span>
                                                )}
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </Card>
            </div>
        </div>
    );
}
