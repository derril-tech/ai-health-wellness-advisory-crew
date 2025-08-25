export interface User {
  id: string;
  email: string;
  name?: string;
  org_id?: string;
  created_at: string;
}

export interface HealthProfile {
  user_id: string;
  experience_level: string;
  goal: string;
  target_date: string;
  diet_pref: string;
  allergies: string[];
  dislikes: string[];
  equipment: string[];
  injuries: any[];
  meds: any[];
  parq: any[];
  cleared: boolean;
}

export interface Program {
  id: string;
  user_id: string;
  start_date: string;
  end_date: string;
  status: 'draft' | 'active' | 'paused' | 'completed';
  goal: any;
  strategy: any;
  created_at: string;
}

export interface MacroTargets {
  id: string;
  program_id: string;
  week: number;
  kcal: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number;
  sodium_mg: number;
  water_ml: number;
  refeed: boolean;
}

export interface Workout {
  id: string;
  program_id: string;
  week: number;
  day_of_week: number;
  title: string;
  focus: string;
  duration_min: number;
}

export interface WorkoutSet {
  id: string;
  workout_id: string;
  exercise_id: string;
  set_idx: number;
  reps: number;
  load_pct: number;
  tempo: string;
  rir: number;
  rest_sec: number;
  notes?: string;
}

export interface WorkoutLog {
  id: string;
  workout_id: string;
  user_id: string;
  ts: string;
  exercise_id: string;
  set_idx: number;
  reps_done: number;
  weight_kg: number;
  rpe: number;
  pain: boolean;
  notes?: string;
}

export interface Habit {
  id: string;
  program_id: string;
  name: string;
  unit: string;
  target: number;
  schedule: any;
  priority: number;
  created_at: string;
}

export interface Checkin {
  id: string;
  program_id: string;
  week: number;
  submitted_at: string;
  adherence_nutrition: number;
  adherence_training: number;
  sleep_score: number;
  fatigue: number;
  summary: string;
  photos?: any[];
}

export interface Adjustment {
  id: string;
  program_id: string;
  week: number;
  kcal_delta: number;
  volume_delta: number;
  deload: boolean;
  habit_changes: any;
  rationale: string;
  created_at: string;
}
