# Mock Interview Platform

This is a comprehensive platform for AI-driven mock interviews, featuring a modern web frontend and a robust Python backend.

## Project Structure

The project is divided into two main modules:

### 1. `ai_interview` (Frontend)
This is a modern web frontend built with **Next.js** (React) and styled with Tailwind CSS. It provides the user interface where candidates can schedule interviews, view active sessions, and engage with the AI interviewer. 
- Communicates with the backend API to manage state.
- Handles audio streaming to and from the user.

### 2. `new_backend` (Backend)
This is the core server and API built with **Python** and **FastAPI**. It handles all the business logic, database interactions, and integrations with external AI services.
- **Database:** Integrates with Supabase for storing interview records, transcripts, and evaluation scores.
- **AI Integrations:** Connects with Ultravox API for real-time voice conversations and Groq for generating post-interview evaluations using LLMs.
- Provides WebSocket endpoints for real-time audio streaming.

---

## How to Run the Project Locally

To get the full application running, you need to start both the backend and frontend servers in separate terminal windows.

### Step 1: Start the Backend Server

1. Open a terminal and navigate to the backend folder:
   ```bash
   cd new_backend
   ```
2. *(Optional but recommended)* Activate your Python virtual environment. If you are using `venv`:
   ```bash
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```
3. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI development server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   The backend will now be running at `http://localhost:8000`.

### Step 2: Start the Frontend Server

1. Open a **new, separate terminal** and navigate to the frontend folder:
   ```bash
   cd ai_interview
   ```
2. Install the Node.js dependencies:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
   The frontend will now be accessible in your browser at `http://localhost:3000`.

---

## Configuration

Make sure your environment variables are set up properly before running. 
- **Backend:** Ensure `new_backend/.env` is populated with the correct API keys (Supabase, Ultravox, Groq, etc.).
- **Frontend:** Ensure `ai_interview/.env.local` has the corresponding client variables needed to connect to the backend.
