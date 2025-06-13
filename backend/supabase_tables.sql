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
    target_role TEXT,
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

-- Learning Goals table (PRD section 4.3 - Track learning progress)
CREATE TABLE learning_goals (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    skill_gap_id INTEGER REFERENCES skill_gaps(id),
    skill_name TEXT NOT NULL,
    learning_resource_type TEXT NOT NULL, -- course, certification, book, video, etc.
    learning_resource_name TEXT NOT NULL,
    learning_resource_url TEXT,
    target_completion_date DATE,
    priority TEXT DEFAULT 'medium', -- high, medium, low
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    status TEXT DEFAULT 'not_started', -- not_started, in_progress, completed, paused
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Learning Recommendations table (PRD section 4.3 - Recommend specific courses, certifications)
CREATE TABLE learning_recommendations (
    id SERIAL PRIMARY KEY,
    skill_gap_id INTEGER REFERENCES skill_gaps(id),
    user_id TEXT NOT NULL,
    skill_name TEXT NOT NULL,
    resource_type TEXT NOT NULL, -- coursera, udemy, youtube, certification, book
    resource_name TEXT NOT NULL,
    resource_url TEXT,
    provider TEXT, -- Coursera, Udemy, DeepLearning.ai, LinkedIn Learning, etc.
    estimated_duration TEXT, -- e.g., "40 hours", "3 months"
    cost TEXT, -- e.g., "Free", "$49", "$150"
    difficulty_level TEXT, -- beginner, intermediate, advanced
    rating DECIMAL(3,2), -- e.g., 4.7
    priority TEXT DEFAULT 'medium', -- high, medium, low
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_cv_records_user_id ON cv_records(user_id);
CREATE INDEX idx_career_paths_user_id ON career_paths(user_id);
CREATE INDEX idx_skill_gaps_user_id ON skill_gaps(user_id);
CREATE INDEX idx_resume_optimizations_user_id ON resume_optimizations(user_id);
CREATE INDEX idx_learning_goals_user_id ON learning_goals(user_id);
CREATE INDEX idx_learning_goals_skill_gap_id ON learning_goals(skill_gap_id);
CREATE INDEX idx_learning_recommendations_user_id ON learning_recommendations(user_id);
CREATE INDEX idx_learning_recommendations_skill_gap_id ON learning_recommendations(skill_gap_id);

-- Enable Row Level Security (RLS)
ALTER TABLE cv_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE career_paths ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_gaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE resume_optimizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_recommendations ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (users can only access their own data)
CREATE POLICY "Users can view own CV records" ON cv_records FOR SELECT USING (auth.uid()::text = user_id);
CREATE POLICY "Users can insert own CV records" ON cv_records FOR INSERT WITH CHECK (auth.uid()::text = user_id);
CREATE POLICY "Users can update own CV records" ON cv_records FOR UPDATE USING (auth.uid()::text = user_id);

CREATE POLICY "Users can view own career paths" ON career_paths FOR SELECT USING (auth.uid()::text = user_id);
CREATE POLICY "Users can insert own career paths" ON career_paths FOR INSERT WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can view own skill gaps" ON skill_gaps FOR SELECT USING (auth.uid()::text = user_id);
CREATE POLICY "Users can insert own skill gaps" ON skill_gaps FOR INSERT WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can view own resume optimizations" ON resume_optimizations FOR SELECT USING (auth.uid()::text = user_id);
CREATE POLICY "Users can insert own resume optimizations" ON resume_optimizations FOR INSERT WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can view own learning goals" ON learning_goals FOR SELECT USING (auth.uid()::text = user_id);
CREATE POLICY "Users can insert own learning goals" ON learning_goals FOR INSERT WITH CHECK (auth.uid()::text = user_id);
CREATE POLICY "Users can update own learning goals" ON learning_goals FOR UPDATE USING (auth.uid()::text = user_id);

CREATE POLICY "Users can view own learning recommendations" ON learning_recommendations FOR SELECT USING (auth.uid()::text = user_id);
CREATE POLICY "Users can insert own learning recommendations" ON learning_recommendations FOR INSERT WITH CHECK (auth.uid()::text = user_id); 