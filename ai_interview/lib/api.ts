
// API Helper functions to communicate with the Python backend

const API_BASE_URL = "/api"; // Requests are proxied via Next.js to backend

export async function fetchFromApi(endpoint: string, options: RequestInit = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options.headers,
        },
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.error || "API request failed");
    }

    return response.json();
}

export const api = {
    // Interview Management
    scheduleInterview: (data: any) =>
        fetchFromApi("/schedule-interview", {
            method: "POST",
            body: JSON.stringify(data),
        }),

    startVoiceSession: (data: {
        interviewId: number;
        candidateName: string;
        interviewType?: string;
        resume?: string;
    }) =>
        fetchFromApi("/start-voice-session", {
            method: "POST",
            body: JSON.stringify(data),
        }),

    // Voice/Call Handling
    getInterview: (interviewId: string) =>
        fetchFromApi(`/interview/${interviewId}`),

    stopInterview: (interviewId: number) =>
        fetchFromApi("/stop-interview", {
            method: "POST",
            body: JSON.stringify({ interviewId }),
        }),

    saveEvaluation: (data: any) =>
        fetchFromApi("/save-evaluation", {
            method: "POST",
            body: JSON.stringify(data),
        }),
};
