-- Create tables for Career Compass AI
-- Run these commands in your Supabase SQL editor

-- CV Records table
CREATE TABLE cv_records (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_content TEXT, -- Base64 encoded file content
    file_type TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    name TEXT,
    email TEXT,
    phone TEXT,
    location TEXT,
    experience TEXT,
    skills TEXT, -- JSON array as text
    education TEXT,
    last_two_jobs TEXT, -- JSON array as text
    summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Career Paths table
CREATE TABLE career_paths (
    id SERIAL PRIMARY KEY,
    cv_record_id INTEGER REFERENCES cv_records(id),
    user_id TEXT NOT NULL,
    job_title TEXT NOT NULL,
    experience_level TEXT NOT NULL,
    career_path_data TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Skill Gap Analysis table
CREATE TABLE skill_gaps (
    id SERIAL PRIMARY KEY,
    cv_record_id INTEGER REFERENCES cv_records(id),
    user_id TEXT NOT NULL,
    job_description TEXT NOT NULL,
    analysis_data TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Resume Optimizations table
CREATE TABLE resume_optimizations (
    id SERIAL PRIMARY KEY,
    cv_record_id INTEGER REFERENCES cv_records(id),
    user_id TEXT NOT NULL,
    job_description TEXT NOT NULL,
    optimization_data TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_cv_records_user_id ON cv_records(user_id);
CREATE INDEX idx_career_paths_user_id ON career_paths(user_id);
CREATE INDEX idx_skill_gaps_user_id ON skill_gaps(user_id);
CREATE INDEX idx_resume_optimizations_user_id ON resume_optimizations(user_id);

-- Enable Row Level Security (RLS)
ALTER TABLE cv_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE career_paths ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_gaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE resume_optimizations ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (adjust based on your authentication setup)
-- These policies ensure users can only access their own data

-- CV Records policies
CREATE POLICY "Users can view their own CV records" ON cv_records
    FOR SELECT USING (user_id = auth.uid()::text);

CREATE POLICY "Users can insert their own CV records" ON cv_records
    FOR INSERT WITH CHECK (user_id = auth.uid()::text);

CREATE POLICY "Users can update their own CV records" ON cv_records
    FOR UPDATE USING (user_id = auth.uid()::text);

CREATE POLICY "Users can delete their own CV records" ON cv_records
    FOR DELETE USING (user_id = auth.uid()::text);

-- Career Paths policies
CREATE POLICY "Users can view their own career paths" ON career_paths
    FOR SELECT USING (user_id = auth.uid()::text);

CREATE POLICY "Users can insert their own career paths" ON career_paths
    FOR INSERT WITH CHECK (user_id = auth.uid()::text);

-- Skill Gaps policies
CREATE POLICY "Users can view their own skill gaps" ON skill_gaps
    FOR SELECT USING (user_id = auth.uid()::text);

CREATE POLICY "Users can insert their own skill gaps" ON skill_gaps
    FOR INSERT WITH CHECK (user_id = auth.uid()::text);

-- Resume Optimizations policies
CREATE POLICY "Users can view their own resume optimizations" ON resume_optimizations
    FOR SELECT USING (user_id = auth.uid()::text);

CREATE POLICY "Users can insert their own resume optimizations" ON resume_optimizations
    FOR INSERT WITH CHECK (user_id = auth.uid()::text); 