HEALTH & WELLNESS ADVISOR CREW —
END‑TO‑END PRODUCT BLUEPRINT
(React 18 + Next.js 14 App Router; CrewAI multi
‑agent orchestration; TypeScript
‑first
contracts.)
1) Product Description & Presentation
One‑liner
A multi‑agent coach that turns a goal like “Lose 5 kg in 12 weeks while maintaining
muscle” into a personalized 12‑week plan across training, nutrition, mindset, and
accountability, updated weekly from real‑world progress and wearable data.
Positioning
• For individuals, personal trainers, and wellness teams who want safe, adaptive
plans with minimal guesswork.
• Output artifacts: weekly workout blocks (sets/reps/tempo/progression), meal plans
(macro & micro targets with grocery lists), mindset practices, habit trackers,
daily/weekly check‑ins, progress reports, and adjustment notes—all auditable and
exportable.
Safety stance
• Not a medical device; pre‑exercise PAR‑Q screening, contraindication checks, and
red‑flag escalation to “consult a licensed professional” when needed.
2) Target User
• Goal‑driven individuals (fat loss, recomposition, strength, endurance).
• Personal trainers & nutrition coaches managing client programs.
• Corporate wellness & fitness studios offering hybrid coaching.
• Rehab‑adjacent users (non‑clinical), with stricter safety guardrails.
3) Features & Functionalities (Extensive)
Intake & Safety
• Questionnaires: goals, timeline, experience level, equipment access,
injuries/contraindications, allergies, dietary pattern (omnivore/vegan/kosher/halal),
sleep/stress.
• Health profile: height, weight, body fat estimate, circumferences, resting HR/HRV
(optional), step count baseline.
• PAR‑Q screen with red‑flag list; automatic plan lockdown if any critical item is “Yes”
until user confirms medical clearance.
Program Design
• Goal translation → numeric targets (Δweight, fat %, strength PRs, VO₂ proxies).
• Nutrition: TDEE estimate (Mifflin/St Jeor + activity), macro split, fiber + micros,
hydration targets; weekly kcal periodization (refeeds/diet breaks optional).
• Training: 12‑week mesocycle → 3–4 microcycles with progressive overload; RPE/RIR
guidance; exercise substitutions based on equipment and injury flags.
• Mindset: CBT‑style reframes, stress management, sleep hygiene, journaling prompts.
• Habit stack: steps/day, protein minimum, bedtime routine, mindfulness minutes.
Dynamic Adaptation
• Weekly check‑ins: weight trend (7‑day avg), tape, photos (optional), adherence %,
RPE fatigue, sleep score.
• Auto‑adjust nutrition (±5–15% calories), training volume/deloads, and habit targets
based on response.
• Device ingestion: Apple Health/Google Fit/Fitbit/Oura/Garmin for steps, HR, HRV,
sleep, workouts.
Day‑to‑Day UX
• Today view: workouts with timers & cues; meals with swap logic; habit checklist;
hydration tracker.
• Grocery list auto‑compiled by week with pantry carry‑over; meal prep options.
• Substitutions: same‑macro swaps; allergy/availability filters; price‑aware
substitutions (optional).
Content & Guidance
• Exercise library with video cues, common faults, regression/progression ladders.
• Recipe library with allergens, cuisine, prep time, macro profile; “cooking skill” slider.
• Mindset library: 5–10‑min practices, journaling, if‑then plans for cravings.
Accountability & Community
• Daily nudges (push/Slack/email), streaks, and coach chat (optional org-level).
• Progress analytics: trend charts, adherence heatmaps, PR logbook.
Compliance & Consent
• Informed‑use consent, data‑sharing controls, data export, deletion, residency.
4) Backend Architecture (Extremely Detailed &
Deployment‑Ready)
4.1 Topology
• Frontend/BFF: Next.js 14 (Vercel).
• API Gateway: Node/NestJS (REST, OpenAPI 3.1, rate limits, Idempotency‑Key, RBAC,
Problem+JSON).
• Auth: Auth.js (OAuth/passwordless) + short‑lived JWT; enterprise SSO (SAML/OIDC);
SCIM for coach orgs.
• Orchestration: CrewAI Orchestrator (Python FastAPI) coordinating:
o Nutritionist, Trainer, Psychologist, Accountability Buddy
o plus Safety Screener, Progress Analyst, Schedule Optimizer, Grocery Planner,
Recipe/Exercise Librarian.
• Workers (Python):
o intake-normalizer (questionnaire → normalized profile)
o tdee-macro-engine (kcal/macros periodization)
o mealplanner (constrained optimization, macro balancing, swap catalog)
o workout-periodization (blocks, sets/reps, tempo, RPE/RIR, deload)
o habit-engine (targets, streaks, reminders)
o progress-analyzer (weekly check-in logic, adjustments)
o device-ingestor (Apple/Google/Fitbit/Oura/Garmin adapters)
o grocery-builder (ingredient aggregation, pantry diffs)
o reporter (weekly PDF/HTML summaries)
• Event Bus: NATS (intake.*, plan.*, meal.*, workout.*, checkin.*, device.*,
alert.*, export.*).
• Task Queue: Celery (NATS/Redis backend) with lanes: interactive, adjustments,
device-sync, reports.
• DB: Postgres (Neon/Cloud SQL) + Timescale for biometrics; pgvector for
recipe/exercise embeddings.
• Object Storage: S3/R2 (images/videos, exports).
• Cache: Upstash Redis (session, “today” plan, timers, presence).
• Realtime: WebSocket gateway (NestJS) with SSE fallback (check-ins, timers, chat).
• Observability: OpenTelemetry traces; Prometheus/Grafana; Sentry; structured JSON
logs.
• Secrets: Cloud Secrets Manager/Vault; provider keys via KMS; zero plaintext secrets in
DB.
4.2 CrewAI Agents & Responsibilities
• Safety Screener — PAR‑Q gating, contraindication flags; blocks plan generation if risk
> policy threshold.
• Nutritionist — kcal/macros, meal distribution, micro targets, refeed/diet break
cadence; builds meal templates; swap logic.
• Trainer — 12‑week periodization, exercise selection by equipment & injury flags,
progressive overload rules, deloads.
• Psychologist — mindset practices, adherence troubleshooting, relapse plans, sleep
routines.
• Accountability Buddy — nudges, check‑in prompts, streak messaging; tone per user
preference.
• Progress Analyst — ingests weekly data; decides adjustments (kcal/volume/deload).
• Grocery Planner — shopping list with pantry diffs; cost hints.
• Schedule Optimizer — reflows sessions & meals around calendar conflicts.
• Librarian — curates recipes/exercises; embeds & tags content; quality thresholds.
Agent Tools (strictly defined)
• Calc.tdee(profile) → kcal/day with activity & TEF adjustment.
• Macros.plan(goal, timeline, preference) → daily macros + periodization.
• Meals.generate(day, constraints) → meals[] meeting macro window with
micros.
• Workouts.generate(week, split, constraints) → sessions[] with
sets/reps/tempo/RPE.
• Adjustments.evaluate(progress) → {kcal_delta, volume_delta, deload?,
habit_deltas}.
• Devices.pull(conn, window) → normalized steps/hr/sleep.
• Grocery.compile(week, pantry) → items[] with quantities.
• Mindset.assign(week, issues) → practices[] + journaling prompts.
• Schedule.solve(calendar, availability) → plan with moved sessions/meals
respecting rules.
4.3 Data Model (Postgres + Timescale + pgvector)
-- Tenancy & Users
CREATE TABLE orgs (
id UUID PRIMARY KEY, name TEXT NOT NULL, plan TEXT, created_at
TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE users (
id UUID PRIMARY KEY, org_id UUID, email CITEXT UNIQUE, name TEXT,
dob DATE,
sex_at_birth TEXT, height_cm NUMERIC, tz TEXT, created_at
TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE roles (
user_id UUID, org_id UUID, role TEXT CHECK (role IN
('owner','coach','member','viewer')),
PRIMARY KEY (user_id, org_id)
);
-- Health Profile & Safety
CREATE TABLE health_profiles (
user_id UUID PRIMARY KEY REFERENCES users(id),
experience_level TEXT, goal TEXT, target_date DATE,
diet_pref TEXT, allergies TEXT[], dislikes TEXT[], equipment TEXT[],
injuries JSONB, meds JSONB, parq JSONB, cleared BOOLEAN DEFAULT
FALSE,
created_at TIMESTAMPTZ DEFAULT now()
);
-- Devices
CREATE TABLE devices (
id UUID PRIMARY KEY, user_id UUID, provider TEXT, access_token TEXT,
refresh_token TEXT,
expires_at TIMESTAMPTZ, scope TEXT[], connected_at TIMESTAMPTZ
);
-- Biometrics (Timescale hypertable)
CREATE TABLE biometrics (
ts TIMESTAMPTZ NOT NULL, user_id UUID, kind TEXT, --
'weight','bodyfat','waist','hr','hrv','sleep','steps'
value NUMERIC, meta JSONB, PRIMARY KEY (ts, user_id, kind)
);
-- Program (12-week plan)
CREATE TABLE programs (
id UUID PRIMARY KEY, user_id UUID, start_date DATE, end_date DATE,
status TEXT
CHECK (status IN ('draft','active','paused','completed')),
goal JSONB, strategy JSONB, created_at TIMESTAMPTZ DEFAULT now()
);
-- Nutrition
CREATE TABLE macro_targets (
id UUID PRIMARY KEY, program_id UUID, week INT, kcal INT, protein_g
INT, carbs_g INT, fat_g INT,
fiber_g INT, sodium_mg INT, water_ml INT, refeed BOOLEAN DEFAULT
FALSE
);
CREATE TABLE recipes (
id UUID PRIMARY KEY, org_id UUID, name TEXT, cuisine TEXT, skill
TEXT,
cook_min INT, tags TEXT[], allergens TEXT[], ingredients JSONB, --
[{name, qty_g, kcal, macros{p,c,f}, micros{...}}]
macros JSONB, micros JSONB, instructions TEXT, embedding
VECTOR(1536)
);
CREATE TABLE meal_plans (
id UUID PRIMARY KEY, program_id UUID, day DATE, total_kcal INT,
target_macros JSONB
);
CREATE TABLE meals (
id UUID PRIMARY KEY, meal_plan_id UUID REFERENCES meal_plans(id),
slot TEXT, -- 'breakfast','lunch','dinner','snack1'...
recipe_id UUID REFERENCES recipes(id), servings NUMERIC, macros
JSONB, micros JSONB, notes TEXT
);
CREATE TABLE pantry_items (
id UUID PRIMARY KEY, user_id UUID, name TEXT, qty_unit TEXT, qty
NUMERIC, updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE grocery_lists (
id UUID PRIMARY KEY, program_id UUID, week INT, items JSONB, --
[{name, qty, unit, aisle}]
generated_at TIMESTAMPTZ DEFAULT now()
);
-- Training
CREATE TABLE exercises (
id UUID PRIMARY KEY, org_id UUID, name TEXT, pattern TEXT, equipment
TEXT[],
primary_muscles TEXT[], secondary_muscles TEXT[], video_key TEXT,
cues TEXT[],
contraindications TEXT[], progression JSONB, embedding VECTOR(1536)
);
CREATE TABLE workouts (
id UUID PRIMARY KEY, program_id UUID, week INT, day_of_week INT,
title TEXT, focus TEXT, duration_min INT
);
CREATE TABLE workout_sets (
id UUID PRIMARY KEY, workout_id UUID REFERENCES workouts(id),
exercise_id UUID REFERENCES exercises(id),
set_idx INT, reps INT, load_pct NUMERIC, tempo TEXT, rir INT,
rest_sec INT, notes TEXT
);
CREATE TABLE workout_logs (
id UUID PRIMARY KEY, workout_id UUID, user_id UUID, ts TIMESTAMPTZ,
exercise_id UUID, set_idx INT, reps_done INT, weight_kg NUMERIC, rpe
NUMERIC, pain BOOLEAN, notes TEXT
);
-- Habits & Mindset
CREATE TABLE habits (
id UUID PRIMARY KEY, program_id UUID, name TEXT, unit TEXT, target
NUMERIC, schedule JSONB, -- RRULE
priority INT, created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE habit_logs (
id UUID PRIMARY KEY, habit_id UUID, user_id UUID, ts TIMESTAMPTZ,
value NUMERIC, note TEXT
);
CREATE TABLE mindset_practices (
id UUID PRIMARY KEY, program_id UUID, week INT, title TEXT, script
TEXT, duration_min INT, tags TEXT[]
);
CREATE TABLE journals (
id UUID PRIMARY KEY, user_id UUID, ts TIMESTAMPTZ, mood INT, stress
INT, entry TEXT
);
-- Check-ins & Adjustments
CREATE TABLE checkins (
id UUID PRIMARY KEY, program_id UUID, week INT, submitted_at
TIMESTAMPTZ,
adherence_nutrition NUMERIC, adherence_training NUMERIC, sleep_score
NUMERIC, fatigue NUMERIC,
summary TEXT, photos JSONB
);
CREATE TABLE adjustments (
id UUID PRIMARY KEY, program_id UUID, week INT, kcal_delta INT,
volume_delta INT,
deload BOOLEAN, habit_changes JSONB, rationale TEXT, created_at
TIMESTAMPTZ DEFAULT now()
);
-- Messaging & Notifications
CREATE TABLE messages (
id UUID PRIMARY KEY, program_id UUID, sender TEXT, body TEXT, ts
TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE nudges (
id BIGSERIAL PRIMARY KEY, user_id UUID, channel TEXT, payload JSONB,
sent_at TIMESTAMPTZ
);
-- Audit & Exports
CREATE TABLE exports (
id UUID PRIMARY KEY, program_id UUID, kind TEXT, s3_key TEXT, meta
JSONB, created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE audit_log (
id BIGSERIAL PRIMARY KEY, user_id UUID, action TEXT, target TEXT,
meta JSONB, created_at TIMESTAMPTZ DEFAULT now()
);
Indexes & Rules
• Timescale hypertable on biometrics(ts); retention policies (e.g., raw HR data 18
months).
• Vector indexes (HNSW/IVFFLAT) on recipes.embedding, exercises.embedding.
• RLS policies per org_id/user_id.
• Triggers to update meal_plans.total_kcal and macro totals on meal upserts.
4.4 API Surface (REST /v1, versioned)
Auth & Users
• POST /v1/auth/login / POST /v1/auth/refresh
• GET /v1/me (profile + clearance flags)
• PATCH /v1/me (non‑sensitive fields)
Intake & Safety
• POST /v1/intake {questionnaire} → normalized profile & risk flags
• POST /v1/intake/clearance {acknowledged:true} (unlocks plan if no critical
risk)
Program Lifecycle
• POST /v1/programs {start_date, goal} → draft plan
• POST /v1/programs/:id/activate
• GET /v1/programs/:id / list
• POST /v1/programs/:id/adjust {source:'weekly_checkin'|'manual',
params}
Nutrition
• GET /v1/programs/:id/macros?week=
• GET /v1/programs/:id/meal-plans?week=&day=
• POST /v1/meal-plans/:id/swap {meal_id, recipe_id? | constraints}
• GET /v1/programs/:id/grocery-list?week=
• POST /v1/pantry {name, qty, unit}
Training
• GET /v1/programs/:id/workouts?week=
• POST /v1/workouts/:id/log
{sets:[{exercise_id,set_idx,reps_done,weight_kg,rpe,pain,notes}]}
• POST /v1/workouts/:id/substitute {exercise_id, alt_exercise_id}
Habits & Mindset
• GET /v1/programs/:id/habits ; POST /v1/habits/:id/log
• GET /v1/programs/:id/mindset?week=
• POST /v1/journals {mood,stress,entry}
Check‑ins & Progress
• POST /v1/programs/:id/checkin {metrics, photos?}
• GET /v1/programs/:id/adjustments
• GET /v1/progress (trends, PRs, heatmaps)
Devices & Calendars
• POST /v1/devices/connect/:provider (OAuth)
• POST /v1/devices/sync {window}
• POST /v1/calendar/sync (Google Calendar read/write optional)
Messaging/Notifications
• POST /v1/messages {program_id, body}
• POST /v1/nudges/test {channel}
Exports
• POST /v1/programs/:id/export {targets:['pdf','csv','json']}
• GET /v1/exports/:id
Conventions
• All mutations require Idempotency‑Key.
• Errors: Problem+JSON with typed codes.
• Cursor pagination; strict RLS on user_id.
4.5 Orchestration Logic (CrewAI)
State machines
• Onboarding: created → screened → planned(draft) → active.
• Weekly review: awaiting_checkin → analyzing → adjusted → published.
Weekly Adjustment Pseudologic
• If 7‑day weight avg change < target by >30% for 2 wks AND adherence ≥80% → reduce
kcal 7–12%.
• If fatigue ≥ high OR sleep ≤ poor OR RPE ↑ while volume ↑ → deload week (-30–40%
volume).
• If steps << target → increase steps by +1–2k/day before kcal cuts.
• Mindset flags (cravings/binge risk) → introduce refeed or flexible tracking week.
4.6 Background Jobs
• GeneratePlan(programId) → nutrition + training + habits + mindset + grocery.
• ReflowSchedule(programId) after calendar changes.
• WeeklyCheckinDigest(userId) prompts with last week summary.
• ApplyAdjustments(programId) after check‑in.
• DeviceSync(userId, provider) every 6–12h.
• BuildReport(programId, period) → PDF/HTML.
• Housekeeping: PerformanceRollups, CostRollup, RetentionSweeper,
AlertOnFailure.
4.7 Realtime
• WS channels:
o program:{id}:today (timers, workout step changes)
o program:{id}:checkin (upload status, adjustment preview)
o chat:{programId} (messages)
• SSE fallback; presence awareness for coach/trainee.
4.8 Caching & Performance
• Redis: “today” plan, current workout, current day’s meals, pantry snapshot.
• Timescale compression for old biometrics; downsampled rollups for charts.
• SLOs:
o Generate day view < 500 ms P95 (cached).
o Weekly adjustment decision < 5 s P95 post‑check‑in.
o Workout timer latency < 150 ms P95 on WS.
4.9 Observability
• Traces across gateway → orchestrator → engines; tags: plan_id, user_id (hashed),
decision outcomes.
• Metrics: adherence %, weekly weight delta vs. target, adjustment frequency, deload
ratio, crash‑diet guard triggers, nudges sent/opened.
• Logs: structured JSON with PII scrubbing; full audit of adjustments.
5) Frontend Architecture (React 18 + Next.js 14)
5.1 Tech Choices
• Next.js 14 App Router, TypeScript.
• UI: shadcn/ui + Tailwind (mobile‑first).
• State/data: TanStack Query (server cache) + Zustand for workout timers & ephemeral
plan state.
• Realtime: WebSocket client (auto‑reconnect/backoff) + SSE fallback.
• Forms: react‑hook‑form + Zod (shared schemas).
• Charts: Recharts (trends, PRs, adherence heatmaps).
• Media: HLS player for exercise videos; camera capture for check‑in photos (optional).
5.2 App Structure
/app
/(marketing)/page.tsx
/(app)
dashboard/page.tsx
onboarding/
start/page.tsx
questionnaire/page.tsx
safety/page.tsx
summary/page.tsx
program/
page.tsx // Overview
today/page.tsx
nutrition/
page.tsx // Weekly macros & meals
[day]/page.tsx
training/
page.tsx // Week plan
[workoutId]/page.tsx // Player
habits/page.tsx
mindset/page.tsx
checkin/page.tsx
progress/page.tsx
grocery/page.tsx
schedule/page.tsx
messages/page.tsx
settings/
devices/page.tsx
profile/page.tsx
privacy/page.tsx
/components
IntakeForm/*
SafetyGate/*
MacroCard/*
MealCard/*
SwapModal/*
GroceryList/*
WorkoutCard/*
WorkoutPlayer/*
SetRow/*
RestTimer/*
ExerciseVideo/*
HabitTracker/*
MindsetCard/*
JournalEditor/*
CheckinWizard/*
TrendCharts/*
AdherenceHeatmap/*
ProgressCards/*
SchedulePlanner/*
MessageThread/*
/lib
api-client.ts
ws-client.ts
zod-schemas.ts
rbac.ts
/store
useTodayStore.ts
useWorkoutStore.ts
useMealStore.ts
useCheckinStore.ts
5.3 Key Pages & UX Flows
Onboarding
• IntakeForm (goals, equipment, diet, injuries); SafetyGate shows PAR‑Q results and
requires acknowledgment if any yellow flags; red flags block progression.
• Summary screen: projected timeline, example day, consent toggles.
Program Overview
• Tiles: this week’s calories/macros, workout split, habits, grocery link; progress chips
(weight Δ, adherence).
Today
• WorkoutCard (or Rest day) + MealCard stack; hydration meter; habit checklist; “I’m
traveling” toggle triggers Schedule Optimizer.
Nutrition → Day View
• Macro progress ring; meal list; SwapModal (filter by allergens, prep time, price; shows
macro deltas); “Cook mode” with step timers.
Training → Workout Player
• Set list; SetRow fields (reps, weight, RPE, pain); RestTimer auto‑advances;
ExerciseVideo inline with cues; “Substitute exercise” with safe alternatives.
Check‑in
• CheckinWizard: auto‑pull device metrics; uploads photos (optional); quick questions;
preview Adjustment with explanation.
Progress
• TrendCharts (weight 7‑day avg, circumference, PRs); AdherenceHeatmap;
fatigue/sleep overlay.
Grocery
• Weekly list grouped by aisle; pantry toggle; export to PDF/CSV; “Order via …” buttons
(if enabled).
Messages
• Chat with Accountability Buddy; templated nudges (“I missed today”; “traveling”).
5.4 Component Breakdown (Selected)
• WorkoutPlayer/RestTimer.tsx
Props: { restSec, onDone }; persists in useWorkoutStore; audible alert; WS sync for
coach view (optional).
• SwapModal/RecipeFinder.tsx
Props: { dayMacrosRemaining, constraints }; searches recipe embeddings; shows
macro delta & allergens; one‑tap replace updates meal plan + grocery list.
• TrendCharts/WeightTrend.tsx
Props: { series, targetRate }; displays 7‑day moving average; colors segment when
off‑target.
• CheckinWizard/PreviewAdjustments.tsx
Props: { proposed }; shows kcal/volume changes, deload flag, habit tweaks with
rationale & undo.
5.5 Data Fetching & Caching
• Server Components for static/weekly data (plans, recipes, exercises).
• TanStack Query for day‑level data (today plan, logs, check‑in).
• WS to live‑update timers and chat.
• Route prefetch: overview → today; training ↔ nutrition.
5.6 Validation & Error Handling
• Zod schemas validate intake, logs, check‑ins, swaps.
• Problem+JSON renderer with actionable fixes (e.g., “exercise substitution blocked
due to contraindication: shoulder impingement”).
• Idempotency‑Key on log submissions and adjustments.
• Safety rails: show high‑risk banners, auto‑lock plan when red flags appear.
5.7 Accessibility & i18n
• ARIA labels for timers, progress rings, sliders; large hit‑areas on mobile.
• High‑contrast & color‑blind‑safe palette; voice‑over tested flows.
• next-intl scaffolding; units toggle (metric/imperial); locales.
6) Integrations
• Wearables/Health: Apple HealthKit, Google Fit, Fitbit, Oura, Garmin (read scopes:
steps, HR, HRV, sleep, workouts).
• Food data: USDA FoodData Central (macro/micro lookup) and internal recipe DB.
• Calendars: Google Calendar (optional) for schedule reflow.
• Comms: Email/Push; Slack for org/coach notifications.
• Payments (optional coach orgs): Stripe (seats + metered coaching sessions).
• Storage: Drive/SharePoint export of weekly PDF reports.
7) DevOps & Deployment
• FE: Vercel.
• APIs/Workers: Render/Fly.io for simple; GKE for scale (CPU pool for planners;
memory pool for device sync).
• DB: Neon/Cloud SQL Postgres + Timescale + pgvector; PITR; daily backups.
• Cache: Upstash Redis.
• Object Store: S3/R2 (retention: photos 18 months by default).
• Event Bus: NATS managed/self‑hosted.
• CI/CD: GitHub Actions (lint/typecheck/unit/integration; Docker build; SBOM + cosign;
blue/green deploy; gated migrations).
• IaC: Terraform modules (DB, Redis, NATS, buckets, secrets, DNS/CDN).
• Testing
o Unit: TDEE/macros, planner constraints, workout progression logic, adjustment
engine, swap calculations.
o Contract: OpenAPI.
o E2E (Playwright): onboarding→plan→log→check‑in→adjust.
o Load: k6 (concurrent check‑ins, device sync).
o Chaos: delayed device APIs; partial data weeks.
o Security: ZAP; container scans; secret scanning.
• SLOs
o Day view < 500 ms P95 (cached).
o Weekly adjustment < 5 s P95 after check‑in.
o Device sync reliability ≥ 99% within 24h.
8) Success Criteria
Product KPIs
• Adherence: ≥ 75% average habit/meal/workout adherence after 4 weeks.
• Outcome: median fat‑loss cohorts within ±20% of target rate by week 4.
• Engagement: daily “Today” open rate ≥ 70% first 2 weeks; 30‑day retention ≥ 55%.
• Safety: 100% red‑flag gating events properly blocked until cleared.
Engineering SLOs
• <0.5% 5xx/1k req; 99.9% uptime core APIs; WS drop‑reconnect within 2 s P95.
• Data lag from devices < 6h P95.
9) Security & Compliance
• RBAC: Owner/Coach/Member/Viewer; coach access is explicit invite + audit.
• Encryption: TLS 1.2+ in transit; AES‑256 at rest; token envelope via KMS.
• PII/PHI handling: data minimization; explicit consent for photos; optional HIPAA
alignment (if serving covered entities).
• Tenant isolation: Postgres RLS; S3 prefix isolation; signed URLs.
• Safety guardrails: PAR‑Q enforcement; injury/medication flags restrict exercise pool;
“consult clinician” banners.
• Privacy: granular toggles for device data scopes; DSR endpoints (export/delete).
• Audit: immutable audit of plan changes, adjustments, and access events.
• Supply chain: SLSA provenance; image signing; dependency pinning; Dependabot.
10) Visual/Logical Flows
A) Onboarding → Plan
Questionnaire → Safety screen → Profile normalization → Nutritionist sets macros &
periodization → Trainer builds mesocycle & sessions → Psychologist assigns practices →
Grocery Planner compiles list → Program active.
B) Daily Flow
Open Today → do workout (timers/log) → log meals (or swap) → tick habits → hydration →
journal (optional) → nudges if missed.
C) Weekly Check‑in & Adjust
User submits check‑in → Progress Analyst evaluates (weight trend, adherence, fatigue,
sleep, steps) → propose adjustments (kcal/volume/deload/habits) with rationale → user
accepts → next week’s plan updated.
D) Schedule Conflicts
Calendar change → Schedule Optimizer reflows sessions/meals → notifies user;
preserves rest spacing and macro distribution rules.
E) Swap Meal
User opens SwapModal → constraints applied (macros remaining, allergens, prep time) →
pick recipe → macros rebalanced; grocery list diff updated.
F) Injury Flag During Set
Set logged with pain=true → Safety Screener triggers: immediate substitutions for that
pattern + clinician banner; plan limits volume on affected pattern for the microcycle.