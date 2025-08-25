# Architecture — Health & Wellness Advisor Crew

## Topology
- **Frontend**: Next.js 14 (Vercel), TS, shadcn/Tailwind, TanStack Query + Zustand (timers/ephemeral), TipTap (journals), Recharts (trends/heatmaps), WS/SSE.
- **API Gateway**: NestJS (REST, OpenAPI 3.1, RBAC, Idempotency‑Key, Problem+JSON, rate limits, signed URLs).
- **Auth**: Auth.js + short‑lived JWT; SAML/OIDC (orgs); SCIM (coach orgs).
- **Orchestrator**: FastAPI + CrewAI; FSMs: onboarding and weekly review.
- **Workers (Python)**: `intake-normalizer`, `tdee-macro-engine`, `mealplanner`, `workout-periodization`, `habit-engine`, `progress-analyzer`, `device-ingestor`, `grocery-builder`, `reporter`.
- **Infra**: NATS bus; Celery (Redis/NATS); Postgres + **Timescale** (biometrics), **pgvector** (recipes/exercises); S3/R2; Upstash Redis; OTel + Prometheus/Grafana + Sentry; Vault/KMS.

## Data Model (overview)
- Tenancy & Identity: `orgs`, `users`, `roles`.
- Health & Safety: `health_profiles` (injuries/meds/PAR‑Q, clearance flag).
- Devices & Biometrics: `devices`, `biometrics` (Timescale hypertable).
- Programs: `programs` (12‑week), `macro_targets`, `meal_plans`/`meals`, `grocery_lists`, `pantry_items`.
- Libraries: `recipes`, `exercises` (embeddings + tags + contraindications).
- Training: `workouts`, `workout_sets`, `workout_logs`.
- Habits/Mindset: `habits`, `habit_logs`, `mindset_practices`, `journals`.
- Check‑ins & Adjustments: `checkins`, `adjustments`.
- Messaging/Exports/Audit: `messages`, `nudges`, `exports`, `audit_log`.

## API Surface (v1 highlights)
- **Auth & Me**: `POST /auth/login`, `POST /auth/refresh`, `GET /me`, `PATCH /me`.
- **Intake & Safety**: `POST /intake` (normalize + risk), `POST /intake/clearance`.
- **Programs**: `POST /programs`, `POST /programs/:id/activate`, `GET /programs/:id`, `POST /programs/:id/adjust`.
- **Nutrition**: `GET /programs/:id/macros?week=`, `GET /programs/:id/meal-plans?week=&day=`, `POST /meal-plans/:id/swap`, `GET /programs/:id/grocery-list?week=`, `POST /pantry`.
- **Training**: `GET /programs/:id/workouts?week=`, `POST /workouts/:id/log`, `POST /workouts/:id/substitute`.
- **Habits/Mindset**: `GET /programs/:id/habits`, `POST /habits/:id/log`, `GET /programs/:id/mindset?week=`, `POST /journals`.
- **Check‑ins**: `POST /programs/:id/checkin`, `GET /programs/:id/adjustments`, `GET /progress`.
- **Devices/Calendars**: `POST /devices/connect/:provider`, `POST /devices/sync`, `POST /calendar/sync` (optional).
- **Messaging/Notifications**: `POST /messages`, `POST /nudges/test`.
- **Exports**: `POST /programs/:id/export`, `GET /exports/:id`.
Conventions: Idempotency on all writes, Problem+JSON errors, cursor pagination, strict RLS on `org_id`/`user_id`.

## Agents & Tools
**Agents**: Safety Screener, Nutritionist, Trainer, Psychologist, Accountability Buddy, Progress Analyst, Grocery Planner, Schedule Optimizer, Librarian.  
**Tool Interfaces**:
- `Calc.tdee(profile)` → kcal/day (Mifflin‑St Jeor + activity).
- `Macros.plan(goal,timeline,preference)` → week‑by‑week kcal/macros (+ refeeds/diet breaks optional).
- `Meals.generate(day,constraints)` → recipes that meet macro window, allergens, skill level.
- `Workouts.generate(week,split,constraints)` → sessions with sets/reps/tempo/RIR/rest.
- `Adjustments.evaluate(progress)` → `{kcal_delta, volume_delta, deload?, habit_deltas}` with rationale.
- `Devices.pull(conn,window)` → steps/hr/hrv/sleep normalization.
- `Grocery.compile(week,pantry)` → deduped list with quantities/aisles.
- `Mindset.assign(week,issues)` → practices/journaling.
- `Schedule.solve(calendar,availability)` → reflow respecting spacing constraints.

## Deterministic Core Heuristics (MVP)
- **TDEE**: Mifflin‑St Jeor with activity multiplier; deficit/surplus capped (±15%) for safety; TEF ~10%.
- **Macros**: protein 1.6–2.2 g/kg (goal‑dependent), fats ≥0.6 g/kg, carbs fill remainder; fiber 14 g/1k kcal; sodium targets adjustable.
- **Weight‑loss pacing**: 0.5–1.0% body‑weight/week default; slower if high fatigue/low sleep.
- **Adjustments** (weekly):
  - If 7‑day avg delta < 70% of target for 2 consecutive weeks & adherence ≥80% → **‑7–12% kcal** (or +1–2k steps before kcal if steps low).
  - If fatigue ↑ or sleep poor or RPE ↑ with rising volume → **deload** (‑30–40% volume).
  - Prefer step/habit increases before further kcal cuts when adherence is low.
- **Contraindications**: pattern×injury rules filter exercise pool and block substitutions.
- **Hydration**: baseline 30–35 ml/kg/day, add per activity/climate note (informational).

> These rules are **product logic**, not clinical guidance. Always show the safety disclaimer in‑app.

## Realtime Channels
- `program:{id}:today` — workout timers, meal/habit ticks.
- `program:{id}:checkin` — uploads + adjustment preview.
- `chat:{programId}` — coach/bot messaging.
SSE fallback; presence for coach/trainee.

## Security & Compliance
RBAC (Owner/Coach/Member/Viewer), Postgres RLS, S3 prefix scoping, signed URLs, token envelope encryption (KMS), PII scrubbing in logs, explicit consents (photos/devices). PAR‑Q gating and **immutable audit** for plan changes/adjustments. Optional HIPAA alignment if serving covered entities (feature‑flag: voice off, restricted scopes).

## Deployment & SLOs
FE: Vercel. APIs/Workers: Render/Fly → GKE at scale (separate pools for planners vs. device sync).  
DB: Neon/Cloud SQL + Timescale + pgvector; PITR. Cache: Upstash Redis. Bus: NATS.  
SLOs: Day view **< 500 ms P95**; weekly adjustment **< 5 s P95**; device sync **≥ 99% within 24h**; WS reconnect **< 2 s P95**.
