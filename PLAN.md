# Project Plan — Health & Wellness Advisor Crew

> Scope: Ship an MVP that runs end‑to‑end **onboarding → plan generation → day view → weekly check‑in → auto‑adjustments → weekly report**, with strict safety gates (PAR‑Q) and auditability.

## Current Goal
Deliver a safe, adaptive 12‑week coaching experience that covers **training, nutrition, habits/mindset, grocery**, and **weekly adjustments from real‑world data** (logs + wearables).

## Safety Stance (product)
- **Not a medical device.** Present clear disclaimers and block plan creation when PAR‑Q red flags are present until the user confirms medical clearance.
- Enforce **contraindication filters** on exercise selection and substitutions.
- Escalate to “consult a licensed professional” on **risk triggers** (e.g., chest pain, syncope, injury, eating‑disorder risk signals).

## 80/20 Build Strategy
- **80% [Cursor]**: Monorepo, DB schema + migrations (Postgres + Timescale + pgvector), NestJS API (RBAC, OpenAPI, Problem+JSON, Idempotency), WS/SSE, FE (Today/Nutrition/Training/Check‑in/Progress), planners (deterministic math), exporters, observability, tests.
- **20% [Claude]**: CrewAI orchestration prompts (Nutritionist/Trainer/Psychologist/Progress Analyst/etc.), swap recommendations phrasing, mindset copy, schedule optimizer heuristics, check‑in summarizations.

## Next 3 Tasks
1. **[Cursor]** Scaffold monorepo + `docker-compose.dev` (Postgres+Timescale, Redis, NATS, MinIO) + `.env.example` + GitHub Actions (lint/test/build, SBOM + signing).
2. **[Cursor]** Implement NestJS modules: auth, intake/safety, programs, nutrition (macros/meal plans/grocery), training (workouts/logs/substitutions), habits/mindset, check‑ins/adjustments, devices, messages, exports; emit WS events.
3. **[Claude]** Orchestrator (FastAPI + CrewAI) FSMs (onboarding + weekly review) and tool adapters (Calc.tdee, Macros.plan, Workouts.generate, Meals.generate, Adjustments.evaluate, Devices.pull, Grocery.compile, Mindset.assign, Schedule.solve).

## Phase Plan
- **P0** Repo/infra/CI
- **P1** DB + API contracts + auth/RLS
- **P2** Intake + Safety gate
- **P3** Planners: TDEE/macros + meal plans + grocery
- **P4** Training periodization + workout player/logs
- **P5** Habits/mindset + nudges
- **P6** Weekly check‑in + adjustment engine + rationale
- **P7** Devices (Fitbit/Oura/Garmin first) + data sync
- **P8** Reports/exports + schedule optimizer
- **P9** Analytics + hardening + tests
- **P10** Cost guardrails, dashboards, docs

## Definition of Done (MVP)
- Onboarding with **PAR‑Q**: red flags → plan blocked; yellow flags → warnings + acknowledgment.
- Program generator produces **12‑week plan**: macro periodization + workouts (sets/reps/tempo/RIR) + habits + mindset + weekly grocery.
- **Today** shows workouts, meals, habits, hydration; **SwapModal** respects macros/allergens/equipment.
- Weekly **Check‑in** ingests logs + devices; **Adjustments** compute kcal/volume/deload with human‑readable rationale.
- **Contraindication** engine prevents unsafe exercise selections/substitutions.
- Realtime WS (timers, check‑in progress, chat), audit logs for adjustments/overrides.
- Exports: weekly PDF report, grocery CSV/PDF; full data export (JSON).
- SLOs: **Day view < 500 ms P95** (cached); **Weekly adjustment < 5 s P95** post check‑in.
