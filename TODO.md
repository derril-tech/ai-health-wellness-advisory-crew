# TODO — Health & Wellness Advisor Crew
> 80/20: **[Cursor]** infra/contracts/UI/engines; **[Claude]** agent flows/prompts/copy.

## Phase 0 — Repo, Infra, CI/CD ✅
- [ ] [Cursor] GitHub Actions: lint/typecheck/test, Docker build, SBOM + cosign, gated deploys, migrations.

## Phase 1 — DB & API Contracts ✅
- [x] [Cursor] SQL migrations for tables in ARCH; RLS policies; Timescale hypertable; vector indexes.
- [x] [Cursor] NestJS modules:
  - [x] Auth (Auth.js), RBAC guards, org scoping.
  - [x] Intake/Safety: PAR‑Q rules, clearance flags, audit.
  - [x] Programs: create/activate/list, adjustments endpoint.
  - [x] Nutrition: macros/meal plans, swaps, grocery, pantry.
  - [ ] Training: workouts/sets, logs, substitutions with contraindication checks.
  - [ ] Habits/Mindset: CRUD + logs.
  - [ ] Check‑ins/Progress: create + trends; adjustments listing.
  - [ ] Devices: OAuth connects, sync jobs, normalize readings.
  - [ ] Messages/Nudges, Exports.
  - [ ] Middlewares: Idempotency, Problem+JSON, correlation ids, rate limits.

## Phase 2 — Intake & Safety ✅
- [x] [Cursor] Intake normalizer + risk rules; SafetyGate UI; explicit ack flows; blocked plan state.
- [x] [Claude] Copy for warnings/escalations; friendly screening prompts.

## Phase 3 — Nutrition Engine & Meals ✅
- [x] [Cursor] `tdee-macro-engine` (deterministic); weekly macro targets + periodization; swap math (macro deltas).
- [x] [Cursor] `mealplanner` (constraints: macros, allergens, skill, prep time); pantry integration.
- [x] [Cursor] FE: **Nutrition** pages + **SwapModal**; **Grocery** pages (CSV/PDF export).
- [x] [Claude] Meal descriptions, cooking tips, macro‑equivalent swap phrasing.

## Phase 4 — Training & Player ✅
- [x] [Cursor] `workout-periodization` (upper/lower or push/pull/legs with overload + deloads); workout player (timers, logs, substitution).
- [x] [Cursor] Library CRUD for exercises (contraindications, progressions); embedded HLS videos.
- [x] [Claude] Coaching cues, regression/progression notes.

## Phase 5 — Habits, Mindset, Nudges ✅
- [x] [Cursor] Habit engine + tracker + logs; mindset practice assignments; notifications scheduler.
- [x] [Claude] Mindset scripts, journaling prompts, adherence troubleshooting messages.

## Phase 6 — Weekly Check‑ins & Adjustments ✅
- [x] [Cursor] `progress-analyzer` implementing heuristics (weight trend, adherence, fatigue/sleep, steps) → kcal/volume/deload/habits + rationale.
- [x] [Cursor] **CheckinWizard** + **PreviewAdjustments** UI; audit log entries.
- [x] [Claude] Summaries and empathetic rationales.

## Phase 7 — Devices & Schedule Optimizer ✅
- [x] [Cursor] Device connectors (Fitbit/Oura/Garmin first) + cron sync; normalize steps/HR/HRV/sleep.
- [x] [Cursor] `schedule-optimizer` + **SchedulePlanner** UI; preserve spacing constraints.
- [x] [Claude] Conflict‑resolution copy and suggestions.

## Phase 8 — Reports & Exports ✅
- [x] [Cursor] `reporter` (weekly PDF/HTML), grocery CSV/PDF; full JSON export; signed URLs.
- [x] [Cursor] Progress charts (7‑day avg, adherence heatmaps, PR logbook).

## Phase 9 — Observability, Guardrails, Costs ✅
- [x] [Cursor] OTel tracing, Grafana dashboards, Sentry; token/cost buckets; concurrency caps; retention & data deletion flows.
- [x] [Cursor] Safety regression tests (PAR‑Q, contraindications, deload triggers).

## Phase 10 — Testing Matrix ✅
- [x] [Cursor] Unit: TDEE/macros math, swap calculations, periodization, adjustment rules.
- [x] [Cursor] Contract: OpenAPI + Zod parity; Problem+JSON renderer.
- [x] [Cursor] E2E: onboarding→plan→log→check‑in→adjust→report (Playwright).
- [x] [Cursor] Load: concurrent check‑ins/device sync (k6).
- [x] [Cursor] Chaos: delayed device APIs; partial weeks; WS drops.
- [x] [Cursor] Security: ZAP, dependency scans, secret scanning; signed URL scope tests.

## Out‑of‑Scope (MVP)
- Clinical rehab protocols, medication dosing, diagnostics (explicitly excluded).
- Voice coaching; full HIPAA BAA (flagged for enterprise).
