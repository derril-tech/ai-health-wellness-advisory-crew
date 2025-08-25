-- Health & Wellness Advisor Crew Database Schema
-- Created automatically by Cursor AI (2024-12-19)

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS health;
CREATE SCHEMA IF NOT EXISTS programs;
CREATE SCHEMA IF NOT EXISTS nutrition;
CREATE SCHEMA IF NOT EXISTS training;
CREATE SCHEMA IF NOT EXISTS habits;
CREATE SCHEMA IF NOT EXISTS devices;
CREATE SCHEMA IF NOT EXISTS analytics;

-- ============================================================================
-- AUTHENTICATION & USERS
-- ============================================================================

-- Organizations (for coach orgs)
CREATE TABLE auth.organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    plan VARCHAR(50) DEFAULT 'free',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Users
CREATE TABLE auth.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    name VARCHAR(255),
    org_id UUID REFERENCES auth.organizations(id),
    role VARCHAR(50) DEFAULT 'user',
    email_verified BOOLEAN DEFAULT FALSE,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- HEALTH PROFILES & INTAKE
-- ============================================================================

-- Health profiles
CREATE TABLE health.profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    height_cm INTEGER,
    weight_kg DECIMAL(5,2),
    age INTEGER,
    sex_at_birth VARCHAR(20),
    activity_level VARCHAR(50),
    goal VARCHAR(100),
    experience_level VARCHAR(50),
    equipment_access TEXT[],
    allergies TEXT[],
    injuries JSONB[],
    medications JSONB[],
    parq_flags TEXT[],
    risk_level VARCHAR(20) DEFAULT 'low',
    cleared BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Intake questionnaires
