-- ==================== DATABASE SETUP ====================
-- Complete Interview Platform Database Schema
-- Run this entire SQL in your Supabase SQL Editor to set up the database
-- This will DROP and recreate all tables, so use only for fresh setup or complete reset

-- ==================== DROP EXISTING TABLES (RESET DATABASE) ====================
DROP VIEW IF EXISTS interview_details CASCADE;
DROP VIEW IF EXISTS interview_summaries CASCADE;
DROP TABLE IF EXISTS evaluations CASCADE;
DROP TABLE IF EXISTS transcripts CASCADE;
DROP TABLE IF EXISTS interviews CASCADE;
DROP TABLE IF EXISTS candidates CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ==================== USERS TABLE ====================
-- Stores user profiles and authentication info (linked to Supabase Auth)
CREATE TABLE users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email VARCHAR(255) UNIQUE NOT NULL,
  full_name VARCHAR(255) NOT NULL,
  company_name VARCHAR(255),
  avatar_url TEXT,
  phone VARCHAR(20),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- ==================== CANDIDATES TABLE ====================
-- Stores candidate/user information
CREATE TABLE candidates (
  id BIGSERIAL PRIMARY KEY,
  created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  email VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  phone VARCHAR(20),
  resume_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_candidates_email ON candidates(email);
CREATE INDEX idx_candidates_created_by ON candidates(created_by);
CREATE INDEX idx_candidates_created_at ON candidates(created_at);

-- ==================== INTERVIEWS TABLE ====================
-- Main interviews table with all metadata and audio context
CREATE TABLE interviews (
  id BIGSERIAL PRIMARY KEY,
  
  -- User/Owner Information
  created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Candidate Information
  candidate_name VARCHAR(255) NOT NULL,
  candidate_email VARCHAR(255) NOT NULL,
  
  -- Interview Details
  role VARCHAR(255) NOT NULL,
  interview_type VARCHAR(50) NOT NULL DEFAULT 'Technical',
  voice VARCHAR(100) NOT NULL DEFAULT 'Mark',
  agent_name VARCHAR(255) NOT NULL DEFAULT 'ALEX',
  company_name VARCHAR(255),
  
  -- Resume and Context (for RAG integration with Ultravox)
  resume TEXT,
  custom_instructions TEXT,
  notes TEXT,
  
  -- Status Tracking
  status VARCHAR(50) NOT NULL DEFAULT 'scheduled',
  call_id VARCHAR(255) UNIQUE,
  started_at TIMESTAMP WITH TIME ZONE,
  ended_at TIMESTAMP WITH TIME ZONE,
  end_reason VARCHAR(255),
  duration_seconds INT,
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX idx_interviews_created_by ON interviews(created_by);
CREATE INDEX idx_interviews_candidate_email ON interviews(candidate_email);
CREATE INDEX idx_interviews_status ON interviews(status);
CREATE INDEX idx_interviews_created_at ON interviews(created_at);
CREATE INDEX idx_interviews_call_id ON interviews(call_id);
CREATE INDEX idx_interviews_interview_type ON interviews(interview_type);

-- ==================== TRANSCRIPTS TABLE ====================
-- Stores real-time transcripts from Ultravox calls
CREATE TABLE transcripts (
  id BIGSERIAL PRIMARY KEY,
  interview_id BIGINT NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
  call_id VARCHAR(255) NOT NULL,
  
  -- Transcript Content
  speaker VARCHAR(50) NOT NULL,  -- 'user' or 'assistant'
  transcript TEXT NOT NULL,
  timestamp TIMESTAMP WITH TIME ZONE,
  
  -- Metadata
  summary TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transcripts_interview_id ON transcripts(interview_id);
CREATE INDEX idx_transcripts_call_id ON transcripts(call_id);
CREATE INDEX idx_transcripts_created_at ON transcripts(created_at);

-- ==================== EVALUATIONS TABLE ====================
-- Stores interview evaluation scores
CREATE TABLE evaluations (
  id BIGSERIAL PRIMARY KEY,
  interview_id BIGINT NOT NULL UNIQUE REFERENCES interviews(id) ON DELETE CASCADE,
  
  -- Evaluation Scores (0-10 scale)
  problem_solving NUMERIC(3,1) DEFAULT 0,
  communication NUMERIC(3,1) DEFAULT 0,
  technical_depth NUMERIC(3,1) DEFAULT 0,
  adaptability NUMERIC(3,1) DEFAULT 0,
  overall_score NUMERIC(3,2) DEFAULT 0,
  
  -- Full Evaluation Report from Groq
  full_report TEXT,
  groq_feedback TEXT,
  
  -- Evaluation Details
  notes TEXT,
  evaluator_name VARCHAR(255),
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_evaluations_interview_id ON evaluations(interview_id);
CREATE INDEX idx_evaluations_overall_score ON evaluations(overall_score);

-- ==================== VIEWS ====================

-- Interview Summary View - For quick overview of all interviews
CREATE OR REPLACE VIEW interview_summaries AS
SELECT 
  i.id,
  i.created_by,
  i.candidate_name,
  i.candidate_email,
  i.role,
  i.interview_type,
  i.voice,
  i.agent_name,
  i.company_name,
  i.status,
  i.call_id,
  i.started_at,
  i.ended_at,
  i.duration_seconds,
  ROUND(i.duration_seconds::numeric / 60, 2) as duration_minutes,
  e.overall_score,
  e.problem_solving,
  e.communication,
  e.technical_depth,
  e.adaptability,
  COALESCE(e.notes, '') as evaluation_notes,
  i.created_at
FROM interviews i
LEFT JOIN evaluations e ON i.id = e.interview_id
ORDER BY i.created_at DESC;

-- Interview Details View - Complete information for a single interview
CREATE OR REPLACE VIEW interview_details AS
SELECT 
  i.id,
  i.created_by,
  i.candidate_name,
  i.candidate_email,
  i.role,
  i.interview_type,
  i.voice,
  i.agent_name,
  i.company_name,
  i.resume,
  i.custom_instructions,
  i.notes,
  i.status,
  i.call_id,
  i.started_at,
  i.ended_at,
  i.duration_seconds,
  ROUND(i.duration_seconds::numeric / 60, 2) as duration_minutes,
  COALESCE(e.overall_score, 0) as overall_score,
  COALESCE(e.problem_solving, 0) as problem_solving,
  COALESCE(e.communication, 0) as communication,
  COALESCE(e.technical_depth, 0) as technical_depth,
  COALESCE(e.adaptability, 0) as adaptability,
  COALESCE(e.full_report, '') as full_report,
  COALESCE(e.groq_feedback, '') as groq_feedback,
  COALESCE(e.notes, '') as evaluation_notes,
  i.created_at,
  i.updated_at
FROM interviews i
LEFT JOIN evaluations e ON i.id = e.interview_id;

-- ==================== COMMENTS ====================
-- Table Documentation

COMMENT ON TABLE users IS 'Stores user profiles linked to Supabase Auth';
COMMENT ON TABLE candidates IS 'Stores candidate/user profile information';
COMMENT ON TABLE interviews IS 'Main interviews table - stores all interview metadata, resume context, and call information for Ultravox integration';
COMMENT ON TABLE transcripts IS 'Real-time transcripts from Ultravox calls - stores speaker and transcript content';
COMMENT ON TABLE evaluations IS 'Interview evaluation scores and feedback from interviewers, including Groq AI analysis';

COMMENT ON COLUMN interviews.agent_name IS 'Name of the AI agent (default: ALEX)';
COMMENT ON COLUMN interviews.company_name IS 'Company name for the interview';
COMMENT ON COLUMN interviews.interview_type IS 'Type of interview: Technical, HR, Behavioral, Other';
COMMENT ON COLUMN interviews.voice IS 'Ultravox voice: Mark, Scarlett, Kristin, Sky, Santa';
COMMENT ON COLUMN interviews.resume IS 'Candidate resume text for RAG context in Ultravox';
COMMENT ON COLUMN interviews.custom_instructions IS 'Custom system instructions for the AI interviewer';
COMMENT ON COLUMN interviews.duration_seconds IS 'Interview duration in seconds';
COMMENT ON COLUMN transcripts.speaker IS 'Speaker source: user (candidate) or assistant (Ultravox AI)';
COMMENT ON COLUMN evaluations.overall_score IS 'Overall interview score (0-10.00)';
COMMENT ON COLUMN evaluations.full_report IS 'Complete evaluation report from Groq';
COMMENT ON COLUMN evaluations.groq_feedback IS 'Detailed feedback from Groq AI analysis';

-- ==================== TRIGGERS ====================
-- Auto-create user profile when new auth user signs up

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, full_name, company_name)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email),
    COALESCE(NEW.raw_user_meta_data->>'company_name', '')
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create user profile on signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ==================== ROW LEVEL SECURITY (RLS) ====================
-- Enable RLS on all tables

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE interviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE transcripts ENABLE ROW LEVEL SECURITY;
ALTER TABLE evaluations ENABLE ROW LEVEL SECURITY;

-- Users can read their own profile
CREATE POLICY "Users can view own profile" ON users
  FOR SELECT USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile" ON users
  FOR UPDATE USING (auth.uid() = id);

-- Users can view their own candidates
CREATE POLICY "Users can view own candidates" ON candidates
  FOR SELECT USING (auth.uid() = created_by);

-- Users can create candidates
CREATE POLICY "Users can create candidates" ON candidates
  FOR INSERT WITH CHECK (auth.uid() = created_by);

-- Users can view their own interviews
CREATE POLICY "Users can view own interviews" ON interviews
  FOR SELECT USING (auth.uid() = created_by);

-- Users can create interviews
CREATE POLICY "Users can create interviews" ON interviews
  FOR INSERT WITH CHECK (auth.uid() = created_by);

-- Users can update their own interviews
CREATE POLICY "Users can update own interviews" ON interviews
  FOR UPDATE USING (auth.uid() = created_by);

-- Users can view transcripts for their interviews
CREATE POLICY "Users can view transcripts for own interviews" ON transcripts
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM interviews
      WHERE interviews.id = transcripts.interview_id
      AND interviews.created_by = auth.uid()
    )
  );

-- Users can create transcripts for their interviews
CREATE POLICY "Users can create transcripts for own interviews" ON transcripts
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM interviews
      WHERE interviews.id = transcripts.interview_id
      AND interviews.created_by = auth.uid()
    )
  );

-- Users can view evaluations for their interviews
CREATE POLICY "Users can view evaluations for own interviews" ON evaluations
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM interviews
      WHERE interviews.id = evaluations.interview_id
      AND interviews.created_by = auth.uid()
    )
  );

-- Users can create evaluations for their interviews
CREATE POLICY "Users can create evaluations for own interviews" ON evaluations
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM interviews
      WHERE interviews.id = evaluations.interview_id
      AND interviews.created_by = auth.uid()
    )
  );

-- ==================== MIGRATE EXISTING AUTH USERS ====================
-- Create user profiles for any existing auth users that don't have profiles yet

INSERT INTO public.users (id, email, full_name, company_name)
SELECT
  au.id,
  au.email,
  COALESCE(au.raw_user_meta_data->>'full_name', au.email),
  COALESCE(au.raw_user_meta_data->>'company_name', '')
FROM auth.users au
LEFT JOIN public.users pu ON au.id = pu.id
WHERE pu.id IS NULL
ON CONFLICT (id) DO NOTHING;
