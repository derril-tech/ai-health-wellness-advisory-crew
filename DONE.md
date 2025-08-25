# DONE — Health & Wellness Advisor Crew

## Phase 0 — Repo, Infra, CI/CD

[2024-12-19] [Cursor] Monorepo: `apps/{frontend,gateway,orchestrator,workers}`, `packages/{sdk}`.
[2024-12-19] [Cursor] `docker-compose.dev.yml`: Postgres(+Timescale), Redis, NATS, MinIO; healthchecks; seed data.
[2024-12-19] [Cursor] `env.example` with DB/REDIS/NATS/S3/JWT/OAuth/device provider placeholders.

## Phase 1 — Database & API Contracts

[2024-12-19] [Cursor] SQL migrations for tables in ARCH; RLS policies; Timescale hypertable; vector indexes.
[2024-12-19] [Cursor] NestJS modules: Auth (Auth.js), RBAC guards, org scoping.
[2024-12-19] [Cursor] NestJS modules: Intake/Safety: PAR‑Q rules, clearance flags, audit.
[2024-12-19] [Cursor] NestJS modules: Programs: create/activate/list, adjustments endpoint.
[2024-12-19] [Cursor] NestJS modules: Nutrition: macros/meal plans, swaps, grocery, pantry.

## Phase 2 — Intake & Safety

[2024-12-19] [Cursor] Intake normalizer + risk rules; SafetyGate UI; explicit ack flows; blocked plan state.
[2024-12-19] [Claude] Copy for warnings/escalations; friendly screening prompts.

## Phase 3 — Nutrition Engine & Meals

[2024-12-19] [Cursor] `tdee-macro-engine` (deterministic); weekly macro targets + periodization; swap math (macro deltas).
[2024-12-19] [Cursor] `mealplanner` (constraints: macros, allergens, skill, prep time); pantry integration.
[2024-12-19] [Cursor] FE: **Nutrition** pages + **SwapModal**; **Grocery** pages (CSV/PDF export).
[2024-12-19] [Claude] Meal descriptions, cooking tips, macro‑equivalent swap phrasing.

## Phase 4 — Training & Player

[2024-12-19] [Cursor] `workout-periodization` (upper/lower or push/pull/legs with overload + deloads); workout player (timers, logs, substitution).
[2024-12-19] [Cursor] Library CRUD for exercises (contraindications, progressions); embedded HLS videos.
[2024-12-19] [Claude] Coaching cues, regression/progression notes.

## Phase 5 — Habits, Mindset, Nudges

[2024-12-19] [Cursor] Habit engine + tracker + logs; mindset practice assignments; notifications scheduler.
[2024-12-19] [Claude] Mindset scripts, journaling prompts, adherence troubleshooting messages.

## Phase 6 — Weekly Check-ins & Adjustments

[2024-12-19] [Cursor] `progress-analyzer` implementing heuristics (weight trend, adherence, fatigue/sleep, steps) → kcal/volume/deload/habits + rationale.
[2024-12-19] [Cursor] **CheckinWizard** + **PreviewAdjustments** UI; audit log entries.
[2024-12-19] [Claude] Summaries and empathetic rationales.

## Phase 7 — Devices & Schedule Optimizer

[2024-12-19] [Cursor] Device connectors (Fitbit/Oura/Garmin first) + cron sync; normalize steps/HR/HRV/sleep.
[2024-12-19] [Cursor] `schedule-optimizer` + **SchedulePlanner** UI; preserve spacing constraints.
[2024-12-19] [Claude] Conflict‑resolution copy and suggestions.

## Phase 8 — Reports & Exports

[2024-12-19] [Cursor] `reporter` (weekly PDF/HTML), grocery CSV/PDF; full JSON export; signed URLs.
[2024-12-19] [Cursor] Progress charts (7‑day avg, adherence heatmaps, PR logbook).

## Phase 9 — Observability, Guardrails, Costs

[2024-12-19] [Cursor] OTel tracing, Grafana dashboards, Sentry; token/cost buckets; concurrency caps; retention & data deletion flows.
[2024-12-19] [Cursor] Safety regression tests (PAR‑Q, contraindications, deload triggers).

## Phase 10 — Testing Matrix

[2024-12-19] [Cursor] Unit: TDEE/macros math, swap calculations, periodization, adjustment rules.
[2024-12-19] [Cursor] Contract: OpenAPI + Zod parity; Problem+JSON renderer.
[2024-12-19] [Cursor] E2E: onboarding→plan→log→check‑in→adjust→report (Playwright).
[2024-12-19] [Cursor] Load: concurrent check‑ins/device sync (k6).
[2024-12-19] [Cursor] Chaos: delayed device APIs; partial weeks; WS drops.
[2024-12-19] [Cursor] Security: ZAP, dependency scans, secret scanning; signed URL scope tests.