CREATE TABLE health.intake_questionnaires (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    responses JSONB NOT NULL,
    normalized_profile_id UUID REFERENCES health.profiles(id),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================================
-- PROGRAMS & PLANS
-- ============================================================================

-- Programs
CREATE TABLE programs.programs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES health.profiles(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    goal JSONB NOT NULL,
    strategy JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Program adjustments
CREATE TABLE programs.adjustments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program_id UUID NOT NULL REFERENCES programs.programs(id) ON DELETE CASCADE,
    week INTEGER NOT NULL,
    kcal_delta INTEGER DEFAULT 0,
    volume_delta DECIMAL(5,2) DEFAULT 0,
    deload BOOLEAN DEFAULT FALSE,
    habit_changes JSONB,
    rationale TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- NUTRITION
-- ============================================================================

-- Macro targets (TimescaleDB hypertable)
CREATE TABLE nutrition.macro_targets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program_id UUID NOT NULL REFERENCES programs.programs(id) ON DELETE CASCADE,
    week INTEGER NOT NULL,
    day_of_week INTEGER,
    kcal INTEGER NOT NULL,
    protein_g INTEGER NOT NULL,
    carbs_g INTEGER NOT NULL,
    fat_g INTEGER NOT NULL,
    fiber_g INTEGER NOT NULL,
    sodium_mg INTEGER NOT NULL,
    water_ml INTEGER NOT NULL,
    refeed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('nutrition.macro_targets', 'created_at');

-- Meal plans
CREATE TABLE nutrition.meal_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program_id UUID NOT NULL REFERENCES programs.programs(id) ON DELETE CASCADE,
    week INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    meal_type VARCHAR(50) NOT NULL,
    meals JSONB NOT NULL,
    total_kcal INTEGER NOT NULL,
    total_protein_g INTEGER NOT NULL,
    total_carbs_g INTEGER NOT NULL,
    total_fat_g INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Food database
CREATE TABLE nutrition.foods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255),
    serving_size_g DECIMAL(8,2),
    kcal_per_100g INTEGER NOT NULL,
    protein_g_per_100g DECIMAL(5,2) NOT NULL,
    carbs_g_per_100g DECIMAL(5,2) NOT NULL,
    fat_g_per_100g DECIMAL(5,2) NOT NULL,
    fiber_g_per_100g DECIMAL(5,2),
    sodium_mg_per_100g INTEGER,
    allergens TEXT[],
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create vector index for food embeddings
CREATE INDEX IF NOT EXISTS foods_embedding_idx ON nutrition.foods USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================================================
-- TRAINING
-- ============================================================================

-- Exercises library
CREATE TABLE training.exercises (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    muscle_groups TEXT[],
    equipment TEXT[],
    contraindications TEXT[],
    progressions TEXT[],
    regressions TEXT[],
    video_url VARCHAR(500),
    instructions TEXT,
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create vector index for exercise embeddings
CREATE INDEX IF NOT EXISTS exercises_embedding_idx ON training.exercises USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Workouts
CREATE TABLE training.workouts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program_id UUID NOT NULL REFERENCES programs.programs(id) ON DELETE CASCADE,
    week INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    focus VARCHAR(100),
    duration_min INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Workout sets
CREATE TABLE training.workout_sets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workout_id UUID NOT NULL REFERENCES training.workouts(id) ON DELETE CASCADE,
    exercise_id UUID NOT NULL REFERENCES training.exercises(id),
    set_idx INTEGER NOT NULL,
    reps INTEGER NOT NULL,
    load_pct DECIMAL(5,2),
    tempo VARCHAR(20),
    rir INTEGER DEFAULT 2,
    rest_sec INTEGER,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Workout logs (TimescaleDB hypertable)
CREATE TABLE training.workout_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workout_id UUID NOT NULL REFERENCES training.workouts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    exercise_id UUID NOT NULL REFERENCES training.exercises(id),
    set_idx INTEGER NOT NULL,
    reps_done INTEGER NOT NULL,
    weight_kg DECIMAL(6,2),
    rpe INTEGER CHECK (rpe >= 1 AND rpe <= 10),
    pain BOOLEAN DEFAULT FALSE,
    notes TEXT,
    logged_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('training.workout_logs', 'logged_at');

-- ============================================================================
-- HABITS & MINDSET
-- ============================================================================

-- Habits
CREATE TABLE habits.habits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program_id UUID NOT NULL REFERENCES programs.programs(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    target DECIMAL(8,2) NOT NULL,
    schedule JSONB NOT NULL,
    priority INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Habit logs (TimescaleDB hypertable)
CREATE TABLE habits.habit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    habit_id UUID NOT NULL REFERENCES habits.habits(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    value DECIMAL(8,2) NOT NULL,
    note TEXT,
    logged_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('habits.habit_logs', 'logged_at');

-- ============================================================================
-- CHECK-INS & PROGRESS
-- ============================================================================

-- Check-ins (TimescaleDB hypertable)
CREATE TABLE analytics.checkins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program_id UUID NOT NULL REFERENCES programs.programs(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    week INTEGER NOT NULL,
    adherence_nutrition INTEGER CHECK (adherence_nutrition >= 0 AND adherence_nutrition <= 100),
    adherence_training INTEGER CHECK (adherence_training >= 0 AND adherence_training <= 100),
    sleep_score INTEGER CHECK (sleep_score >= 0 AND sleep_score <= 100),
    fatigue INTEGER CHECK (fatigue >= 1 AND fatigue <= 10),
    weight_kg DECIMAL(5,2),
    body_fat_pct DECIMAL(4,2),
    photos JSONB,
    summary TEXT,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('analytics.checkins', 'submitted_at');

-- ============================================================================
-- DEVICES & WEARABLES
-- ============================================================================

-- Device connections
CREATE TABLE devices.connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    provider_user_id VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMP WITH TIME ZONE,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, provider)
);

-- Device data (TimescaleDB hypertable)
CREATE TABLE devices.device_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    connection_id UUID NOT NULL REFERENCES devices.connections(id) ON DELETE CASCADE,
    data_type VARCHAR(50) NOT NULL,
    value DECIMAL(10,4),
    unit VARCHAR(20),
    metadata JSONB,
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL,
    synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('devices.device_data', 'recorded_at');

-- ============================================================================
-- MESSAGES & NOTIFICATIONS
-- ============================================================================

-- Messages
CREATE TABLE analytics.messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE auth.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE health.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE health.intake_questionnaires ENABLE ROW LEVEL SECURITY;
ALTER TABLE programs.programs ENABLE ROW LEVEL SECURITY;
ALTER TABLE programs.adjustments ENABLE ROW LEVEL SECURITY;
ALTER TABLE nutrition.macro_targets ENABLE ROW LEVEL SECURITY;
ALTER TABLE nutrition.meal_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE training.workouts ENABLE ROW LEVEL SECURITY;
ALTER TABLE training.workout_sets ENABLE ROW LEVEL SECURITY;
ALTER TABLE training.workout_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE habits.habits ENABLE ROW LEVEL SECURITY;
ALTER TABLE habits.habit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics.checkins ENABLE ROW LEVEL SECURITY;
ALTER TABLE devices.connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE devices.device_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics.messages ENABLE ROW LEVEL SECURITY;

-- RLS Policies
-- Users can only access their own data
CREATE POLICY "Users can view own profile" ON auth.users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON auth.users FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can access own health data" ON health.profiles FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can access own intake data" ON health.intake_questionnaires FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access own programs" ON programs.programs FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can access own adjustments" ON programs.adjustments FOR ALL USING (
    program_id IN (SELECT id FROM programs.programs WHERE user_id = auth.uid())
);

CREATE POLICY "Users can access own nutrition data" ON nutrition.macro_targets FOR ALL USING (
    program_id IN (SELECT id FROM programs.programs WHERE user_id = auth.uid())
);
CREATE POLICY "Users can access own meal plans" ON nutrition.meal_plans FOR ALL USING (
    program_id IN (SELECT id FROM programs.programs WHERE user_id = auth.uid())
);

CREATE POLICY "Users can access own training data" ON training.workouts FOR ALL USING (
    program_id IN (SELECT id FROM programs.programs WHERE user_id = auth.uid())
);
CREATE POLICY "Users can access own workout sets" ON training.workout_sets FOR ALL USING (
    workout_id IN (SELECT id FROM training.workouts WHERE program_id IN (SELECT id FROM programs.programs WHERE user_id = auth.uid()))
);
CREATE POLICY "Users can access own workout logs" ON training.workout_logs FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access own habits" ON habits.habits FOR ALL USING (
    program_id IN (SELECT id FROM programs.programs WHERE user_id = auth.uid())
);
CREATE POLICY "Users can access own habit logs" ON habits.habit_logs FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access own checkins" ON analytics.checkins FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access own device data" ON devices.connections FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can access own device readings" ON devices.device_data FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access own messages" ON analytics.messages FOR ALL USING (auth.uid() = user_id);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Performance indexes
CREATE INDEX idx_users_email ON auth.users(email);
CREATE INDEX idx_users_org_id ON auth.users(org_id);

CREATE INDEX idx_profiles_user_id ON health.profiles(user_id);
CREATE INDEX idx_intake_user_id ON health.intake_questionnaires(user_id);

CREATE INDEX idx_programs_user_id ON programs.programs(user_id);
CREATE INDEX idx_programs_status ON programs.programs(status);
CREATE INDEX idx_adjustments_program_week ON programs.adjustments(program_id, week);

CREATE INDEX idx_macro_targets_program_week ON nutrition.macro_targets(program_id, week);
CREATE INDEX idx_meal_plans_program_week_day ON nutrition.meal_plans(program_id, week, day_of_week);
CREATE INDEX idx_foods_name ON nutrition.foods(name);

CREATE INDEX idx_exercises_category ON training.exercises(category);
CREATE INDEX idx_workouts_program_week ON training.workouts(program_id, week);
CREATE INDEX idx_workout_sets_workout ON training.workout_sets(workout_id);
CREATE INDEX idx_workout_logs_user_date ON training.workout_logs(user_id, logged_at);

CREATE INDEX idx_habits_program ON habits.habits(program_id);
CREATE INDEX idx_habit_logs_habit_date ON habits.habit_logs(habit_id, logged_at);

CREATE INDEX idx_checkins_user_week ON analytics.checkins(user_id, week);
CREATE INDEX idx_checkins_program_week ON analytics.checkins(program_id, week);

CREATE INDEX idx_device_connections_user_provider ON devices.connections(user_id, provider);
CREATE INDEX idx_device_data_user_type_date ON devices.device_data(user_id, data_type, recorded_at);

CREATE INDEX idx_messages_user_unread ON analytics.messages(user_id, read_at) WHERE read_at IS NULL;

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON auth.users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON auth.organizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON health.profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_programs_updated_at BEFORE UPDATE ON programs.programs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_connections_updated_at BEFORE UPDATE ON devices.connections FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SEED DATA
-- ============================================================================

-- Insert sample exercises
INSERT INTO training.exercises (name, category, muscle_groups, equipment, instructions) VALUES
('Push-ups', 'bodyweight', ARRAY['chest', 'triceps', 'shoulders'], ARRAY['none'], 'Start in plank position, lower body until chest nearly touches ground, push back up'),
('Squats', 'bodyweight', ARRAY['quadriceps', 'glutes', 'hamstrings'], ARRAY['none'], 'Stand with feet shoulder-width apart, lower hips back and down, return to standing'),
('Pull-ups', 'bodyweight', ARRAY['back', 'biceps'], ARRAY['pull-up bar'], 'Hang from bar, pull body up until chin over bar, lower with control'),
('Deadlifts', 'strength', ARRAY['back', 'glutes', 'hamstrings'], ARRAY['barbell'], 'Stand with feet hip-width, grip bar, lift by extending hips and knees'),
('Bench Press', 'strength', ARRAY['chest', 'triceps', 'shoulders'], ARRAY['barbell', 'bench'], 'Lie on bench, lower bar to chest, press back up');

-- Insert sample foods
INSERT INTO nutrition.foods (name, brand, serving_size_g, kcal_per_100g, protein_g_per_100g, carbs_g_per_100g, fat_g_per_100g, fiber_g_per_100g, sodium_mg_per_100g) VALUES
('Chicken Breast', 'Generic', 100, 165, 31, 0, 3.6, 0, 74),
('Brown Rice', 'Generic', 100, 111, 2.6, 23, 0.9, 1.8, 5),
('Broccoli', 'Generic', 100, 34, 2.8, 7, 0.4, 2.6, 33),
('Salmon', 'Generic', 100, 208, 25, 0, 12, 0, 59),
('Sweet Potato', 'Generic', 100, 86, 1.6, 20, 0.1, 3, 55);

-- Create default organization
INSERT INTO auth.organizations (name, slug, plan) VALUES ('Health Crew', 'health-crew', 'free');
