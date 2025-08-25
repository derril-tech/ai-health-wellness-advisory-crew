import { z } from 'zod';

// Auth schemas
export const LoginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

export const RefreshTokenSchema = z.object({
  refresh_token: z.string(),
});

// User schemas
export const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string().optional(),
  org_id: z.string().uuid().optional(),
  created_at: z.string().datetime(),
});

// Health Profile schemas
export const HealthProfileSchema = z.object({
  user_id: z.string().uuid(),
  experience_level: z.string(),
  goal: z.string(),
  target_date: z.string().date(),
  diet_pref: z.string(),
  allergies: z.array(z.string()),
  dislikes: z.array(z.string()),
  equipment: z.array(z.string()),
  injuries: z.array(z.any()),
  meds: z.array(z.any()),
  parq: z.array(z.any()),
  cleared: z.boolean(),
});

// Program schemas
export const ProgramSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  start_date: z.string().date(),
  end_date: z.string().date(),
  status: z.enum(['draft', 'active', 'paused', 'completed']),
  goal: z.any(),
  strategy: z.any(),
  created_at: z.string().datetime(),
});

export const CreateProgramSchema = z.object({
  start_date: z.string().date(),
  goal: z.any(),
});

// Macro schemas
export const MacroTargetsSchema = z.object({
  id: z.string().uuid(),
  program_id: z.string().uuid(),
  week: z.number().int().positive(),
  kcal: z.number().int().positive(),
  protein_g: z.number().int().positive(),
  carbs_g: z.number().int().positive(),
  fat_g: z.number().int().positive(),
  fiber_g: z.number().int().positive(),
  sodium_mg: z.number().int().positive(),
  water_ml: z.number().int().positive(),
  refeed: z.boolean(),
});

// Workout schemas
export const WorkoutSchema = z.object({
  id: z.string().uuid(),
  program_id: z.string().uuid(),
  week: z.number().int().positive(),
  day_of_week: z.number().int().min(1).max(7),
  title: z.string(),
  focus: z.string(),
  duration_min: z.number().int().positive(),
});

export const WorkoutSetSchema = z.object({
  id: z.string().uuid(),
  workout_id: z.string().uuid(),
  exercise_id: z.string().uuid(),
  set_idx: z.number().int().positive(),
  reps: z.number().int().positive(),
  load_pct: z.number().positive(),
  tempo: z.string(),
  rir: z.number().int().min(0).max(3),
  rest_sec: z.number().int().positive(),
  notes: z.string().optional(),
});

export const WorkoutLogSchema = z.object({
  id: z.string().uuid(),
  workout_id: z.string().uuid(),
  user_id: z.string().uuid(),
  ts: z.string().datetime(),
  exercise_id: z.string().uuid(),
  set_idx: z.number().int().positive(),
  reps_done: z.number().int().positive(),
  weight_kg: z.number().positive(),
  rpe: z.number().min(1).max(10),
  pain: z.boolean(),
  notes: z.string().optional(),
});

export const LogWorkoutSchema = z.object({
  sets: z.array(z.object({
    exercise_id: z.string().uuid(),
    set_idx: z.number().int().positive(),
    reps_done: z.number().int().positive(),
    weight_kg: z.number().positive(),
    rpe: z.number().min(1).max(10),
    pain: z.boolean(),
    notes: z.string().optional(),
  })),
});

// Habit schemas
export const HabitSchema = z.object({
  id: z.string().uuid(),
  program_id: z.string().uuid(),
  name: z.string(),
  unit: z.string(),
  target: z.number().positive(),
  schedule: z.any(),
  priority: z.number().int().positive(),
  created_at: z.string().datetime(),
});

export const LogHabitSchema = z.object({
  value: z.number(),
  note: z.string().optional(),
});

// Check-in schemas
export const CheckinSchema = z.object({
  id: z.string().uuid(),
  program_id: z.string().uuid(),
  week: z.number().int().positive(),
  submitted_at: z.string().datetime(),
  adherence_nutrition: z.number().min(0).max(100),
  adherence_training: z.number().min(0).max(100),
  sleep_score: z.number().min(0).max(100),
  fatigue: z.number().min(1).max(10),
  summary: z.string(),
  photos: z.array(z.any()).optional(),
});

export const SubmitCheckinSchema = z.object({
  metrics: z.any(),
  photos: z.array(z.any()).optional(),
});

// Adjustment schemas
export const AdjustmentSchema = z.object({
  id: z.string().uuid(),
  program_id: z.string().uuid(),
  week: z.number().int().positive(),
  kcal_delta: z.number(),
  volume_delta: z.number(),
  deload: z.boolean(),
  habit_changes: z.any(),
  rationale: z.string(),
  created_at: z.string().datetime(),
});

// Device schemas
export const SyncDevicesSchema = z.object({
  window: z.string(),
});

// Export schemas
export const ExportProgramSchema = z.object({
  targets: z.array(z.string()),
});
