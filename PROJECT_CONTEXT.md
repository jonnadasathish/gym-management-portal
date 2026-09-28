# Gym Management Portal — PROJECT_CONTEXT.md

> **Document purpose:** This is the living implementation memory for the Gym Management Portal.
>
> It is maintained according to `AGENTS.md`.
>
> `PRD.md` defines **what the product must be**.
>
> `AGENTS.md` defines **how the AI/development team must work**.
>
> `PROJECT_CONTEXT.md` defines **the current known implementation state, approved decisions, history, TODOs, blockers, tests, and handoff information**.
>
> This file must never be treated as a one-time project plan. It must be updated continuously after meaningful development work.

---

# 1. Current State

## 1.1 Project Identity

| Field | Value |
|---|---|
| Product | Gym Management Portal |
| PRD Version | 1.0 |
| PRD Date | September 24, 2026 |
| PRD Status | Draft — Product/Engineering Ready |
| Target Market | India |
| Target Customers | Independent gyms and small multi-location gym chains |
| Initial Gym Size | 100–500 members/location |
| Platform | Responsive web portal |
| Member Experience | Same platform, role-specific screens, mobile-responsive |
| Frontend | Vue |
| Backend | Python Django |
| API Layer | Django REST Framework |
| Database | MySQL |
| Cloud | AWS |
| Initial Payment Gateway | Razorpay |
| Target Delivery | 8 weeks |
| Budget Tier | Mid-market |

## 1.2 Current Project Status

**Status:** IMPLEMENTING — implementable V1 leftovers closed (GYM-018). Remaining gaps are product/ops blocked, not leftover coding tasks.

**Overall MVP Progress:** Domain + HTTP APIs + Vue staff/owner/member surfaces exist through Phase 6. Implementable Must leftovers from GYM-017 (renew UI, freeze request+approve, portal cancel, trainer PT today, PT reschedule, member status sync, branch revenue, login throttle, biometric adapter interface, subscription list, member initiate via FakePaymentProvider) landed in GYM-018. AWS and live Razorpay HTTPS are not started. Recurring charge/retry, waitlist auto-promote, GST legal rules, and WhatsApp/SMS vendors remain intentionally unimplemented.

**Current Phase:** GYM-019 Apex Pulse domain styling applied across Vue modules.

**Current Module:** Frontend presentation (Apex Pulse design system).

**Current Task:** Record GYM-019. Product/ops blockers unchanged. Do not invent waitlist auto-promote, GST, recurring-retry policy, live Razorpay, or AWS.

**Application Code Status:** Staff renew + freeze-request approve/reject; portal cancel/pay/freeze-request; trainer Today + reschedule; `sync_member_status`; dashboard `revenue.by_branch`; login 5/min; biometric adapter interface; subscription list (no charge); member `POST /payments/initiate/` via FakePaymentProvider when Razorpay keys are empty.

**Database Schema Status:** `memberships.0003_freeze_request` added `FreezeRequest`.

**API Status:** Prior groups plus freeze-request approve/reject, PT reschedule, payments subscriptions list, payments initiate, dashboard `by_branch`.

**Frontend Status:** IMPLEMENTING — Apex Pulse dark shell (GYM-019): sidebar, cinematic login, KPI cards, status pills on every staff/member view. Business APIs unchanged.

**Infrastructure Status:** Local docker-compose. No AWS.

**Testing Status:** **245 passed, 0 failed** — `docker compose run --rm backend pytest -q` executed 2026-09-28 after GYM-018. Frontend: vitest 1 passed + `vite build` succeeded.

**Production Status:** Not started.

## 1.3 Important Current Fact

Phase 1–6 domain foundations plus Vue staff/owner/member surfaces are in the repository and tested (245 backend tests after GYM-018). Implementable V1 leftovers are closed. Do not treat modules as `COMPLETE`: Razorpay `create_order`/`process_refund` have **not** been executed against a real gateway; waitlist auto-promotion is intentionally absent (AGENTS.md §23.4); recurring `Subscription` charge/retry is visibility-only; WhatsApp/SMS remain console/in-app only (DEC-022); AWS is not started. These are blocked/deferred product-ops items, not leftover implementation tasks.

---

# 2. Source of Truth

The project follows this hierarchy:

```text
Current Explicit User Instruction
        ↓
PRD.md
        ↓
Previously Approved Decisions in PROJECT_CONTEXT.md
        ↓
Approved Architecture / Data / API Decisions
        ↓
Existing Code and Tests
        ↓
AI Reasoning / Suggestions
```

## 2.1 Product Source

Primary product specification:

```text
PRD.md
```

The PRD is the baseline for:

- product scope
- user personas
- roles
- user stories
- functional requirements
- acceptance criteria
- non-functional requirements
- technical baseline
- roadmap
- risks
- open questions
- MVP priority

## 2.2 Engineering Source

Primary engineering operating contract:

```text
AGENTS.md
```

## 2.3 Living Project Memory

Current state and historical project memory:

```text
PROJECT_CONTEXT.md
```

## 2.4 No Silent Requirement Invention

When the PRD or existing approved project state does not specify an important behavior:

```text
DO NOT GUESS
        ↓
Record as OPEN QUESTION
        ↓
Identify affected areas
        ↓
Resolve explicitly
        ↓
Record approved decision
```

---

# 3. Product Baseline

## 3.1 Product Summary

The Gym Management Portal is a multi-location SaaS platform intended to help gym owners and staff manage:

- members
- memberships
- attendance
- billing
- payments
- classes
- personal training
- trainers
- workout plans
- member progress
- notifications
- reporting
- member self-service

Members use the same responsive web platform through member-specific functionality.

## 3.2 Product Problem

The product addresses operational fragmentation caused by combinations of:

- Excel / Google Sheets
- paper attendance
- WhatsApp
- manual payment records
- separate biometric systems
- trainer notebooks
- accounting tools
- calendars
- manual renewal reminders

## 3.3 Product North Star

The PRD defines the central operational workflow as:

```text
Acquire
   ↓
Register
   ↓
Sell Membership
   ↓
Collect Payment
   ↓
Check In
   ↓
Schedule
   ↓
Train
   ↓
Track Progress
   ↓
Renew
   ↓
Retain
```

The most important V1 workflows are:

```text
Membership renewal
        +
Payment collection
        +
Member retention
```

## 3.4 Product Goals

The PRD targets:

| Goal | Target |
|---|---:|
| Reduce manual member-management work | ≥40% |
| Reduce renewal tracking time | ≥50% |
| Reduce billing entry errors | ≥60% |
| Member self-service | ≥50% of routine requests |
| Average check-in time | <10 seconds |
| Digital payment adoption | ≥50% of payments |
| Expiring-member follow-up coverage | ≥90% |
| Owner visibility | Daily real-time dashboard |
| Multi-branch support | V1 |

## 3.5 Product KPIs

### Adoption

- % members with complete profiles
- Daily active staff users
- Weekly active members
- % memberships managed through the platform

### Revenue

- Monthly recurring revenue processed
- Collection rate
- Outstanding dues
- Renewal conversion rate
- Failed payment recovery rate

### Engagement

- Average visits/member/month
- Class booking rate
- PT session completion
- Member portal login rate

### Retention

- Membership renewal rate
- Membership expiry rate
- Freeze rate
- Cancellation rate
- 30/60/90-day retention

---

# 4. Product Assumptions

The following assumptions come directly from the PRD:

1. Multiple branches are supported from V1.
2. Initial target scale is approximately 100–500 active members per location.
3. Architecture should support growth beyond that initial size.
4. India is the initial market.
5. INR is the default currency.
6. Razorpay is the initial payment gateway.
7. Payment providers should be abstracted so other gateways can be added later.
8. WhatsApp/SMS are desirable; critical transactional notifications are prioritized.
9. Members use the same responsive web platform in V1.
10. Native apps are Phase 2.
11. Roles are fixed as Owner, Front Desk/Admin, Trainer/Coach, Member.
12. GST-ready invoicing is required for the India market.
13. Biometric/RFID integrations use an adapter/API approach.
14. Initial data migration supports CSV/Excel and a migration framework.
15. Advanced AI coaching is out of scope for V1.
16. Eight-week delivery prioritizes operational workflows over advanced analytics/automation.

---

# 5. Non-Goals

The following are outside V1 according to the PRD:

- Full accounting/ERP
- Payroll processing
- Advanced HR management
- Native iOS/Android apps
- AI-generated workout plans
- AI personal trainer
- Nutrition / meal planning engine
- Gym/trainer marketplace
- Gym equipment IoT management
- Full POS / retail inventory
- Franchise royalty management
- Advanced marketing automation
- Video workout streaming
- Insurance management
- Hardware manufacturing
- Direct biometric hardware control for every vendor
- International tax compliance

---

# 6. User Personas

## 6.1 Gym Owner

**Primary objective:** Run the business and increase revenue.

Key needs:

- business performance visibility
- collections monitoring
- churn reduction
- branch management
- staff monitoring
- attendance visibility
- renewal tracking

## 6.2 Front Desk/Admin Staff

**Primary objective:** Process daily gym operations quickly.

Key needs:

- member registration
- payment collection
- check-in
- renewals
- booking management
- member support

## 6.3 Trainer / Coach

**Primary objective:** Manage assigned clients and training activity.

Key needs:

- assigned clients
- PT sessions
- workout plans
- progress
- class schedules

## 6.4 Member

**Primary objective:** Manage gym participation without depending on reception.

Key needs:

- membership status
- payments
- invoices
- attendance
- classes
- PT
- workouts
- progress
- freeze/renewal
- notifications
- trainer-related interactions

---

# 7. Roles and Permission Baseline

Roles are fixed for V1:

```text
OWNER
FRONT_DESK_ADMIN
TRAINER
MEMBER
```

The PRD role matrix is:

| Feature | Owner | Front Desk | Trainer | Member |
|---|:---:|:---:|:---:|:---:|
| Dashboard | Full | Full | Limited | Personal |
| Member Management | Full | Full | Assigned clients | Own profile |
| Membership Plans | Full | Manage | View | View |
| Membership Renewal | ✓ | ✓ | View | Self-service |
| Attendance | Full | Full | View | Own |
| Billing | Full | Manage | View PT | Own payments |
| Classes | Full | Manage | Own classes | Book |
| PT | Full | Manage | Own clients | Book |
| Trainer Management | Full | Limited | Own profile | — |
| Leads/CRM | Full | Full | Assigned leads | — |
| Reports | Full | Operational | Personal | Personal |
| Workout Plans | Full | View | Manage clients | View |
| Progress | Full | View | Manage | Own |
| Branch Management | Full | Assigned branch | Assigned branch | Home branch |
| Settings | Full | Limited | Own profile | Own profile |

### Important Authorization Rule

The exact technical authorization mechanism is **not yet implemented**.

The implementation must preserve the functional role boundaries above and must enforce authorization on the backend.

---

# 8. Core Product Flow

The product's core operational domain flow is:

```text
Organization
   ↓
Branch
   ↓
User / Staff / Trainer
   ↓
Member
   ↓
Membership Plan
   ↓
Membership
   ↓
Billing / Invoice
   ↓
Payment
   ↓
Attendance
   ↓
Class / PT
   ↓
Workout
   ↓
Progress
   ↓
Renewal / Retention
```

Supporting domains:

```text
Notifications
Reports
Dashboard
CRM / Leads
Audit
Integrations
Migration
```

---

# 9. Requirement Traceability

## 9.1 Requirement ID Convention

Requirements are tracked as:

```text
REQ-001
REQ-002
REQ-003
...
```

Requirement IDs must never be reused or renumbered once assigned.

> **Correction note (GYM-002):** An earlier pass of this document used the
> non-conforming prefix `REQ-US-001`…`REQ-US-020` for the PRD §7 user stories.
> This violated the `REQ-XXX` convention mandated by `AGENTS.md` §7. No code,
> tests, or external references existed against those IDs (project was still
> pre-implementation), so they have been renumbered in place to `REQ-001`…
> `REQ-020` below with no loss of information. This correction is recorded
> here rather than silently applied, per `AGENTS.md` §5.3 / §57 (context
> integrity — failed/incorrect prior states must remain visible).

## 9.2 Requirement Status Values

```text
NOT_STARTED
ANALYSIS
DESIGNED
IMPLEMENTING
TESTING
REVIEW
COMPLETE
BLOCKED
DEFERRED
```

## 9.3 Requirement Coverage Table

Columns follow `AGENTS.md` §7: requirement ID, PRD reference, requirement
text, priority, module, implementation status, test status, verification
status, notes.

Coverage includes both PRD §7 user stories and the module-level / non-functional
requirements from PRD §8–§10 that are not already expressed as a user story.
All statuses are `NOT_STARTED` — the application has no implementation yet.

### User Stories (PRD §7)

| ID | PRD Ref | Requirement | Priority | Module | Impl | Test | Verified | Notes |
|---|---|---|---|---|---|---|---|---|
| REQ-001 | US-001 | Owner sees today's revenue (collected/pending/refunded) | Must | Dashboard, Billing | IMPLEMENTING | TESTING | NOT_STARTED | `GET /reports/dashboard/` OWNER only; Vue `/dashboard` |
| REQ-002 | US-002 | Admin registers a member with mandatory fields + plan | Must | Members | IMPLEMENTING | TESTING | NOT_STARTED | API+Vue register; plan sold on member detail |
| REQ-003 | US-003 | Admin checks a member in within 10s | Must | Attendance | IMPLEMENTING | TESTING | NOT_STARTED | Staff check-in API+Vue; interval still provisional |
| REQ-004 | US-004 | Member scans QR to record attendance | Must | Attendance | IMPLEMENTING | TESTING | NOT_STARTED | `qr_payload` check-in + Vue paste/BarcodeDetector; no biometric vendor |
| REQ-005 | US-005 | Owner sees expiring memberships (configurable window) | Must | Dashboard, Memberships | IMPLEMENTING | TESTING | NOT_STARTED | Dashboard `expiring_7` / `expiring_30`; window not owner-configurable |
| REQ-006 | US-006 | Member pays dues online; gateway success updates balance | Must | Member Portal, Payments | IMPLEMENTING | TESTING | NOT_STARTED | Portal Pay → `POST /payments/initiate/` (FakePaymentProvider when keys empty); webhook still settles; real Razorpay create_order NOT EXECUTED |
| REQ-007 | US-007 | Admin freezes a membership; expiry recalculated | Must | Memberships | IMPLEMENTING | TESTING | NOT_STARTED | Staff freeze/unfreeze Vue uses existing API; policy default still OQ-005 |
| REQ-008 | US-008 | Member books a class only if capacity available | Must | Classes | IMPLEMENTING | TESTING | NOT_STARTED | Sequential + threaded last-seat tests |
| REQ-009 | US-009 | Trainer sees today's PT sessions on a calendar | Must | Personal Training, Trainers | IMPLEMENTING | TESTING | NOT_STARTED | PT Vue "Today" filters local date; not a full calendar widget |
| REQ-010 | US-010 | Trainer records a workout against member/date | Must | Workouts | IMPLEMENTING | TESTING | NOT_STARTED | `POST /workouts/logs/` + Vue Workouts |
| REQ-011 | US-011 | Member views progress (measurements, history) | Must | Progress | IMPLEMENTING | TESTING | NOT_STARTED | Entries + personal-bests APIs; portal + staff Vue |
| REQ-012 | US-012 | Owner compares branch-level revenue | Should | Reports | IMPLEMENTING | TESTING | NOT_STARTED | `revenue.by_branch` on dashboard JSON + Vue list; zeros included |
| REQ-013 | US-013 | Admin imports existing members via CSV with validation | Must | Data Migration | IMPLEMENTING | TESTING | NOT_STARTED | Preview-then-confirm; Vue `/import` front-desk only |
| REQ-014 | US-014 | Member views payment history / receipts | Must | Member Portal, Payments | IMPLEMENTING | TESTING | NOT_STARTED | Portal + staff member-detail list `GET /payments/`; PDF receipts not built |
| REQ-015 | US-015 | Owner filters/exports expired members | Must | Members, Reports | IMPLEMENTING | TESTING | NOT_STARTED | OWNER `GET /reports/expired-members.csv`; PDF not built |
| REQ-016 | US-016 | Member cancels a class booking; capacity released | Must | Classes | IMPLEMENTING | TESTING | NOT_STARTED | Portal Cancel on BOOKED/WAITLISTED; backend cancel already released capacity |
| REQ-017 | US-017 | Trainer creates/assigns client workout programs | Must | Workouts | IMPLEMENTING | TESTING | NOT_STARTED | `POST /workouts/programs/` STAFF_AND_TRAINER + Vue assign |
| REQ-018 | US-018 | Admin records cash payments as payment records | Must | Billing, Payments | IMPLEMENTING | TESTING | NOT_STARTED | `POST /payments/cash/` + Vue sell-and-collect path |
| REQ-019 | US-019 | Owner configures staff permissions | Could | Authorization | NOT_STARTED | NOT_STARTED | NOT_STARTED | Deferred unless approved |
| REQ-020 | US-020 | Member requests membership freeze (self-service) | Should | Memberships, Member Portal | IMPLEMENTING | TESTING | NOT_STARTED | PENDING request + staff approve/reject; no auto-approve; dates required (OQ-005 arithmetic unchanged) |

### Module / Functional Requirements (PRD §8)

| ID | PRD Ref | Requirement | Priority | Module | Impl | Test | Verified | Notes |
|---|---|---|---|---|---|---|---|---|
| REQ-021 | §8.1 | Member profile stores full identity/contact/fitness/consent fields | Must | Members | IMPLEMENTING | TESTING | NOT_STARTED | Model+API have identity/contact/consent; Vue register collects name/phone/branch/date |
| REQ-022 | §8.1 | Duplicate mobile numbers prevented within same organization | Must | Members | IMPLEMENTING | TESTING | NOT_STARTED | UniqueConstraint (organization, phone); same phone allowed across orgs |
| REQ-023 | §8.1 | Member status auto-derives from membership dates | Must | Members, Memberships | IMPLEMENTING | TESTING | NOT_STARTED | `sync_member_status` after freeze/unfreeze/renew/expire/create; latest membership wins |
| REQ-024 | §8.1 | Freeze history cannot be deleted by normal staff | Must | Memberships | IMPLEMENTING | TESTING | NOT_STARTED | `unfreeze_membership` never deletes freeze rows; no staff delete API |
| REQ-025 | §8.1 | Membership history preserved after renewal | Must | Memberships | IMPLEMENTING | TESTING | NOT_STARTED | `renew_membership` creates a new row; old → EXPIRED |
| REQ-026 | §8.1 | Search by name, mobile, member ID, QR ID | Must | Members | IMPLEMENTING | TESTING | NOT_STARTED | DRF search on name/phone/member_code/email; QR is uuid payload on check-in |
| REQ-027 | §8.2 | Check-in via staff search, QR, and biometric/RFID adapter | Must | Attendance, Integrations | IMPLEMENTING | TESTING | NOT_STARTED | Staff + QR live; `AccessControlAdapter` interface only; vendor = OQ-003 |
| REQ-028 | §8.2 | Check-in eligibility validation (active/branch/blocked/duplicate) | Must | Attendance | IMPLEMENTING | TESTING | NOT_STARTED | Active membership, home/extra branch, soft-delete block, interval duplicate |
| REQ-029 | §8.2 | Every check-in records member, branch, timestamp, method | Must | Attendance | IMPLEMENTING | TESTING | NOT_STARTED | Attendance has member, branch, checkin_at, method, optional device_id |
| REQ-030 | §8.2 | Manual check-in override is audit-logged | Must | Attendance, Audit | IMPLEMENTING | TESTING | NOT_STARTED | Override requires reason + staff; `audit_log` written |
| REQ-031 | §8.3 | Payment methods: cash, UPI, card, online gateway, partial | Must | Payments, Billing | IMPLEMENTING | TESTING | NOT_STARTED | Method enum + cash/UPI/partial/gateway initiate tested; no API |
| REQ-032 | §8.3 | Payment state machine (Pending→...→Refunded/Cancelled) | Must | Payments | IMPLEMENTING | TESTING | NOT_STARTED | Full enum on model; transitions only via `payments.services` |
| REQ-033 | §8.3 | Invoice contains number/GST/member/items/tax/total/status | Must | Billing | IMPLEMENTING | TESTING | NOT_STARTED | `gst_details` JSON snapshot only — OQ-004 still OPEN |
| REQ-034 | §8.3 | Recurring billing: frequency, next date, mandate ID, retries | Must | Billing, Payments | IMPLEMENTING | TESTING | NOT_STARTED | GET `/payments/subscriptions/` visibility only; charge/retry DEFERRED (no invented policy) |
| REQ-035 | §8.3 | Duplicate Razorpay webhook does not duplicate payment effects | Must | Payments | IMPLEMENTING | TESTING | NOT_STARTED | Unique `PaymentEvent.gateway_event_id` + IntegrityError path tested |
| REQ-036 | §8.3 | No raw card credentials are ever stored | Must | Payments | IMPLEMENTING | TESTING | NOT_STARTED | No card-number/CVV fields on any model; HMAC verify unit-tested |
| REQ-037 | §8.3 | Refunds update payment/invoice records via controlled workflow | Must | Payments, Billing | IMPLEMENTING | TESTING | NOT_STARTED | Original Payment.amount never mutated; invoice net-paid recomputed |
| REQ-038 | §8.4 | Class booking cannot exceed configured capacity | Must | Classes | IMPLEMENTING | TESTING | NOT_STARTED | `select_for_update` on occurrence; sequential + threaded last-seat tests |
| REQ-039 | §8.4 | Member cannot book overlapping class sessions | Must | Classes | IMPLEMENTING | TESTING | NOT_STARTED | Shared hold check with PT sessions |
| REQ-040 | §8.4 | Cancellation releases slot; waitlist may promote | Must | Classes | IMPLEMENTING | TESTING | NOT_STARTED | Cancel releases BOOKED slot; auto-promote NOT implemented (OQ / §23.4) |
| REQ-041 | §8.4 | Trainer cannot be assigned conflicting sessions | Must | Classes, Trainers | IMPLEMENTING | TESTING | NOT_STARTED | Checked on class book + PT schedule; occurrence-create write API not yet |
| REQ-042 | §8.5 | PT package tracks purchased/consumed/remaining sessions + expiry | Must | Personal Training | IMPLEMENTING | TESTING | NOT_STARTED | `sessions_remaining` property; CheckConstraint consumed ≤ purchased |
| REQ-043 | §8.5 | PT session state machine (Scheduled/Completed/Cancelled/No-show/Rescheduled) | Must | Personal Training | IMPLEMENTING | TESTING | NOT_STARTED | In-place reschedule keeps SCHEDULED; overlap + COMPLETED rejection tested |
| REQ-044 | §8.5 | Completed session decrements package balance exactly once | Must | Personal Training | IMPLEMENTING | TESTING | NOT_STARTED | `select_for_update` on package; sequential + threaded double-complete tests |
| REQ-045 | §8.5 | Cancelled session does not decrement balance unless gym policy overrides | Must | Personal Training | IMPLEMENTING | TESTING | NOT_STARTED | Cancel default = no consume; gym-policy override still OQ |
| REQ-046 | §8.6 | Staff records: name/mobile/email/role/branch/status | Must | Trainers, Accounts | IMPLEMENTING | TESTING | NOT_STARTED | OWNER create/activate/deactivate; Vue `/staff` |
| REQ-047 | §8.6 | Trainer compensation models (fixed/per-session/per-class/%) | Must | Trainers | IMPLEMENTING | TESTING | NOT_STARTED | Read-only calc; REVENUE_SHARE amount is None (base undefined); no payroll |
| REQ-048 | §8.7 | Lead pipeline (New→Contacted→...→Converted/Lost) | Should | CRM / Leads | IMPLEMENTING | TESTING | NOT_STARTED | Convert creates Member; Vue `/leads`; no marketing automation |
| REQ-049 | §8.8 | Owner dashboard: revenue/membership/attendance/PT metrics | Must | Dashboard | IMPLEMENTING | TESTING | NOT_STARTED | `GET /reports/dashboard/` derives from Payment/Invoice/Membership/Attendance/PT |
| REQ-050 | §8.8 | Reports export as CSV/PDF where appropriate | Must | Reports | IMPLEMENTING | TESTING | NOT_STARTED | OWNER `GET /reports/dashboard.csv`; PDF not built |
| REQ-051 | §8.9 | Mandatory transactional notification events (11 events) | Must | Notifications | IMPLEMENTING | TESTING | NOT_STARTED | All 11 event types have an in-app path (hooks or scans). Vendors OQ-001/002 |
| REQ-052 | §8.9 | Notification channel/provider abstraction | Must | Notifications, Integrations | IMPLEMENTING | TESTING | NOT_STARTED | `NotificationProvider` + `ConsoleNotificationProvider` (DEC-022); no vendor HTTP |
| REQ-053 | §8.10 | Branch A data never appears in Branch B staff views without authorization | Must | Branches, Authorization | IMPLEMENTING | TESTING | NOT_STARTED | Staff querysets use `authorized_branch_ids`; isolation tests exist per domain |
| REQ-054 | §8.10 | Owner can view/switch/compare across all branches | Must | Branches, Dashboard | IMPLEMENTING | TESTING | NOT_STARTED | Owner dashboard `revenue.by_branch`; no separate branch-switcher UI |
| REQ-055 | §8.11 | Member self-service: membership/payments/classes/attendance/PT/workout/progress | Must | Member Portal | IMPLEMENTING | TESTING | NOT_STARTED | `/portal` includes freeze-request, cancel booking, pay initiate, payments list |
| REQ-056 | §8.12 | Workout program structure: Program→Day→Exercise→Sets/Reps/Weight/Rest/Notes | Must | Workouts | IMPLEMENTING | TESTING | NOT_STARTED | Nested program/day/exercise + logs; no AI coaching |
| REQ-057 | §8.12 | Progress tracking: weight/BMI/measurements/PRs/photos | Must | Progress | IMPLEMENTING | TESTING | NOT_STARTED | BMI when weight+height; photo_url string only; no AI |

### Non-Functional / Architectural Requirements (PRD §9–§10)

| ID | PRD Ref | Requirement | Priority | Module | Impl | Test | Verified | Notes |
|---|---|---|---|---|---|---|---|---|
| REQ-058 | §9.1 | Performance targets: API p95<500ms, dashboard p95<1.5s, check-in<2s, search<500ms | Must | Production/Operations | NOT_STARTED | NOT_STARTED | NOT_STARTED | |
| REQ-059 | §9.2 | Multi-tenant scalability (100–500 members/branch → 10,000+ gyms future) | Must | Organizations | NOT_STARTED | NOT_STARTED | NOT_STARTED | No fundamental rewrite required |
| REQ-060 | §9.3 | Security baseline: HTTPS, hashing, RBAC, tenant isolation, CSRF/XSS/SQLi, secrets, encryption | Must | Authorization, Accounts/Auth | IMPLEMENTING | TESTING | NOT_STARTED | Login ScopedRateThrottle 5/min; full HTTPS/AWS hardening not started |
| REQ-061 | §9.4 | No raw card data stored; delegated to gateway | Must | Payments | IMPLEMENTING | TESTING | NOT_STARTED | Same evidence as REQ-036 |
| REQ-062 | §9.5 | Consent, purpose limitation, data access/deletion (DPDP-aligned) | Must | Accounts/Auth, Members | NOT_STARTED | NOT_STARTED | NOT_STARTED | Exact legal treatment = open, needs legal review |
| REQ-063 | §9.6 | 99.9% monthly availability; health checks, backups, monitoring, alerting | Must | Production/Operations | IMPLEMENTING | TESTING | NOT_STARTED | Local `/healthz/` + `/readyz/` (DB+Redis); backups/alerting/AWS not started |
| REQ-064 | §9.7 | Daily full backup, PITR where supported, ≥30 day retention, monthly restore test | Must | Production/Operations | NOT_STARTED | NOT_STARTED | NOT_STARTED | |
| REQ-065 | §9.8 | Localization: INR, IST, Indian date/mobile formats, GST-ready, English UI | Must | Billing, Accounts/Auth | NOT_STARTED | NOT_STARTED | NOT_STARTED | |
| REQ-066 | §10.3 | Every business record traceable to organization/tenant; tenant isolation enforced in every query | Must | Organizations, Authorization | IMPLEMENTING | TESTING | NOT_STARTED | TenantScopedModel + `for_organization`/`for_user`; 17 `test_tenant_isolation.py` files |
| REQ-067 | §10.3/§13.1 | Payment provider abstraction (PaymentService → PaymentProvider → RazorpayProvider) | Must | Payments, Integrations | IMPLEMENTING | TESTING | NOT_STARTED | Interface + RazorpayProvider + FakePaymentProvider; real HTTPS order/refund NOT EXECUTED |
| REQ-068 | §8.2/§13.1 | Biometric/RFID access-control adapter interface (vendor-agnostic) | Should | Integrations, Attendance | IMPLEMENTING | TESTING | NOT_STARTED | `attendance/adapters.py` Protocol + Fake parse_event; no vendor HTTP (OQ-003) |
| REQ-069 | §12/§13.1 | CSV/Excel migration: validate → preview → confirm → import → report | Must | Data Migration | IMPLEMENTING | TESTING | NOT_STARTED | Members CSV only; never inserts unvalidated rows; Excel upload not built |

### Traceability Rule

Every implementation task must cite the requirement ID(s) it addresses. New
requirements discovered during implementation must be appended with the next
unused `REQ-XXX` ID — never inserted out of sequence and never reusing a
retired ID.

---

# 10. Functional Module Baseline

## 10.1 Member Management

### Required Capabilities

- member database
- identity data
- contact data
- profile photo
- DOB
- gender
- address
- emergency contact
- joining date
- branch
- trainer
- membership status
- medical/fitness notes
- consent status
- current membership
- historical memberships
- membership plan
- payment status
- freeze history
- renewal history

### Search

Must support:

- name
- mobile
- member ID
- QR ID

### Acceptance Criteria

- Duplicate mobile numbers are prevented within the same gym.
- Member status changes according to membership dates.
- Normal staff cannot delete freeze history.
- Membership history remains after renewal.
- Search returns required identifiers.

Status: NOT_STARTED

---

# 11. Membership Domain Baseline

Required:

- membership plans
- current membership
- historical membership
- price
- discount
- payment status
- freeze
- renewal
- status

Freeze must capture:

- reason
- start date
- end date
- notes
- history

The system must recalculate revised expiry according to the configured freeze policy.

Membership lifecycle is a high-risk domain and requires service-level business rules, transactions where necessary, authorization, and tests.

Status: NOT_STARTED

---

# 12. Attendance Domain Baseline

Check-in methods:

1. staff search
2. QR
3. biometric/RFID adapter

Eligibility must validate:

- active membership
- allowed branch
- account status
- duplicate check-in rules

Attendance must record:

- member
- branch
- timestamp
- method

Manual override requires audit logging.

Performance requirements:

- QR/check-in experience ≤10 seconds under normal conditions
- backend check-in processing target <2 seconds

Status: NOT_STARTED

---

# 13. Billing and Payments Baseline

Supported payment concepts:

- one-time
- recurring
- installments
- discounts
- taxes
- partial payments
- cash
- UPI
- card
- online gateway

Payment states:

```text
Pending
Initiated
Successful
Failed
Refunded
Partially Refunded
Cancelled
```

Invoices must contain:

- invoice number
- gym details
- GST details where applicable
- member
- items
- discount
- tax
- total
- payment method
- payment status
- date

Recurring billing must support:

- billing frequency
- start date
- next billing date
- mandate/subscription ID
- retries
- failed-payment status

Critical invariants:

- successful payment updates payment/membership state
- duplicate webhook events must not create duplicate payments
- failed payments are visible
- member payment confirmation is sent
- refunds update financial records
- raw card credentials are never stored
- payment records are not casually mutated/deleted

Initial provider:

```text
Razorpay
```

Payment provider abstraction is required for future providers.

Status: NOT_STARTED

---

# 14. Classes and Scheduling Baseline

Required:

- group classes
- PT
- trainer calendars
- recurring classes
- one-off sessions
- capacity
- waitlists
- booking
- cancellation
- no-show tracking

Class fields include:

- name
- branch
- trainer
- room
- capacity
- start time
- end time
- booking policy

Rules:

- capacity cannot be exceeded
- member cannot book overlapping sessions
- cancellation releases a slot
- waitlist can promote members
- trainers cannot have conflicting sessions
- class attendance links to booking

Capacity and booking are concurrency-sensitive.

Status: NOT_STARTED

---

# 15. Personal Training Baseline

PT package examples:

- 5 sessions
- 10 sessions
- 20 sessions
- monthly unlimited

Track:

- package price
- purchased sessions
- consumed sessions
- remaining sessions
- expiry
- trainer

PT session states:

```text
Scheduled
Completed
Cancelled
No-show
Rescheduled
```

Required rules:

- completed session decrements package balance
- cancellation does not decrement unless gym policy specifies otherwise
- trainer access is limited to assigned sessions
- owner can view all
- member can view remaining sessions

PT consumption is concurrency-sensitive.

Status: NOT_STARTED

---

# 16. Staff and Trainer Baseline

Staff fields:

- name
- mobile
- email
- role
- branch
- joining date
- employment status

Trainer fields:

- specialization
- certifications
- assigned members
- classes
- PT sessions
- compensation model

V1 compensation concepts:

- fixed salary
- per-session
- per-class
- revenue percentage

Payroll disbursement is out of scope.

Status: NOT_STARTED

---

# 17. CRM / Leads Baseline

CRM is **Should** priority.

Lead data and pipeline are defined in the PRD.

This area should not displace core MVP operational workflows unless priority is explicitly changed.

Status: NOT_STARTED

---

# 18. Dashboard and Reporting Baseline

## Owner Revenue

- today's collection
- monthly collection
- pending dues
- refunds
- branch revenue
- membership-plan revenue

## Membership

- active
- expired
- expiring within 7 days
- expiring within 30 days
- new
- cancelled
- frozen

## Attendance

- today's check-ins
- daily trend
- monthly trend
- average visits/member
- peak hours

## PT

- sessions
- completed sessions
- remaining package sessions
- PT revenue

Reports should support CSV/PDF export where appropriate.

Status: NOT_STARTED

---

# 19. Notifications Baseline

Channels:

- WhatsApp
- SMS
- Email
- In-app

Mandatory transactional events:

| Event | Notification |
|---|---|
| Membership created | Welcome |
| Payment successful | Receipt |
| Payment failed | Failure |
| Membership expiring | Reminder |
| Membership expired | Expiry |
| Class booking | Confirmation |
| Class reminder | Reminder |
| PT booking | Confirmation |
| PT reminder | Reminder |
| Birthday | Birthday message |
| Freeze approved | Confirmation |

WhatsApp requires an approved Business API provider.

Provider selection is currently unresolved.

Status: NOT_STARTED

---

# 20. Multi-Branch Baseline

Each branch has:

- name
- address
- contact
- operating hours
- staff
- trainers
- members
- classes
- revenue
- attendance

Owner:

- all branches
- branch switching
- comparison
- consolidated reporting

Staff:

- assigned branch by default

Trainer:

- assigned branch

Member:

- home branch
- potentially allowed additional branches depending on membership

Core security invariant:

```text
Branch A data
must not
appear in Branch B staff views
without authorization.
```

Status: NOT_STARTED

---

# 21. Member Portal Baseline

Member home should display:

- membership status
- expiry
- QR code
- upcoming class
- upcoming PT
- outstanding balance
- recent attendance

Member capabilities:

### Membership

- view plan
- view expiry
- request freeze
- renew
- history

### Payments

- pay dues
- invoices
- payment history

### Classes

- browse
- book
- cancel
- waitlist
- bookings

### Attendance

- history
- visit frequency

### PT

- trainer
- sessions
- book PT

### Workout

- assigned plan
- log workout
- sets/reps/weight

### Progress

- weight
- body measurements
- photos
- personal bests

Status: NOT_STARTED

---

# 22. Workout and Progress Baseline

Workout structure:

```text
Program
 └── Day
      └── Exercise
           ├── Sets
           ├── Reps
           ├── Weight
           ├── Rest
           └── Notes
```

Exercise library can contain:

- name
- muscle group
- equipment
- instructions
- video/image reference

Member logging:

- sets
- reps
- weight
- duration
- notes

Progress:

- body weight
- BMI where applicable
- measurements
- strength PRs
- workout completion
- progress photos

Advanced AI coaching is out of scope for V1.

Status: NOT_STARTED

---

# 23. Data Migration Baseline

Initial migration requirement:

```text
CSV / Excel
    ↓
Validation
    ↓
Preview
    ↓
Duplicate detection
    ↓
Mapping
    ↓
Confirmation
    ↓
Import
    ↓
Import report
```

The PRD explicitly warns about:

- duplicate members
- missing phone numbers
- invalid dates
- duplicate payments
- inconsistent membership status

Uploaded data must not be inserted directly into production tables without validation/preview.

Status: NOT_STARTED

---

# 24. Non-Functional Requirements

## 24.1 Performance Targets

| Metric | Target |
|---|---:|
| Standard API p95 | <500ms |
| Dashboard API p95 | <1.5s |
| Check-in backend | <2s |
| Initial page load | <3s |
| Search response | <500ms |
| Large report generation | Asynchronous |

## 24.2 Scalability

Initial target:

- multi-tenant SaaS
- multiple gyms
- multiple branches/gym
- 100–500 members/location

Future architectural target:

- 10,000+ gyms
- millions of member records
- without a fundamental rewrite

## 24.3 Availability

Target:

```text
99.9% monthly availability
```

## 24.4 Backup

Required:

- daily full DB backup
- point-in-time recovery where supported
- ≥30-day retention
- monthly restore test

## 24.5 Localization

V1:

- INR
- Indian date/time formats
- IST
- Indian mobile numbers
- GST-ready invoices
- English UI

Future regional languages are Phase 2+.

---

# 25. Security Baseline

Required controls:

- HTTPS
- password hashing
- secure session/token management
- role-based authorization
- tenant isolation
- branch-level authorization
- audit logging
- rate limiting
- CSRF protection
- XSS prevention
- SQL injection prevention
- secure upload validation
- secrets outside source code
- encryption at rest where appropriate
- encryption in transit

## 25.1 Payment Security

Raw card details must never be stored.

## 25.2 Personal Data

The application handles:

- names
- phone numbers
- email
- addresses
- fitness information
- payment information
- attendance history

Implementation must support appropriate consent, purpose limitation, data access/deletion workflows and security controls applicable to India's Digital Personal Data Protection framework.

## 25.3 Audit-Critical Operations

At minimum, sensitive operations should be considered for audit logging:

- manual attendance overrides
- membership freeze
- payment correction/refund
- staff status changes
- authorization-sensitive changes
- financial state changes
- data import
- other security-sensitive actions

Exact audit coverage can be expanded during architecture implementation.

---

# 26. Technical Architecture Baseline

The PRD's high-level architecture is:

```text
                    ┌─────────────────────┐
                    │     Vue Frontend    │
                    │ Web / Responsive UI │
                    └──────────┬──────────┘
                               │
                              HTTPS
                               │
                    ┌──────────▼──────────┐
                    │    Django Backend   │
                    │ REST API / Auth     │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼──────────────────┐
             │                 │                  │
      ┌──────▼──────┐  ┌──────▼──────┐   ┌──────▼──────┐
      │    MySQL    │  │    Redis    │   │ Background  │
      │             │  │             │   │   Workers   │
      └─────────────┘  └─────────────┘   └──────┬──────┘
                                                 │
                         ┌───────────────────────┼────────────┐
                         │                       │            │
                   ┌─────▼─────┐          ┌──────▼─────┐ ┌──▼───┐
                   │ Razorpay  │          │ WhatsApp/  │ │Email │
                   │           │          │ SMS        │ │      │
                   └───────────┘          └────────────┘ └──────┘
```

## 26.1 Suggested Django Domains (PRD baseline)

The PRD suggests:

```text
accounts
tenants
branches
members
memberships
attendance
payments
billing
classes
pt
trainers
workouts
progress
notifications
reports
crm
audit
integrations
```

These are architectural starting points, not a license to create unnecessary abstractions or apps.

## 26.1.1 Approved Django Application List (GYM-003 / DEC-007)

The PRD list above is finalized into 20 concrete Django apps. Reasoning for
each deviation from the raw PRD list is captured in `DEC-007` (§28). No app
is created merely because DRF makes CRUD "easy" — each has a distinct
domain/data-ownership reason.

| App | Purpose | Notes vs PRD list |
|---|---|---|
| `core` | Shared abstract base models (`TenantScopedModel`, `TimestampedModel`, `SoftDeleteModel`), tenant-scoping queryset/manager mixins, custom exceptions, shared validators | New — not a business module; pure technical foundation (§69 "no hidden business logic" requires this to be a visible, reusable primitive, not copy-pasted per app) |
| `accounts` | `User` model (custom, `AbstractBaseUser`), roles, login/logout, JWT issuance, password reset, invitations | Matches PRD `accounts` |
| `organizations` | `Organization` model, org-level settings (freeze policy defaults, GST details, billing config) | Renamed from PRD `tenants` for clarity; "tenant" is the *concept*, `Organization` is the *model* |
| `branches` | `Branch` model, staff/trainer/member branch-access grants | Matches PRD `branches` |
| `members` | `Member` profile, consent, emergency contact, medical notes | Matches PRD `members` |
| `memberships` | `MembershipPlan`, `Membership`, `MembershipFreeze`, renewal history | Matches PRD `memberships` |
| `attendance` | `Attendance`, QR-token issuance, biometric adapter interface | Matches PRD `attendance` |
| `billing` | `Invoice`, `InvoiceLineItem` | Split from PRD `payments`/`billing` combined idea — invoices are billing documents, distinct lifecycle from payment settlement |
| `payments` | `Payment`, `Refund`, `Subscription` (recurring/mandate), `PaymentProvider` interface, `RazorpayProvider` | Matches PRD `payments`; billing/payments kept as two apps because an invoice can have multiple payment attempts and partial payments (§21.1) |
| `classes` | `GymClass`, `ClassOccurrence`, `Booking`, `Waitlist` | Matches PRD `classes` |
| `pt` | `PTPackage`, `PTSession` | Matches PRD `pt` |
| `trainers` | Trainer-specific profile extension (specializations, certifications, compensation config) | Matches PRD `trainers`; staff/trainer *accounts* live in `accounts`, trainer-specific *domain* data lives here |
| `workouts` | `Exercise` (library), `WorkoutProgram`, `WorkoutDay`, `WorkoutDayExercise`, `WorkoutLog` | Matches PRD `workouts` |
| `progress` | `ProgressEntry` (weight/measurements/photos/PRs) | Matches PRD `progress` |
| `notifications` | `NotificationTemplate`, `NotificationLog`, provider adapter interface | Matches PRD `notifications` |
| `reports` | Aggregation/read endpoints only (dashboard + reports); no independent financial calculation | Combines PRD `reports` + the "Owner Dashboard" concept — §30 forbids a second shadow financial calculation path, so dashboard cards and reports share one aggregation layer over `billing`/`payments`/`memberships`/`attendance` |
| `crm` | `Lead`, `LeadActivity` | Matches PRD `crm`; **Should** priority — must not consume MVP schedule |
| `migration` | `ImportJob`, `ImportRowError` | New — PRD §12/§31 requires upload→validate→preview→confirm→import→report; needs its own auditable model, not ad-hoc scripts |
| `audit` | `AuditLog` (generic, append-only) | Matches PRD `audit` |
| `integrations` | Abstract provider interfaces (`PaymentProvider`, `NotificationProvider`, `BiometricAdapter`) + per-organization credential storage | Matches PRD `integrations`; concrete implementations (e.g. `RazorpayProvider`) live inside the owning domain app (`payments`), the interface/contract lives here |

**Explicitly not separate apps** (and why):

- **Member Portal** — not a backend app. Per `AGENTS.md` §27, member self-service must reuse the same `members`/`memberships`/`payments`/`classes`/`pt`/`workouts`/`progress` service logic as staff flows, exposed through member-scoped permissions on the same endpoints. A separate app would risk duplicating business rules.
- **Dashboard** — folded into `reports` for the same "no shadow calculation path" reason (§30).
- **Staff** (as distinct from `trainers`) — staff accounts are `accounts.User` records with `role=STAFF_ADMIN`; no separate `staff` app is needed since there is no staff-specific domain data beyond the `User`/`Branch` relationship already modeled.

## 26.2 Multi-Tenant Baseline

Conceptual structure:

```text
Platform
  └── Gym Organization
        ├── Branch A
        │    ├── Staff
        │    ├── Members
        │    └── Classes
        │
        └── Branch B
             ├── Staff
             ├── Members
             └── Classes
```

Core authorization path:

```text
User
  ↓
Organization
  ↓
Branch
  ↓
Resource
```

Every business record should have an organization/tenant association as required by the design.

**Exact implementation strategy is now decided — see `DEC-008` (multi-tenancy
enforcement) and `DEC-009` (branch access model) in §28.**

---

# 27. Core Data Model Baseline

The PRD defines these core entities:

## Organization

```text
id
name
status
created_at
```

## Branch

```text
id
organization_id
name
address
phone
timezone
status
```

## User

```text
id
organization_id
branch_id
role
name
email
phone
password_hash
status
```

## Member

```text
id
organization_id
home_branch_id
member_code
name
phone
email
dob
gender
joining_date
status
```

## MembershipPlan

```text
id
organization_id
name
duration
price
billing_frequency
freeze_allowed
status
```

## Membership

```text
id
member_id
plan_id
start_date
end_date
status
freeze_days
price
discount
```

## Subscription

```text
id
member_id
membership_id
gateway
gateway_subscription_id
status
next_billing_date
```

## Payment

```text
id
member_id
invoice_id
amount
method
gateway
gateway_transaction_id
status
paid_at
```

## Attendance

```text
id
member_id
branch_id
checkin_at
checkout_at
method
device_id
```

## Class

```text
id
branch_id
name
trainer_id
capacity
start_time
end_time
recurrence
```

## Booking

```text
id
class_id
member_id
status
booked_at
cancelled_at
```

## PTPackage

```text
id
member_id
trainer_id
sessions_purchased
sessions_used
expiry_date
```

## PTSession

```text
id
package_id
member_id
trainer_id
scheduled_at
status
notes
```

## WorkoutProgram

```text
id
member_id
trainer_id
name
start_date
end_date
status
```

## WorkoutLog

```text
id
member_id
program_id
exercise_id
date
sets
reps
weight
notes
```

### Data Model Status (as of GYM-002)

**PRD baseline captured.**

**Django implementation: NOT_STARTED.**

The final data model must be reviewed for missing relationships, lifecycle requirements, auditability, constraints, indexing, financial history, concurrency and migration compatibility before models are created.

---

## 27.A Approved Data Model Design (GYM-003)

**Status: DESIGNED.** This is a schema-level design (field lists, relationships,
constraints, indexes) recorded for review and future implementation. **No
`models.py` code or migrations have been written — that is scaffolding, out
of scope for this architecture task.** Money fields are `Decimal` everywhere
(never float), per `AGENTS.md` §15.4 / §90.11. Every tenant-owned model
inherits `core.TenantScopedModel` (see `DEC-008`).

### `core` (shared abstractions — no business table)

- `TimestampedModel` (abstract): `created_at`, `updated_at`.
- `TenantScopedModel` (abstract, extends `TimestampedModel`): `organization` (FK, indexed, required), `uuid` (indexed unique `UUIDField`, external identifier — see `DEC-012`). Provides a default manager that **requires** an explicit organization filter context (raises if used unscoped outside an internal/admin context) — see `DEC-008`.
- `SoftDeleteModel` (abstract, mixin, opt-in per model): `is_deleted`, `deleted_at`. Used only where "soft delete" is the correct business behavior (e.g. `Member`), never for financial rows (which use state transitions, not deletion — §21.7/§34.4).

### `accounts`

- **`User`** (extends `AbstractBaseUser` + `PermissionsMixin`, tenant-scoped): `organization` FK, `uuid`, `email` (unique per organization), `phone`, `full_name`, `role` (`OWNER` / `STAFF_ADMIN` / `TRAINER` / `MEMBER`, choices), `is_active`, `date_joined`, `last_login`. **Indexes:** `(organization, email)` unique, `(organization, role)`.
  - Note: `MEMBER`-role users link 1:1 to a `members.Member` record (a `Member` can exist without portal login access until invited; a `User` with role `MEMBER` always has exactly one `Member`).
- **`RefreshToken`** (if session-store-backed rotation is used instead of pure stateless JWT blacklist — see `DEC-010`): `user` FK, `token_hash`, `issued_at`, `expires_at`, `revoked_at`, `replaced_by` (self FK, nullable). **Indexes:** `token_hash` unique, `(user, revoked_at)`.
- **`PasswordResetToken`**: `user` FK, `token_hash`, `expires_at`, `used_at`.

### `organizations`

- **`Organization`**: `uuid`, `name`, `legal_name`, `gstin` (nullable), `status` (`ACTIVE`/`SUSPENDED`), `default_timezone` (default `Asia/Kolkata`), `default_currency` (default `INR`), `freeze_policy` (choices: `EXTEND_BY_FREEZE_DAYS` / `PAUSE_NO_EXTEND` / other — **default/allowed policy set is OQ-005, still open**; schema stores the *choice*, not the *decision of what the default should be*), `created_at`.
- **`OrganizationSettings`** (1:1, optional split to avoid a bloated `Organization` row): billing/notification defaults, invoice numbering sequence config.

### `branches`

- **`Branch`** (tenant-scoped): `organization` FK, `uuid`, `name`, `address`, `phone`, `timezone`, `operating_hours` (JSON or related table), `status` (`ACTIVE`/`INACTIVE`). **Indexes:** `(organization, status)`.
- **`BranchAccess`** (grants non-home branch access — implements PRD §8.10/§16.3): `user` FK (nullable — staff/trainer grants) OR `member` FK (nullable — member multi-branch grants; exactly one of `user`/`member` set, enforced via `CheckConstraint`), `branch` FK, `granted_at`, `granted_by` FK(`accounts.User`). **Constraint:** unique `(user, branch)` and unique `(member, branch)`.
  - `OWNER` role users implicitly have all branches in their organization — no `BranchAccess` rows needed for owners (checked via role, not rows, to avoid N rows per branch per owner).
  - `STAFF_ADMIN`/`TRAINER` have exactly one **home branch** (`accounts.User.home_branch` FK, added below) plus zero-or-more `BranchAccess` grants for additional branches.
  - `Member.home_branch` FK (in `members.Member`) plus zero-or-more `BranchAccess` grants when the membership plan permits cross-branch access (PRD §8.10 "Member... Allowed branches if configured").

  *(Correction to `accounts.User` above: add `home_branch` FK, nullable — null only for `OWNER` role.)*

### `members`

- **`Member`** (tenant-scoped, soft-delete): `organization` FK, `uuid`, `user` FK (nullable — a member may exist before portal login is provisioned), `member_code` (human-friendly, unique per organization, e.g. `GYM-000123`), `home_branch` FK, `assigned_trainer` FK(`accounts.User`, nullable), `full_name`, `phone`, `email` (nullable), `dob`, `gender`, `address`, `emergency_contact_name`, `emergency_contact_phone`, `photo` (S3-backed `ImageField`), `medical_notes` (text, encrypted-at-rest consideration flagged), `consent_status` (choices), `joining_date`, `status` (`ACTIVE`/`INACTIVE`/derived — see below). **Indexes:** `(organization, phone)` unique (duplicate-mobile prevention, REQ-022), `(organization, member_code)` unique, `(organization, status)`.
  - `status` is **derived**, not hand-edited: a service recomputes it from the current `Membership` state (REQ-023) — no independent source of truth duplicated on `Member`.

### `memberships`

- **`MembershipPlan`** (tenant-scoped): `organization` FK, `uuid`, `name`, `duration_days`, `price` (Decimal), `billing_frequency` (`ONE_TIME`/`MONTHLY`/`QUARTERLY`/...), `freeze_allowed` (bool), `max_freeze_days` (nullable int), `status` (`ACTIVE`/`ARCHIVED`).
- **`Membership`** (tenant-scoped via `member.organization`): `member` FK, `plan` FK, `start_date`, `end_date`, `status` (`ACTIVE`/`FROZEN`/`EXPIRED`/`CANCELLED` — §19.2, no unsupported states without justification), `price` (Decimal, snapshot at sale — price changes on the plan must not retroactively alter sold memberships), `discount` (Decimal), `created_by` FK(`accounts.User`). **Indexes:** `(member, status)`, `(end_date)` (for expiry-scan jobs).
  - Renewal creates a **new** `Membership` row referencing the same `member`; it never mutates/deletes the prior row (§19.3/§59.3).
- **`MembershipFreeze`**: `membership` FK, `start_date`, `end_date`, `reason`, `notes`, `requested_by` FK, `approved_by` FK (nullable), `revised_end_date` (computed result, stored for audit), `created_at`. **No hard delete** by normal staff — enforced at the permission layer, not just the UI (§19.1/§59.4).

### `attendance`

- **`Attendance`** (tenant-scoped via `member.organization`): `member` FK, `branch` FK, `checkin_at`, `checkout_at` (nullable), `method` (`STAFF_SEARCH`/`QR`/`BIOMETRIC`/`MANUAL_OVERRIDE`), `device_id` (nullable), `recorded_by` FK(`accounts.User`, nullable — null for self-service QR), `override_reason` (nullable, required when `method=MANUAL_OVERRIDE`). **Indexes:** `(member, checkin_at)`, `(branch, checkin_at)` (dashboard/trend queries).
- **`QRToken`**: `member` FK (1:1 or rotating tokens), `token` (opaque, indexed unique), `issued_at`, `expires_at` (rotation policy TBD at implementation time — not a schema blocker).

### `billing`

- **`Invoice`** (tenant-scoped via `member.organization`): `member` FK, `uuid`, `invoice_number` (unique per organization, sequential per `OrganizationSettings` numbering config), `issue_date`, `subtotal`/`discount`/`tax`/`total` (all Decimal), `gst_details` (JSON snapshot — exact fields = OQ-004, schema keeps it flexible pending finance/legal confirmation), `status` (`DRAFT`/`ISSUED`/`PAID`/`PARTIALLY_PAID`/`VOID`), `created_by` FK.
- **`InvoiceLineItem`**: `invoice` FK, `description`, `quantity`, `unit_price` (Decimal), `tax_rate` (Decimal), `line_total` (Decimal), `related_membership` FK (nullable), `related_pt_package` FK (nullable).

### `payments`

- **`Payment`** (tenant-scoped via `invoice.member.organization`): `invoice` FK, `uuid`, `amount` (Decimal), `method` (`CASH`/`UPI`/`CARD`/`GATEWAY`), `gateway` (nullable, e.g. `RAZORPAY`), `gateway_payment_id` (nullable, indexed), `gateway_order_id` (nullable, indexed), `status` (`PENDING`/`INITIATED`/`SUCCESSFUL`/`FAILED`/`REFUNDED`/`PARTIALLY_REFUNDED`/`CANCELLED` — full PRD state set, §21.2/§59.5-6, never collapsed), `paid_at` (nullable), `recorded_by` FK (nullable — null for gateway-initiated), `idempotency_key` (indexed unique, nullable — client/webhook-supplied dedup key). **Never mutated** to a terminal state without a corresponding `PaymentEvent`/`Refund` row (immutability — §21.7/§34.4).
- **`PaymentEvent`** (append-only ledger of state transitions, esp. webhook deliveries): `payment` FK, `event_type`, `gateway_event_id` (**indexed unique** — this is the primary idempotency guard for duplicate webhooks, REQ-035/§59.5), `raw_payload` (JSON, secrets redacted), `received_at`, `processed_at` (nullable).
- **`Refund`**: `payment` FK, `amount` (Decimal), `reason`, `status` (`PENDING`/`PROCESSED`/`FAILED`), `gateway_refund_id` (nullable), `initiated_by` FK, `processed_at` (nullable).
- **`Subscription`** (recurring billing / mandate): `member` FK, `membership_plan` FK, `gateway`, `gateway_subscription_id` (indexed), `status`, `next_billing_date`, `retry_count`.

### `classes`

- **`GymClass`** (tenant-scoped via `branch.organization`): `branch` FK, `name`, `trainer` FK(`accounts.User`), `room`, `capacity` (positive int, DB `CheckConstraint > 0`), `recurrence_rule` (RFC5545-style or simplified JSON), `booking_policy` (JSON — cancellation cutoff, etc.), `status`.
- **`ClassOccurrence`** (one concrete bookable session, materialized from recurrence): `gym_class` FK, `start_time`, `end_time`, `capacity_override` (nullable), `status` (`SCHEDULED`/`CANCELLED`). **Indexes:** `(gym_class, start_time)`, `(trainer via gym_class, start_time)` for trainer-conflict queries.
- **`Booking`**: `occurrence` FK, `member` FK, `status` (`BOOKED`/`WAITLISTED`/`CANCELLED`/`ATTENDED`/`NO_SHOW`), `booked_at`, `cancelled_at` (nullable). **Constraint:** unique `(occurrence, member)` where `status != CANCELLED` (prevents double-booking); capacity enforcement is a transactional service-layer check (`SELECT ... FOR UPDATE` / `select_for_update()`) at booking time, not just this constraint — see `DEC concurrency notes` under §59.7 (capacity is a race condition boundary, requires row locking or an atomic counter, not merely a `COUNT(*)` check-then-insert).

### `pt`

- **`PTPackage`** (tenant-scoped via `member.organization`): `member` FK, `trainer` FK, `plan_name` (e.g. "10 sessions"), `sessions_purchased` (int), `sessions_consumed` (int, **DB `CheckConstraint`: `sessions_consumed <= sessions_purchased`**), `price` (Decimal), `expiry_date`.
- **`PTSession`**: `package` FK, `member` FK (denormalized for query convenience, must always match `package.member`), `trainer` FK, `scheduled_at`, `duration_minutes`, `status` (`SCHEDULED`/`COMPLETED`/`CANCELLED`/`NO_SHOW`/`RESCHEDULED`), `notes`, `linked_workout_log` FK (nullable). Consumption of `sessions_consumed` happens via `select_for_update()` on `PTPackage` inside the same transaction that marks a session `COMPLETED` — never a separate step (§24.2/§59.10).

### `trainers`

- **`TrainerProfile`** (1:1 with `accounts.User` where `role=TRAINER`): `specializations` (M2M or JSON list), `certifications` (JSON/related table), `compensation_model` (`FIXED_SALARY`/`PER_SESSION`/`PER_CLASS`/`REVENUE_SHARE`), `compensation_rate` (Decimal), `bio`.

### `workouts`

- **`Exercise`** (organization-scoped library, or global + org override — decided as organization-scoped for V1 simplicity): `name`, `muscle_group`, `equipment`, `instructions`, `media_url`.
- **`WorkoutProgram`**: `member` FK, `trainer` FK, `name`, `start_date`, `end_date` (nullable), `status`.
- **`WorkoutDay`**: `program` FK, `day_index`/`label`.
- **`WorkoutDayExercise`** (planned prescription): `workout_day` FK, `exercise` FK, `target_sets`, `target_reps`, `target_weight` (nullable), `rest_seconds`, `notes`, `order`.
- **`WorkoutLog`** (actual member-logged performance): `member` FK, `workout_day_exercise` FK (nullable — logs can exist ad hoc, not only against a prescribed plan), `exercise` FK, `date`, `sets`, `reps`, `weight` (Decimal), `duration_seconds` (nullable), `notes`.

### `progress`

- **`ProgressEntry`**: `member` FK, `recorded_at`, `weight_kg` (Decimal, nullable), `body_fat_pct` (nullable), `measurements` (JSON: chest/waist/hips/arms/etc., nullable), `photo` (S3 `ImageField`, nullable), `notes`.
- **`PersonalBest`**: `member` FK, `exercise` FK, `value` (Decimal), `unit`, `achieved_at`.

### `notifications`

- **`NotificationTemplate`** (org-scoped, per event type + channel): `organization` FK, `event_type` (choices matching PRD §8.9 table), `channel` (`WHATSAPP`/`SMS`/`EMAIL`/`IN_APP`), `template_body`.
- **`NotificationLog`**: `organization` FK, `recipient_user`/`recipient_member` FK, `event_type`, `channel`, `status` (`PENDING`/`SENT`/`FAILED`/`DELIVERED` where the provider reports it), `provider_message_id` (nullable), `sent_at`, `error_detail` (nullable) — satisfies §29.3 "preserve enough state to diagnose whether generated/attempted/succeeded/failed."

### `reports`

- No independent business tables. Optionally a `SavedReportConfig` (org-scoped: name, filters, schedule) if scheduled report delivery is implemented. All figures are computed via read-only aggregation queries/services over `billing`/`payments`/`memberships`/`attendance`/`pt` — never a duplicated ledger.

### `crm`

- **`Lead`** (tenant-scoped): `branch` FK, `name`, `phone`, `source`, `interested_plan` FK(`memberships.MembershipPlan`, nullable), `assigned_staff` FK, `trial_date` (nullable), `status` (pipeline enum per PRD §8.7), `next_follow_up`, `notes`, `converted_member` FK(`members.Member`, nullable — set on conversion).
- **`LeadActivity`**: `lead` FK, `activity_type`, `notes`, `created_by` FK, `created_at`.

### `migration`

- **`ImportJob`**: `organization` FK, `uploaded_by` FK, `file` (S3), `entity_type` (`MEMBERS`/`PAYMENTS`/...), `status` (`UPLOADED`/`VALIDATING`/`PREVIEW_READY`/`CONFIRMED`/`IMPORTING`/`COMPLETED`/`FAILED`), `total_rows`, `valid_rows`, `error_rows`, `created_at`, `completed_at`.
- **`ImportRowError`**: `job` FK, `row_number`, `raw_data` (JSON), `error_messages` (JSON).

### `audit`

- **`AuditLog`** (append-only, no update/delete permitted at the DB-permission or service level): `organization` FK (nullable for platform-level events), `actor` FK(`accounts.User`, nullable — null for system-initiated), `action`, `resource_type`, `resource_id` (or `resource_uuid`), `branch` FK (nullable), `before_state` (JSON, nullable), `after_state` (JSON, nullable), `occurred_at`, `request_id` (nullable, for tracing). **Indexes:** `(organization, occurred_at)`, `(resource_type, resource_id)`.

### `integrations`

- **`OrganizationIntegrationCredential`** (tenant-scoped, secrets encrypted at rest / stored via AWS Secrets Manager reference, never plaintext in DB): `organization` FK, `provider` (`RAZORPAY`/`WHATSAPP`/`SMS`/`BIOMETRIC_VENDOR_X`), `config` (JSON, non-secret fields only), `secret_ref` (reference/ARN, not the secret itself), `status`.
- No other tables — this app hosts Python abstract base classes/interfaces (`PaymentProvider`, `NotificationProvider`, `BiometricAdapter`), not additional persisted domain data.

---

# 28. Architecture Decisions

This section records decisions only after they are explicitly approved.

## ADR / Decision Log

| ID | Decision | Status | Date | Reason | Affected Areas |
|---|---|---|---|---|---|
| DEC-001 | Vue frontend | APPROVED BY PRD | 2026-09-24 | PRD technology baseline | Frontend |
| DEC-002 | Python Django backend | APPROVED BY PRD | 2026-09-24 | PRD technology baseline | Backend |
| DEC-003 | MySQL database | APPROVED BY PRD | 2026-09-24 | PRD technology baseline | Data |
| DEC-004 | AWS deployment | APPROVED BY PRD | 2026-09-24 | PRD technology baseline | Infrastructure |
| DEC-005 | Razorpay initial gateway | APPROVED BY PRD | 2026-09-24 | India-first V1 payment requirement | Payments |
| DEC-006 | Responsive web member experience in V1 | APPROVED BY PRD | 2026-09-24 | Native apps are Phase 2 | Member Portal |
| DEC-007 | 20-app Django decomposition (see §26.1.1) | PROPOSED — architect decision, no business/security trade-off requiring sign-off | 2026-09-25 | Concrete, reviewable module boundaries mapped 1:1 to domains | All backend modules |
| DEC-008 | Multi-tenancy: shared database, shared schema, mandatory `organization` FK + enforced queryset scoping | PROPOSED — architect decision | 2026-09-25 | See below | All tenant-owned data, Security |
| DEC-009 | Branch access: `home_branch` FK + `BranchAccess` grant table for additional access | PROPOSED — architect decision | 2026-09-25 | See below | Branches, Authorization |
| DEC-010 | Authentication: JWT (access + rotating refresh) via `djangorestframework-simplejwt`, access token in-memory on client, refresh token in `httpOnly` cookie | **APPROVED BY USER — 2026-09-28** | 2026-09-25 (approved 2026-09-28) | See below | Accounts, Security, Frontend |
| DEC-011 | Authorization: custom DRF permission classes + tenant/branch queryset-scoping mixins (no `django-guardian`) | PROPOSED — architect decision | 2026-09-25 | See below | Authorization, all modules |
| DEC-012 | Primary keys: `BigAutoField` internal PK + indexed `uuid` field for external-facing identifiers | PROPOSED — architect decision | 2026-09-25 | See below | Data model, Security, Attendance (QR) |
| DEC-013 | Background processing: Celery + Redis (broker + result backend) | PROPOSED — architect decision, matches PRD architecture diagram | 2026-09-25 | Already implied by PRD §10.1 diagram | Notifications, Reports, Migration |
| DEC-014 | File storage: S3 via `django-storages`, private bucket + presigned URLs for member photos/progress photos/imports | PROPOSED — architect decision | 2026-09-25 | AWS baseline; §36.3 upload safety | Members, Progress, Migration |
| DEC-015 | API conventions: URL versioning, `PageNumberPagination`, `django-filter`, consistent envelope + error schema, mandatory `Idempotency-Key` on payment-mutating endpoints | PROPOSED — architect decision | 2026-09-25 | See §30 | All APIs |
| DEC-016 | Testing: `pytest-django` + `factory_boy` + `pytest-cov`; mandatory tenant-isolation test module per tenant-owned app | PROPOSED — architect decision | 2026-09-25 | See §40 | All modules, CI |
| DEC-017 | Config: `django-environ`, per-environment settings modules (`base`/`dev`/`staging`/`production`), all secrets from environment/AWS Secrets Manager | PROPOSED — architect decision | 2026-09-25 | 12-factor, §47 secrets policy | Environments, Security |
| DEC-018 | Financial integrity: money always `Decimal`; `Payment` rows are append-only/immutable once terminal, corrections via `Refund`/`PaymentEvent` rows, never `UPDATE`/`DELETE` of settled amounts | PROPOSED — architect decision, directly mandated by `AGENTS.md` §15.4/§21.7/§34.4 | 2026-09-25 | Non-negotiable per AGENTS.md | Billing, Payments |
| DEC-019 | Audit logging: dedicated `audit.AuditLog` model + service call from sensitive service-layer operations (not Django admin log, not signals-only) | PROPOSED — architect decision | 2026-09-25 | Signals-only audit is fragile/bypassable; explicit service calls are traceable | Audit, all sensitive operations |
| DEC-020 | Concurrency: `select_for_update()` row locking + DB `CheckConstraint`s for capacity/PT-balance/freeze; no "check-then-insert" without a lock | PROPOSED — architect decision, mandated by `AGENTS.md` §15.3/§59.7/§59.10 | 2026-09-25 | Non-negotiable per AGENTS.md | Classes, PT, Memberships, Payments |

### DEC-008 — Multi-Tenancy Enforcement Strategy

**Context:** PRD §10.3 requires organization → branch → resource isolation.
MySQL is the fixed database choice (`DEC-003`). Target scale is 100–500
members/branch today, growing toward many gyms without a rewrite (PRD §9.2).

**Decision:** Single shared MySQL database, shared schema. Every tenant-owned
table carries a mandatory, indexed `organization_id` (via `core.TenantScopedModel`).
Enforcement is layered, not single-point:

1. **Model layer** — `TenantScopedModel`'s default manager refuses to return
   an unscoped queryset outside an explicit "system" context.
2. **View/service layer** — every DRF viewset resolves the organization from
   the **authenticated user**, never from a client-supplied `organization_id`
   or `branch_id` (`AGENTS.md` §16.2, non-negotiable). A shared
   `TenantScopedViewSetMixin` injects this automatically so it cannot be
   forgotten per-view.
3. **Test layer** — every tenant-owned app requires a tenant-isolation test
   proving org A cannot read/write org B data, per `AGENTS.md` §16.4 (mandatory,
   not optional).

**Alternatives considered:**
- *Schema-per-tenant* — not well supported by MySQL (no `search_path` like
  Postgres); would require per-tenant databases, which is operationally heavy
  for "many small independent gyms" and complicates cross-tenant admin/reporting.
- *Database-per-tenant* — same operational weight, rejected for the same reason,
  and contradicts the "no complex AWS architecture without documented reason"
  rule (§48) at this budget tier.

**Reason:** Shared-schema row-level isolation is the standard, proven approach
for this scale and budget tier, keeps a single set of migrations, and is what
the PRD's own architecture diagram (single MySQL box) already implies.

**Consequences:** All future models MUST inherit `TenantScopedModel` (or be
scoped transitively through a FK to one, e.g. `InvoiceLineItem` via `Invoice`).
Code review / tests must catch any raw `Model.objects.all()` call that bypasses
tenant scope.

**Risks:** A missed scope check on any single endpoint is a tenant-isolation
breach — mitigated by the mixin + mandatory tests, not by developer discipline
alone.

**Affected modules:** All.

**Related requirements:** REQ-053, REQ-066, all of §59.1–§59.2.

---

### DEC-009 — Branch Access Model

**Context:** PRD §8.10/§16.3: Owner = all branches; Staff/Trainer default =
assigned branch only; Member = home branch + optional additional branches
"if configured."

**Decision:** `accounts.User.home_branch` (nullable FK, null only for `OWNER`)
+ `members.Member.home_branch` (required FK) + a shared `branches.BranchAccess`
grant table for the *exception* cases (staff/trainer/member granted access
beyond their home branch). `OWNER` role bypasses branch checks entirely (checked
via role, not enumerated grant rows, to avoid an all-branches row explosion).

**Alternatives considered:** Pure M2M `User.branches` / `Member.branches`
with no "home" concept — rejected because the PRD explicitly distinguishes a
primary "home" branch from occasional additional access, and reporting/UX
(e.g. "which branch is this member normally at") needs a single authoritative
home branch, not an ambiguous M2M set.

**Reason:** Matches PRD language precisely; keeps the common case (single
branch) cheap (one FK, no join) while still supporting the configurable
multi-branch exception.

**Consequences:** Authorization checks must check `home_branch` OR
`BranchAccess` OR `role == OWNER` — this three-way check is centralized in one
permission helper, not reimplemented per view.

**Risks:** None beyond the general authorization-leakage risk already tracked
in §59.2.

**Affected modules:** Branches, Authorization, Members, Trainers.

**Related requirements:** REQ-053, REQ-054.

---

### DEC-010 — Authentication Mechanism ✅ APPROVED BY USER (2026-09-28, GYM-004)

**Approval note:** Proposed 2026-09-25, flagged for explicit user review.
User confirmed **"Jwt"** on 2026-09-28. Status upgraded from `PROPOSED` to
`APPROVED`. No change to the design itself — recorded verbatim as proposed.

**Context:** `AGENTS.md` §18 requires a centralized, explicitly-decided
authentication mechanism. This is the single most consequential, hardest-to-reverse
decision in this architecture pass, and PRD §13.3 already earmarks native
mobile apps for Phase 2 (which will need to reuse the same backend API).

**Decision:** Stateless JWT via `djangorestframework-simplejwt`:
- **Access token:** short-lived (~15 min), sent as `Authorization: Bearer`,
  held only in Vue application memory (never `localStorage`, to reduce XSS
  token-theft blast radius).
- **Refresh token:** longer-lived (~7–14 days), **rotating** (a new refresh
  token is issued on every use, old one is blacklisted — `simplejwt`'s
  `ROTATE_REFRESH_TOKENS` + blacklist app), stored in an `httpOnly`, `Secure`,
  `SameSite=Lax` cookie scoped to the API's domain.
- Logout blacklists the current refresh token server-side (mitigates the usual
  "can't log out a JWT" complaint).
- Frontend and API are deployed on separate subdomains of the same top-level
  domain (e.g. `app.<domain>` for the Vue SPA on S3/CloudFront, `api.<domain>`
  for Django on ALB) with CORS configured to allow credentials from `app.<domain>`
  only.

**Alternatives considered:**
- **Django session auth + CSRF cookie** — simpler, server can invalidate a
  session instantly, no client-side token-refresh logic needed. Rejected as
  the *primary* choice because: (a) it couples the API tightly to
  cookie-based browser sessions, complicating Phase 2 native-mobile reuse of
  the same API; (b) with a separate `app.<domain>`/`api.<domain>` split it
  needs the same `SameSite`/CORS care as cookie-based JWT refresh anyway, so
  the usual "sessions are simpler" advantage shrinks once subdomains are
  split for CDN-friendly SPA hosting.
- **Long-lived single JWT, no refresh** — rejected: no clean revocation story,
  a stolen long-lived token is a large blast radius.

**Why this was flagged rather than silently decided:** `AGENTS.md` §43
classifies authentication as a HIGH-risk change category requiring explicit
approval-status tracking. It was the one choice in this pass where a
reasonable engineer could legitimately prefer session-based auth instead, and
it is hard to change later without touching every client. **Resolved:** user
confirmed JWT on 2026-09-28 — see approval note above.

**Consequences:** Vue app needs an auth store that holds the access token in
memory, refreshes silently via a call that relies on the `httpOnly` cookie,
and re-authenticates on hard refresh. Requires `django-cors-headers` +
`SIMPLE_JWT` blacklist app configured.

**Risks:** Access-token-in-memory mitigates XSS exfiltration of a persistent
token but the access token is still bearer-style for its short lifetime; CORS
misconfiguration would be a security bug — must be covered by a security-review
checklist item before production.

**Affected modules:** Accounts/Auth, all API consumers, Frontend.

**Related requirements:** REQ-060, §17 (frontend permissions are UX only —
unaffected by this choice), §59.12.

---

### DEC-011 — Authorization Implementation

**Context:** Roles are fixed (`OWNER`/`STAFF_ADMIN`/`TRAINER`/`MEMBER`, PRD
§6/AGENTS.md §17). Branch scoping adds a second dimension beyond simple role
checks (`DEC-009`).

**Decision:** Custom DRF `permission_classes` (e.g. `IsOrgMember`,
`HasRole(*roles)`, `HasBranchAccess`) composed per viewset, backed by a shared
queryset-scoping mixin (ties into `DEC-008`). Object-level checks (e.g. "this
trainer may only modify their own assigned PT sessions") are implemented as
explicit service-layer checks, not relied upon via URL-hiding or frontend
checks (§17.5/§72).

**Alternatives considered:** `django-guardian` (per-object permission rows in
the DB) — rejected as unnecessary weight; the permission model here is
describable by role + org + branch + ownership FK comparison, which doesn't
need a generic per-object ACL table.

**Reason:** Matches the actual shape of the PRD's role matrix without
over-engineering.

**Consequences:** Every viewset must declare its permission classes
explicitly; a lint/test convention should assert no viewset is missing them
(to be added when DRF scaffolding exists).

**Risks:** None beyond general authorization-leakage risk (§59.2), mitigated
by centralization + mandatory authorization tests (§41.2).

**Affected modules:** Authorization, all modules.

**Related requirements:** REQ-060.

---

### DEC-012 — Primary Key / External Identifier Strategy

**Context:** Sequential integer IDs exposed in URLs or QR codes can leak
information via enumeration (e.g. probing `/api/v1/members/43/` across
organizations, or predicting another member's QR code).

**Decision:** Internal PK stays `BigAutoField` (fast joins/indexes, MySQL-friendly,
matches PRD's own `id` field convention in §10.4). Every `TenantScopedModel`
additionally carries an indexed, unique `uuid` field. **All externally-exposed
identifiers (API resource URLs, QR check-in tokens) use the `uuid`/opaque
token, never the raw integer PK.**

**Alternatives considered:** UUID as the actual PK — rejected; larger index
size, worse MySQL `InnoDB` clustering-index locality at this write volume,
with no additional benefit once a separate external `uuid` field exists.

**Reason:** Gets the security benefit (non-enumerable external references)
without the MySQL performance cost of a random-UUID clustered primary key.

**Consequences:** Serializers must expose `uuid` (aliased as `id` in the API
response) instead of the internal PK; internal PK never appears in a response
body.

**Risks:** None significant; minor extra index storage cost, acceptable at
this scale.

**Affected modules:** Data model (all), Attendance (QR), API layer.

**Related requirements:** REQ-053, REQ-066.

---

### DEC-013 — Background Processing

**Decision:** Celery workers + Redis as broker and result backend (matches
the PRD's own architecture diagram, §10.1). Used for: notification delivery
(§29.2), large report generation (§9.1 "async" requirement), scheduled
expiry/reminder scans, CSV import processing (§13.1/§31).

**Alternatives considered:** Synchronous-only (rejected — violates PRD's
explicit async requirement for large reports and notification non-blocking
rule §29.2); Django-Q / RQ (rejected — Celery is the de facto standard with
the widest Django ecosystem support, and Redis is already in the approved
architecture diagram as the intended broker).

**Consequences:** Requires a Redis instance (ElastiCache in AWS) and at least
one worker process/container in every environment including local dev
(`docker-compose` for local).

**Affected modules:** Notifications, Reports, Data Migration.

**Related requirements:** REQ-050, REQ-051, REQ-069.

---

### DEC-014 — File Storage

**Decision:** `django-storages` with S3 backend, private bucket, presigned
URLs for read access (profile photos, progress photos, medical notes
attachments if any, CSV import files). No public-read bucket for
member-identifiable content.

**Consequences:** Requires `AWS_STORAGE_BUCKET_NAME`, IAM role/credentials as
environment/secret config (`DEC-017`); upload validation (type/size/safe
filename generation) enforced server-side per `AGENTS.md` §36.3 before the S3
`PUT`.

**Affected modules:** Members, Progress, Data Migration.

**Related requirements:** §36.3.

---

### DEC-015 — API Conventions

See the fully expanded convention set in §30. Summary: `/api/v1/` prefix,
`PageNumberPagination` (default page size 25, max 100), `django-filter` for
filtering, consistent JSON envelope (`{"data": ..., "meta": ...}` for
collections, error envelope `{"error": {"code", "message", "field_errors"}}`),
mandatory `Idempotency-Key` header support on `payments`/`billing`
mutating endpoints (defense-in-depth alongside `PaymentEvent.gateway_event_id`
webhook dedup).

**Affected modules:** All APIs.

**Related requirements:** REQ-035, §32.

---

### DEC-016 — Testing Strategy

**Decision:** `pytest-django` (clearer fixtures/parametrization than
`unittest`-style `TestCase` for this project's needs) + `factory_boy` (test
data factories per model, avoids brittle fixture JSON) + `pytest-cov`. Every
tenant-owned app ships a `test_tenant_isolation.py` as a first-class,
non-optional file (not "add tests if time permits").

**Alternatives considered:** Plain Django `TestCase` — still fully compatible
with `pytest-django` (it can run existing `TestCase`s), so no lock-in risk;
chosen `pytest` primarily for fixture composition and parametrized
concurrency tests (e.g. simulating N simultaneous booking attempts).

**Affected modules:** All, CI.

**Related requirements:** §41 (all).

---

### DEC-017 — Configuration / Environment Strategy

**Decision:** `django-environ` reading from `.env` (local only, gitignored)
or real environment variables (staging/production). Settings split into
`config/settings/{base,dev,staging,production}.py`. Secrets (DB password,
Django `SECRET_KEY`, Razorpay keys, JWT signing key if asymmetric, AWS
credentials) come from environment variables backed by AWS Secrets
Manager/Parameter Store in staging/production — **never committed**.

**Affected modules:** Environments, Security.

**Related requirements:** §47 (all).

---

### DEC-018 — Financial Data Integrity

**Decision:** (Restates and makes concrete the already-mandatory `AGENTS.md`
§15.4/§21.7/§34.4 rules for this schema.) All money fields are `DecimalField`.
`Payment` rows, once `SUCCESSFUL`, are never `UPDATE`d to a different amount or
`DELETE`d; corrections happen via new `Refund` rows and `PaymentEvent` entries.
Webhook processing dedups via `PaymentEvent.gateway_event_id` unique index
(`DEC-008`'s tenant scoping + this index together prevent both cross-tenant
leakage and duplicate financial side effects).

**Affected modules:** Billing, Payments.

**Related requirements:** REQ-035, REQ-036, REQ-037, §59.5–§59.6.

---

### DEC-019 — Audit Logging Approach

**Decision:** Dedicated `audit.AuditLog` model, written to via explicit
service-layer calls (`audit_log(actor, action, resource, before, after)`) at
the point sensitive operations occur (freeze/unfreeze, manual check-in
override, refunds/financial corrections, role changes, member status changes,
import confirmation) — not via Django's admin `LogEntry` (too narrow, only
covers admin-site edits) and not purely via signals (signals can silently miss
bulk/`update()` operations and make the "who/why" context harder to capture).

**Affected modules:** Audit, and every module with a sensitive-action list in
`AGENTS.md` §17.6/§38.

**Related requirements:** REQ-024, REQ-030.

---

### DEC-020 — Concurrency Control

**Decision:** Every finite-resource state transition identified in `AGENTS.md`
§59.7/§59.10 (class capacity, PT package balance) uses `select_for_update()`
inside an atomic transaction at the moment of commit (booking creation, PT
session completion), backed by a DB `CheckConstraint` as a last-resort guard
(e.g. `sessions_consumed <= sessions_purchased`). A plain "count existing rows,
then insert if under capacity" pattern without a lock is explicitly disallowed
— it is a known race condition (the "last seat" problem, §23.2).

**Affected modules:** Classes, Personal Training, Memberships (freeze),
Payments (webhook dedup uses a unique constraint rather than a lock, since
it's an insert-time dedup, not a decrement).

**Related requirements:** REQ-038, REQ-044, §59.7, §59.10.

---

### DEC-021 — Waitlist is a Booking status, not a second table (GYM-011)

**Decision:** Class waitlist is `Booking.status=WAITLISTED`. There is no separate Waitlist table. Cancellation of a BOOKED row releases capacity and does **not** auto-promote a waitlisted booking (AGENTS.md §23.4; REQ-040 promotion policy remains an open product question).

MySQL cannot express a partial unique constraint of “one active booking per (occurrence, member)”. `book_occurrence` enforces that in the service layer after locking the occurrence.

The Django app lives at package `classes` with app label `gym_classes` (Python `classes` collides with the stdlib name only as a module path; the label avoids Django app-label issues).

Overlap checks for members and trainers are shared in `pt.services` and cover both class occurrences and PT sessions so a member cannot hold a class and a PT session at the same time.

**Affected modules:** Classes, Personal Training.

**Related requirements:** REQ-038, REQ-039, REQ-040, REQ-041.

---

### DEC-022 — Notifications are console/in-app only until vendors are chosen (GYM-014)

**Decision:** V1 notification delivery uses `NotificationProvider` → `ConsoleNotificationProvider`. Templates and `NotificationLog` persist per organization. Domain services enqueue `MEMBERSHIP_CREATED`, `PAYMENT_SUCCESSFUL`, `CLASS_BOOKING`, `PT_BOOKING`, and `FREEZE_APPROVED` via `transaction.on_commit` so a notify failure cannot roll back money, booking, freeze, or membership state. Waitlisted bookings do not emit `CLASS_BOOKING`. Duplicate webhooks do not emit a second `PAYMENT_SUCCESSFUL`.

WhatsApp/SMS/email HTTP is **not** implemented (OQ-001/002 remain OPEN). Reminder/birthday/expiry events exist on the enum but have no scheduler yet.

**Affected modules:** Notifications, Classes, PT, Payments, Memberships.

**Related requirements:** REQ-051, REQ-052.

---

### Decisions Still Genuinely Open (Not Resolved By This Pass)

These remain deliberately unresolved — they are business/vendor/legal
decisions, not technical architecture, and `AGENTS.md` §2.4/§44 forbids
guessing on them:

- WhatsApp provider (OQ-001)
- SMS provider (OQ-002)
- Biometric vendor (OQ-003)
- Exact GST invoice field/legal requirements (OQ-004) — schema keeps a
  flexible `gst_details` JSON snapshot on `Invoice` pending finance/legal sign-off
- Exact membership freeze policy calculation (OQ-005) — schema stores the
  *choice* (`Organization.freeze_policy` enum) but not which policy is correct/default
- Cross-branch membership configuration specifics (OQ-006) — schema supports
  it via `BranchAccess`; exact business rules for when it's granted are undecided
- Trial membership behavior (OQ-007)
- Exact AWS service sizing/selection (instance types, RDS Multi-AZ timing,
  ECS vs EC2 for Celery workers) (OQ-009) — directional mapping only, in §43
- CI/CD platform — depends on where the repository will be hosted/remote,
  currently local-only; not yet chosen
- Observability/APM stack — not yet chosen

No engineering assumption above should be treated as approved until recorded as such.

---

# 29. Database / Migration State

## Current State

Database schema: **DESIGNED** (GYM-003 §27.A) and **partially migrated**
through Phase 3 domain apps.

Django migrations applied on the local compose MySQL service (GYM-008):

```text
accounts, organizations, branches, members, memberships, attendance,
billing.0001_initial, payments.0001_initial
(+ Django contrib + token_blacklist)
```

Seed/reference data: NONE (tests use `factory_boy` only)

Production migration tooling: NONE

Data import tooling: NONE

## Identifier / Indexing Approach (GYM-003 / DEC-012)

- Internal PK: `BigAutoField` on every table.
- External-facing identifier: indexed unique `uuid` field on every
  `TenantScopedModel`, used in all API URLs and QR tokens instead of the raw PK.
- Every tenant-scoped table indexes `organization_id` (and `branch_id` where
  present) as the leading column of its most common filter, per `AGENTS.md` §34.3.
- Financial lookup indexes: `Payment.gateway_payment_id`,
  `PaymentEvent.gateway_event_id` (unique — webhook idempotency guard),
  `Payment.idempotency_key` (unique, nullable).
- Booking uniqueness: `(occurrence, member)` unique where not cancelled.

## Database Principles

The implementation must account for:

- organization ownership
- branch ownership
- uniqueness
- status/lifecycle
- auditability
- financial immutability
- indexing
- concurrency
- migration safety
- data import safety

## Critical Financial Data

Payment and invoice history must not be casually hard-deleted or mutated.

Controlled correction/refund workflows are required.

## Migration Rule

Any schema change requires:

1. identify affected models
2. identify API impact
3. identify frontend impact
4. identify data impact
5. create migration
6. test migration
7. assess rollback
8. update PROJECT_CONTEXT.md

---

# 30. API State

## API Baseline

Approved API namespace (`DEC-015`):

```text
/api/v1/
```

## Approved Domain Groups

```text
/api/v1/auth                 (login, refresh, logout, password reset)
/api/v1/organizations
/api/v1/branches
/api/v1/members
/api/v1/memberships
/api/v1/attendance
/api/v1/billing
/api/v1/payments
/api/v1/classes
/api/v1/personal-training
/api/v1/trainers
/api/v1/workouts
/api/v1/progress
/api/v1/notifications
/api/v1/reports              (includes owner-dashboard aggregation endpoints)
/api/v1/crm
/api/v1/migration
```

## Current API Status

Implemented (GYM-010 + GYM-011), all under `/api/v1/`, JWT except the Razorpay webhook:

```text
GET/POST          /members/                  staff create/list; role-scoped
GET/PATCH/DELETE  /members/{uuid}/           soft-delete on DELETE
GET               /members/me/               MEMBER only
POST              /members/{uuid}/provision-login/   OWNER/STAFF_ADMIN
GET               /branches/
GET/POST          /memberships/plans/
GET/POST          /memberships/
POST              /memberships/{uuid}/freeze/
POST              /memberships/{uuid}/unfreeze/
POST              /memberships/{uuid}/renew/
POST              /memberships/{uuid}/request-freeze/     MEMBER own
GET               /memberships/freeze-requests/
POST              /memberships/freeze-requests/{uuid}/approve/
POST              /memberships/freeze-requests/{uuid}/reject/
GET               /attendance/
POST              /attendance/check-in/
GET/POST          /billing/
GET               /payments/
POST              /payments/cash/
POST              /payments/initiate/            MEMBER/staff; Fake if no Razorpay keys
GET               /payments/subscriptions/       read-only; no charge
POST              /payments/webhooks/razorpay/   AllowAny + HMAC
GET               /classes/trainers/
GET/POST          /classes/catalog/          POST = OWNER/STAFF_ADMIN
GET/POST          /classes/occurrences/      POST = OWNER/STAFF_ADMIN; trainer conflict 409
POST              /classes/occurrences/{uuid}/cancel/
GET               /classes/bookings/
POST              /classes/bookings/book/        OWNER/STAFF/MEMBER; TRAINER 403
POST              /classes/bookings/{uuid}/cancel/
GET/POST          /pt/packages/              POST = OWNER/STAFF_ADMIN
GET               /pt/sessions/
POST              /pt/sessions/schedule/
POST              /pt/sessions/{uuid}/reschedule/
POST              /pt/sessions/{uuid}/complete/
POST              /pt/sessions/{uuid}/cancel/
```

Organization is always taken from the authenticated user. Client-supplied
`organization_id` is ignored. List/detail queries are further restricted by
role (OWNER = org; STAFF_ADMIN = authorized branches; TRAINER = assigned
members; MEMBER = own rows).

## Approved API Conventions (GYM-003 / DEC-015)

**Authentication:** `Authorization: Bearer <access_token>` header (JWT, per
`DEC-010`). Refresh via `httpOnly` cookie against `/api/v1/auth/refresh/`.

**Pagination:** DRF `PageNumberPagination`, default `page_size=25`, max
`page_size=100` (client-overridable up to the max via `?page_size=`).

**Filtering/sorting:** `django-filter` `FilterSet` per list endpoint for
filterable fields explicitly declared per resource (never arbitrary
field-name-based filtering); sorting via `?ordering=` on an explicit allow-list
of fields.

**Response envelope:**

```json
{
  "data": { /* object or array */ },
  "meta": { "page": 1, "page_size": 25, "total": 143 }
}
```

**Error envelope** (consistent across all endpoints, no stack traces/SQL/internal
IDs leaked, per `AGENTS.md` §32.2):

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable summary",
    "field_errors": { "phone": ["Already registered in this organization."] }
  }
}
```

**Status codes:** standard REST semantics (`200`/`201`/`204`/`400`/`401`/`403`/`404`/`409`/`422`/`429`/`500`); `409 Conflict` reserved for concurrency-losing
requests (e.g. class full by the time the lock was acquired).

**Idempotency:** Any endpoint that creates a financial side effect (payment
initiation, refund, invoice generation) must accept an optional
`Idempotency-Key` header; the server persists and returns the original
response for a repeated key within a TTL window. This is in addition to (not
instead of) `PaymentEvent.gateway_event_id` webhook-level dedup — defense in
depth per `AGENTS.md` §21.4.

**Versioning:** URL path versioning only (`/api/v1/`); no header-based
versioning scheme, to keep the contract simple and cache-friendly.

## API Contract Requirements

Before frontend dependence, each meaningful endpoint must define:

- method
- URL
- authentication
- authorization
- request
- validation
- response
- errors
- database effects
- transactions
- audit effects
- idempotency where applicable

---

# 31. Frontend State

## Technology

Vue

## Current State

Frontend project: **IMPLEMENTING** (GYM-009 + GYM-010 + GYM-011). Vue 3.5 + Vite 5 + Pinia + Vue Router.

Implemented:
- `src/api/client.js` — `/api/v1` client, `{data}` / `{error}` envelope, credentials included so the httpOnly refresh cookie is sent to `/api/v1/auth/` only.
- Access token held in `window.__gymportalAccessToken` (memory). Never written to `localStorage` / `sessionStorage` (DEC-010; covered by a vitest).
- `src/stores/auth.js` — login / logout / bootstrap-via-refresh.
- Routes: `/login` (public), `/` (home), `/members`, `/members/:id`, `/check-in`, `/classes`, `/pt` (staff-only), `/portal` (MEMBER only).
- Front-desk flows: register member, add plan, sell membership + cash invoice, search + check-in, create/schedule/book classes, sell PT package + schedule/complete, enable portal login.
- Member portal: membership, invoices, class book-self, attendance, PT packages/sessions.
- Dockerfile + compose `frontend` service (`npm run dev` on :5173).

Not implemented: workout/progress screens, form libraries, CSS framework.

## V1 Frontend Areas

Likely application areas based on PRD:

- authentication
- owner dashboard
- front desk workflows
- member management
- membership management
- attendance/check-in
- billing
- payments
- classes
- PT
- trainer management
- workouts
- progress
- notifications
- reports
- member portal
- settings

Exact component structure remains an implementation decision.

## Critical UX Requirements

### Check-in

The check-in experience must be optimized for speed.

### Member Portal

Member workflows must be mobile-responsive.

### Dashboard

Owner dashboard must prioritize operational visibility over visual complexity.

---

# 32. Roadmap

## Phase 0 — Foundation — Week 1

PRD scope:

- AWS environment
- Django project
- Vue application
- authentication
- tenant architecture
- branch architecture
- user roles
- database foundation
- CI/CD
- logging

Current Phase: ACTIVE / NOT YET IMPLEMENTED

## Week 2 — Members & Memberships

- Member CRUD
- search/filter
- member profile
- membership plans
- membership lifecycle
- freeze/hold
- renewal

## Week 3 — Attendance

- QR generation
- QR scanning
- staff check-in
- attendance history
- eligibility validation
- basic biometric/RFID adapter interface

## Week 4 — Billing

- invoices
- payments
- Razorpay
- webhooks
- payment history
- outstanding dues
- renewal payment

## Week 5 — Classes & PT

- class management
- trainer calendar
- capacity
- booking
- cancellation
- PT packages
- PT sessions

## Week 6 — Member Portal + Workout

- member dashboard
- membership
- payments
- booking
- attendance
- workout plans
- workout logging
- progress

## Week 7 — Staff + Reporting

- staff management
- trainer management
- owner dashboard
- revenue reports
- attendance reports
- membership reports

## Week 8 — Production Readiness

- notifications
- data migration
- security testing
- performance testing
- UAT
- bug fixing
- production deployment

---

# 33. Phase 2

The PRD lists:

- native mobile
- WhatsApp automation
- advanced CRM
- lead campaigns
- advanced analytics
- biometric vendor integrations
- RFID/access control
- trainer compensation automation
- advanced member progress
- push notifications
- member referral system

---

# 34. Phase 3

The PRD lists:

- AI workout recommendations
- AI retention/churn prediction
- nutrition
- advanced marketing automation
- franchise management
- accounting integrations
- inventory/POS
- advanced payroll
- public gym website
- white-label mobile apps
- API marketplace

---

# 35. Module Status

| Module | Priority | Status | Current Task | Blocker |
|---|---|---|---|---|
| Accounts / Auth | Must | **IMPLEMENTING** (GYM-005/018 — JWT auth + login 5/min throttle) | — | AWS HTTPS not started |
| Organizations / Tenants | Must | **IMPLEMENTING** (GYM-005 — Organization/OrganizationSettings live) | Phase 1: members app | — |
| Branches | Must | **IMPLEMENTING** (GYM-005 — Branch/BranchAccess(user) live; member-grant deferred to Phase 1) | Phase 1: members app | — |
| Authorization | Must | **IMPLEMENTING** (GYM-005 — permission classes + viewset mixin live, not yet exercised by a real viewset) | Phase 1: members app | — |
| Members | Must | **IMPLEMENTING** (GYM-010/013/018 — CRUD + portal + `sync_member_status`) | — | — |
| Memberships | Must | **IMPLEMENTING** (GYM-010/018 — freeze/renew + FreezeRequest approve) | — | Freeze policy default = OQ-005 |
| Attendance | Must | **IMPLEMENTING** (GYM-010/017/018 — search + QR + adapter interface) | Vendor HTTP | OQ-003 |
| Billing | Must | **IMPLEMENTING** (GYM-010/014 — invoice + `related_pt_package`) | — | GST field detail = OQ-004 |
| Payments | Must | **IMPLEMENTING** (GYM-010/018 — cash + initiate Fake + subscription list) | Live gateway | Real Razorpay create_order/refund NOT EXECUTED |
| Classes | Must | **IMPLEMENTING** (GYM-012/018 — booking + portal cancel) | — | Waitlist auto-promote = OQ / §23.4 |
| Personal Training | Must | **IMPLEMENTING** (GYM-012/018 — consume + reschedule + Today) | — | Policy override = OQ |
| Trainers / Staff | Must | **IMPLEMENTING** (GYM-015 — OWNER staff write + TrainerProfile + Vue `/staff`) | — | No payroll |
| Workouts | Must | **IMPLEMENTING** (GYM-014 — Program→Day→Exercise + logs + Vue) | — | No AI coaching |
| Progress | Must | **IMPLEMENTING** (GYM-014 — entries/PRs + Vue) | — | Photo upload hardening deferred |
| Member Portal | Must | **IMPLEMENTING** (GYM-013/018 — freeze-request, cancel, pay, payments) | — | Live checkout BLOCKED on keys |
| Notifications | Must | **IMPLEMENTING** (GYM-014/016 — all 11 in-app events; Vue `/notifications`) | Vendor HTTP | OQ-001/002 |
| Dashboard | Must | **IMPLEMENTING** (GYM-014/018 — OWNER dashboard + `by_branch`) | PDF | — |
| Reports | Must | **IMPLEMENTING** (GYM-014/017/018 — JSON + CSV + expired + by_branch) | PDF | — |
| CRM / Leads | Should | **IMPLEMENTING** (GYM-014 — pipeline + convert + Vue) | — | No marketing automation |
| Data Migration | Must | **IMPLEMENTING** (GYM-014 — members CSV preview/confirm + Vue) | Excel | — |
| Integrations | Must/Should by integration | **IMPLEMENTING** (GYM-018 biometric adapter interface; Razorpay still Fake/live-unverified) | Vendor HTTP | OQ-001/002/003 |
| Audit | Must for sensitive actions | **IMPLEMENTING** (GYM-014 — append-only AuditLog + freeze/check-in/refund hooks) | Broader action coverage | — |
| Production / Operations | Must | **IMPLEMENTING** (GYM-016 — `/healthz/` + `/readyz/`; AWS still ANALYSIS) | Backups/alerting | Exact AWS sizing = OQ-009 |

---

# 36. Active TODO

## Immediate

- [x] Verify repository contains `PRD.md`
- [x] Verify `AGENTS.md` is present and approved
- [x] Maintain this `PROJECT_CONTEXT.md`
- [x] Complete requirements traceability (GYM-002 — `REQ-001`..`REQ-069`)
- [x] Perform architecture design (GYM-003)
- [x] Finalize authentication approach (GYM-004 — DEC-010 JWT approved)
- [x] Finalize multi-tenant enforcement approach (GYM-003/005 — DEC-008)
- [x] Finalize branch authorization strategy (GYM-003/005/006 — DEC-009)
- [x] Design complete data model (GYM-003 §27.A)
- [x] Design API conventions (GYM-003 — DEC-015)
- [x] Design test strategy (GYM-003 — DEC-016)
- [x] Establish Django project foundation (GYM-005)
- [x] Establish Vue project foundation (GYM-009 — login/home auth shell)
- [x] Build first real domain viewsets (GYM-010)
- [x] Phase 4 booking + PT consume foundation (GYM-011)
- [x] Staff class/occurrence write + PT front-desk Vue (GYM-012)
- [x] Phase 5 member portal (self-service using existing APIs) (GYM-013)
- [x] Phase 5 workouts / progress (Program→Day→Exercise) (GYM-014)
- [x] Add `billing.InvoiceLineItem.related_pt_package` FK now that `pt` exists (GYM-014)
- [x] Threaded/concurrency tests for last-seat booking and PT double-complete (GYM-014)
- [x] Organization-configurable `min_checkin_interval_minutes` (GYM-014; product default 120 still provisional)
- [x] Wire `audit.AuditLog` into freeze/override/refund (GYM-014)
- [x] Staff/trainer directory + basic compensation calc (REQ-046/047, no payroll) (GYM-015)
- [x] Celery beat in-app reminders (MEMBERSHIP_EXPIRING / CLASS_REMINDER / PT_REMINDER) (GYM-015)
- [x] Owner dashboard CSV export (REQ-050 CSV only) (GYM-015)
- [x] Birthday / MEMBERSHIP_EXPIRED in-app scans (remaining REQ-051) (GYM-016)
- [x] Local healthz/readyz dependency probes (GYM-016)
- [x] PAYMENT_FAILED in-app hook + Vue notification log (GYM-016)
- [x] Staff QR camera scan for check-in (REQ-004 remainder) (GYM-017)
- [x] Owner expired-members CSV (REQ-015) (GYM-017)
- [x] Staff freeze/unfreeze on member detail (REQ-007 admin path) (GYM-017)
- [x] Staff renew UI on member detail (GYM-018)
- [x] Member freeze-request + staff approve/reject (no auto-approve) (GYM-018)
- [x] Portal cancel booking + member payments list + Pay initiate (GYM-018)
- [x] Trainer PT Today + in-place reschedule (GYM-018)
- [x] `sync_member_status` from latest membership (GYM-018)
- [x] Owner dashboard `revenue.by_branch` (GYM-018)
- [x] Login throttle 5/min (GYM-018)
- [x] Biometric/RFID adapter interface only (GYM-018)
- [x] Subscription list without charge/retry (GYM-018)
- [x] Member initiate via FakePaymentProvider when Razorpay keys empty (GYM-018)

## Deferred / blocked — not leftover implementation tasks

These remain **intentionally unimplemented**. Do not pick them as the next coding task unless the user supplies the missing decision or credentials.

- Recurring billing charge/retry for `Subscription` — DEFERRED (no invented retry policy)
- Live Razorpay `create_order`/`process_refund` against a real test-mode account — BLOCKED (keys + network verification)
- Report PDF export (REQ-050 remainder) — DEFERRED (CSV exists)
- Waitlist auto-promotion — MUST remain unimplemented until product policy is approved (AGENTS.md §23.4)
- WhatsApp/SMS vendor HTTP — BLOCKED (OQ-001/002)
- GST named invoice columns — BLOCKED (OQ-004)
- AWS / production backups / alerting — NOT STARTED (OQ-009)

## Not Yet Started (ops only)

AWS / production. No implementable V1 leftover remains in Active TODO.

---

# 37. Blockers

Current blockers:

**None blocking documentation initialization.**

Potential implementation blockers requiring decisions:

- authentication mechanism
- WhatsApp provider
- SMS provider
- biometric vendor
- exact GST invoice interpretation
- cross-branch membership behavior
- membership freeze approval/configuration
- trial membership behavior
- AWS service choices
- exact CI/CD infrastructure

These are open decisions, not implementation failures.

---

# 38. Open Questions / Conflicts

| ID | Question | Source | Status | Impact |
|---|---|---|---|---|
| OQ-001 | WhatsApp provider | PRD | OPEN | Notifications |
| OQ-002 | SMS provider | PRD | OPEN | Notifications |
| OQ-003 | Biometric vendor | PRD | OPEN | Attendance |
| OQ-004 | Exact GST invoice rules | PRD | OPEN | Billing |
| OQ-005 | Membership freeze policy | PRD says configurable | OPEN | Membership |
| OQ-006 | Cross-branch membership rules | PRD says configuration required | OPEN | Branches/Memberships |
| OQ-007 | Trial membership behavior | PRD says recommended | OPEN | Memberships |
| OQ-008 | Exact authentication mechanism | Engineering design | OPEN | Accounts/Security |
| OQ-009 | Exact AWS service architecture | Engineering design | OPEN | Operations |
| OQ-010 | Exact async/background processing implementation | Engineering design | OPEN | Notifications/Reports |

No open question should be silently resolved when it materially changes product behavior.

---

# 39. Known Risks

## Technical

### Payment Gateway Dependency

Recurring payments depend on gateway capabilities, mandate rules and webhook reliability.

Mitigation:

```text
PaymentService
      ↓
PaymentProvider Interface
      ↓
RazorpayProvider
Future Providers
```

### Biometric Compatibility

Different gyms may use different hardware.

Mitigation:

```text
Access Control Interface
        ↓
Vendor Adapter
```

### Migration Quality

Legacy data may contain:

- duplicates
- missing phone numbers
- invalid dates
- duplicate payments
- inconsistent membership status

Mitigation:

```text
Upload
 ↓
Validate
 ↓
Preview
 ↓
Fix
 ↓
Confirm
 ↓
Import
 ↓
Report
```

## Product Risk

The PRD identifies the biggest MVP risk as attempting too much within eight weeks.

Primary V1 focus:

```text
Member
   ↓
Membership
   ↓
Attendance
   ↓
Payment
   ↓
Booking
   ↓
PT
   ↓
Member Self-Service
```

## Adoption Risk

Potential staff resistance to leaving Excel/WhatsApp.

Mitigation priority:

- speed
- simple workflows
- front-desk usability
- reliable reports

## Trust Risk

Owners may not trust reports if financial figures do not align with payment data.

Important controls:

- payment IDs
- gateway IDs
- audit logs
- refund history
- reconciliation

---

# 40. Testing State

## Current Status

**245 passed, 0 failed** — executed 2026-09-28 via
`docker compose run --rm backend pytest -q` after GYM-018. Frontend: vitest 1
passed + `vite build` succeeded.

GYM-018 closed implementable leftovers: freeze request, renew UI, portal cancel/pay,
PT reschedule/Today, member status sync, branch revenue, login throttle, adapter
interface, subscription list.

## Approved Testing Tooling (GYM-003 / DEC-016)

- **Test runner:** `pytest` + `pytest-django`.
- **Test data:** `factory_boy` factories per model (no brittle static JSON fixtures for anything with FK relationships).
- **Coverage:** `pytest-cov`; tracked but no arbitrary numeric gate invented — coverage of the *high-risk areas* in §41 is mandatory regardless of overall %.
- **Mandatory file per tenant-owned app:** `test_tenant_isolation.py` proving org-A/org-B separation (`AGENTS.md` §16.4) — required before a module can be marked `COMPLETE`, not optional.
- **Concurrency tests:** `pytest` with threading/`transaction.atomic()` simulation (or `pytest-django`'s `TransactionTestCase`) for capacity/PT-balance race conditions (`DEC-020`).

## Required Testing Areas

### Foundation

- authentication
- authorization
- tenant isolation
- branch isolation

### Members

- CRUD
- validation
- duplicate mobile handling
- access restrictions

### Memberships

- lifecycle
- freeze
- renewal
- expiry
- history

### Attendance

- eligibility
- duplicate check-ins
- branch access
- QR
- manual override

### Billing / Payments

- invoices
- partial payments
- payment states
- refunds
- webhook idempotency
- failure handling
- payment history

### Classes

- capacity
- booking
- cancellation
- waitlist
- overlapping booking
- trainer conflicts

### PT

- package balance
- session completion
- cancellation
- concurrency

### Member Portal

- own-data isolation
- role restrictions
- payment access
- booking access
- progress access

### Migration

- validation
- duplicate detection
- import correctness
- error reporting

### Production

- security
- performance
- backup restore
- health checks
- deployment

---

# 41. High-Risk Testing Areas

The following are high-risk and must receive explicit test coverage:

1. Tenant isolation
2. Branch authorization
3. Membership lifecycle
4. Freeze calculations
5. Payment state transitions
6. Razorpay webhook idempotency
7. Refund handling
8. Class-capacity concurrency
9. PT-session concurrency
10. Data migration correctness

These are not considered complete based solely on manual UI verification.

---

# 42. Performance Tracking

Performance must be recorded as implementation progresses.

Baseline targets:

| Area | Target |
|---|---:|
| Standard API | p95 <500ms |
| Dashboard API | p95 <1.5s |
| Check-in backend | <2s |
| Search | <500ms |
| Initial page load | <3s |
| Large reports | Async |

Actual measurements must only be recorded after they are actually tested.

---

# 43. Environment / Deployment State

## Local Development

Status: NOT_STARTED. Approved direction (GYM-003 / `DEC-017`): `docker-compose`
with MySQL, Redis, Django (`runserver`/`gunicorn`), Celery worker, and the Vue
dev server; config via `.env` (gitignored) read by `django-environ`.

## Staging

Status: NOT_STARTED.

## Production

Status: NOT_STARTED.

## AWS — Directional Service Mapping (GYM-003, proposed, not yet provisioned)

This is a **direction**, not a provisioning action — no AWS resources have
been created. Recorded now so implementation has a target; exact instance
sizing/HA configuration remains OQ-009 and must be revisited at Phase 7
(production readiness) against actual load.

| Concern | Proposed AWS Service | Notes |
|---|---|---|
| Django API + Celery workers | ECS Fargate (or EC2 if cost-preferred later) | Containerized, matches "modular Django monolith" baseline — no microservices |
| MySQL | RDS for MySQL | Multi-AZ deferred until justified by actual traffic/SLA needs |
| Redis | ElastiCache for Redis | Celery broker + result backend |
| Vue static SPA | S3 + CloudFront | Matches "separate deployables" decision in `DEC-010` |
| File uploads | S3 (private bucket) | Per `DEC-014` |
| Secrets | AWS Secrets Manager / SSM Parameter Store | Per `DEC-017` |
| Email | SES | Notification channel per §8.9 |
| Load balancing / TLS | ALB + ACM | HTTPS everywhere per §9.3 |
| DNS | Route 53 | `app.<domain>` / `api.<domain>` split per `DEC-010` |

## CI/CD

Status: NOT_STARTED — genuinely open (depends on where the repository is
hosted; no remote configured yet). Not chosen in this pass.

## Monitoring

Status: NOT_STARTED. Observability stack not yet chosen (remains open).

## Backups

Status: NOT_STARTED. Requirements (daily full backup, PITR where supported,
≥30-day retention, monthly restore test) are captured in §9.7/§24.4 — RDS
automated backups + snapshot policy is the natural fit once provisioned, but
this is not yet configured.

## Restore Verification

Status: NOT_STARTED.

---

# 44. External Integrations

| Integration | Purpose | Phase | Provider | Status |
|---|---|---|---|---|
| Razorpay | Payments | MVP | Razorpay | REQUIRED / NOT_STARTED |
| WhatsApp | Notifications | MVP/Should | TBD | OPEN |
| SMS | Notifications | MVP/Should | TBD | OPEN |
| Email | Notifications | MVP | TBD | NOT_STARTED |
| Biometric/RFID | Attendance | MVP adapter / later vendor integration | TBD | OPEN |
| Accounting | Finance integration | Phase 2 | TBD | LATER |

---

# 45. Dependencies

Current core technology baseline from the PRD:

```text
Vue
Django
Django REST Framework
MySQL
AWS
Razorpay
Redis
Background Workers
```

Important rule:

The PRD shows Redis and background workers in the high-level architecture. Exact implementation/dependency choices must be verified and recorded before installation.

No dependency is considered approved merely because it is common.

---

# 46. Prompt / Iteration History

This section stores meaningful AI-assisted development history.

## Iteration ID Convention

```text
GYM-001
GYM-002
GYM-003
...
```

IDs must never be reused.

## Current History

### GYM-001 — Project Context Initialization

**Date:** 2026-09-25

**Type:** Documentation / Project Bootstrap

**Status:** COMPLETE

**Objective:**
Create the initial living project context based on the approved PRD and AI engineering operating rules.

**Application code changed:**
None.

**Database changes:**
None.

**API changes:**
None.

**Frontend changes:**
None.

**Tests:**
None — application implementation has not started.

**Result:**
Initial `PROJECT_CONTEXT.md` established.

**Next:**
Requirements traceability and architecture design.

---

### GYM-002 — Engineering Operating System Verification + Requirement Traceability Completion

**Date:** 2026-09-25

**Type:** Documentation / Project Bootstrap (governance, no application code)

**User task/prompt (verbatim, summarized where noted):**
User instructed, acting as lead architect, to read `PRD.md` → `AGENTS.md` → `PROJECT_CONTEXT.md` and, before writing any application code, establish/verify the project's permanent engineering operating system: a production-grade `AGENTS.md` covering source-of-truth hierarchy, mandatory context loading, automatic development tracking, `GYM-XXX` task IDs, `REQ-XXX` requirement traceability, module tracking, one-task-at-a-time discipline, no-silent-architecture-decisions, backend/multi-tenancy/authorization/financial-safety/concurrency/API/testing/frontend/dependency/database/security/performance/Git/documentation rules, a completion gate, session recovery, no-fabricated-progress, failed-iteration history, and a final task report format — followed by initializing `PROJECT_CONTEXT.md`. Explicitly: no Django features, no Vue features, no business models, no APIs, no silent architecture choices.

**Objective:**
Verify whether the mandated engineering operating system already exists and is production-grade; close any gaps without inventing scope; do not touch application code.

**Requirement IDs affected:** None directly (governance/traceability infrastructure itself). Indirectly all `REQ-001`…`REQ-069` gained IDs/status for the first time in a conforming format.

**Module:** Cross-cutting (project governance) — no product module implemented.

**Findings on session start:**

1. `PRD.md`, `AGENTS.md` (72KB), and `PROJECT_CONTEXT.md` (51KB+) already existed, were non-empty, and were already committed (`ad2b40b — chore: initialize gym management portal`, branch `master`, working tree clean).
2. `AGENTS.md` already satisfied — and in most areas exceeded — every one of the 27 requirements in the user's prompt (source-of-truth hierarchy, mandatory context loading protocol, automatic tracking rules, `GYM-XXX`/`REQ-XXX` ID conventions, the 23-module tracking list, one-task-at-a-time rule, no-silent-decisions rule, Django/DRF layering, multi-tenancy, authorization, financial safety, concurrency, API standards, testing, frontend rules, dependency policy, database policy, security, performance, Git rules, documentation policy, completion gate, session recovery, no-fabricated-progress rule, failed-iteration-history rule, and the final task report format). No rewrite of `AGENTS.md` was needed or performed.
3. `PROJECT_CONTEXT.md` already contained all 25 mandatory sections (and more), a module status table matching the requested 23 modules, an open-questions log, architecture decision log, roadmap, and a prior `GYM-001` iteration record.
4. **Gap found:** `AGENTS.md` §7 mandates requirement IDs in the form `REQ-001, REQ-002, ...`, but `PROJECT_CONTEXT.md` §9.3 actually used the non-conforming prefix `REQ-US-001`…`REQ-US-020`, and covered only the 20 PRD §7 user stories — not the broader functional requirements in PRD §8 (member/attendance/billing/classes/PT/staff/CRM/dashboard/notifications/branch/portal/workout modules) or the non-functional/architectural requirements in PRD §9–§10 (performance, security, tenancy, payment-provider abstraction, biometric adapter, migration).

**Correction (documented per `AGENTS.md` §5.3 / §57, not silently applied):**
Renumbered the 20 existing user-story requirements from `REQ-US-001..020` to `REQ-001..020` (safe: pre-implementation, no code/tests/PRs referenced the old IDs). Extended coverage with `REQ-021..069` for PRD §8 module-level requirements and PRD §9–§10 non-functional/architectural requirements, each with PRD section reference, priority, module, and independent Implementation/Test/Verification status columns (all currently `NOT_STARTED`, matching actual repository state — no fabricated progress).

**Implementation summary:**
Edited `PROJECT_CONTEXT.md` §9 only. No other section, no `AGENTS.md` content, and no application code was changed.

**Files created:** None.

**Files modified:** `PROJECT_CONTEXT.md` (§9 Requirement Traceability rebuilt; this iteration record added to §46; §49/§50/§55/§58 updated to reflect current state — see below).

**Files deleted:** None.

**Database changes:** None.

**API changes:** None.

**Frontend changes:** None.

**Business logic changes:** None.

**Architectural decisions:** None made or changed. All "Decisions Still Required" in §28 remain open and are unaffected by this iteration.

**Dependencies added/removed:** None.

**Tests written:** None (no code exists to test).

**Tests executed:** NOT EXECUTED — no test suite exists yet; nothing to run.

**Test results:** N/A.

**Bugs discovered:** The `REQ-US-*` vs `REQ-*` naming inconsistency described above (documentation defect, not a code bug).

**Failed implementation attempts:** None.

**Security implications:** None — no security-relevant code changed. Documentation now correctly enumerates security-critical requirements (REQ-035 webhook idempotency, REQ-036/REQ-061 no raw card data, REQ-053/REQ-066 tenant/branch isolation, REQ-060 security baseline) so they are traceable going forward.

**Performance implications:** None.

**Migration implications:** None.

**TODO added:** None new; existing §36 Active TODO list remains the accurate backlog.

**Blockers:** None introduced. Pre-existing open questions (§38, OQ-001..OQ-010) remain open and unresolved by this iteration — none were silently resolved.

**Open questions:** None newly raised.

**Git branch:** `master`

**Git commit at start of iteration:** `ad2b40b` (working tree clean)

**Next recommended task:**
Architecture design phase per `AGENTS.md` §11 / §67: finalize authentication mechanism, multi-tenant enforcement strategy, branch-authorization implementation, full Django data model (reviewed for indexes/constraints/audit/concurrency), and API conventions — each recorded as an explicit decision in `PROJECT_CONTEXT.md` §28 before any Django/Vue scaffolding begins. This is analysis/design work, not business-feature implementation.

---

### GYM-003 — Architecture Analysis: Approved Technical Architecture

**Date:** 2026-09-25

**Type:** Architecture / design documentation (no application code, per explicit user instruction — "before application scaffolding")

**User task/prompt (verbatim):**
"Perform architecture analysis and establish the approved technical architecture before application scaffolding." Followed by a handoff checklist instructing a new developer to read `PRD.md` → `AGENTS.md` → `PROJECT_CONTEXT.md`, review current task/open questions/blockers, and continue only from the recorded next task. User was offered a switch to Plan Mode for this collaborative design work and explicitly declined it, signaling a preference to proceed directly.

**Objective:**
Resolve the architecture-level "Decisions Still Required" backlog from `PROJECT_CONTEXT.md` §28 (as it stood after GYM-002) into concrete, documented, reasoned decisions — Django app boundaries, multi-tenancy enforcement, branch-access model, authentication mechanism, authorization implementation, primary-key/identifier strategy, background processing, file storage, API conventions, testing tooling, environment/config strategy, financial-integrity mechanics, audit logging mechanics, and concurrency-control mechanics — and to produce a full schema-level (not code-level) data model for all 20 approved Django apps, per `AGENTS.md` §11/§67's required pre-coding checkpoints.

**Requirement IDs affected:** Traceability updated on REQ-021 through REQ-069 (module/NFR requirements) by association with the modules whose architecture is now designed; no requirement status changed to `COMPLETE` (design ≠ implementation).

**Module:** Cross-cutting — Accounts/Auth, Organizations, Branches, Authorization moved from `NOT_STARTED` to `DESIGNED`; all other business modules gained a `DESIGNED (schema only)` data-model layer without their business-logic/API/frontend layers being started.

**Approach taken:**
Acting with the architect authority the user assigned, I made and documented each decision directly (Decision ID, context, decision, alternatives considered, reason, consequences, risks, affected modules, related requirements — per `AGENTS.md` §84), rather than blocking on interactive approval for every one, since the user had just declined the more collaborative Plan Mode. The one decision flagged most prominently for override is **`DEC-010` (authentication mechanism: JWT with rotating refresh vs. Django session+CSRF)** — classified HIGH-risk per `AGENTS.md` §43, genuinely reversible-with-cost, and explicitly called out in the response for the user's review rather than silently finalized.

**Implementation summary (all in `PROJECT_CONTEXT.md`, no other files touched):**
- §26.1.1 (new): Approved 20-app Django decomposition table with per-app rationale, and explicit list of concepts that are *not* separate apps (Member Portal, Dashboard, Staff) with the `AGENTS.md` clause each decision satisfies.
- §27.A (new): Full schema-level data model for all 20 apps — models, key fields, FK relationships, uniqueness/check constraints, indexes. Marked `DESIGNED`, explicitly not implemented.
- §28: Added `DEC-007` through `DEC-020` (14 new decision records) covering multi-tenancy, branch access, authentication, authorization, PK/identifier strategy, background jobs, file storage, API conventions, testing tooling, environment/config, financial integrity, audit logging, and concurrency control. Trimmed "Decisions Still Required" down to the genuinely open, non-technical items (vendor/provider choices, legal/GST confirmation, freeze-policy default, CI/CD hosting, observability stack, AWS sizing) — none of which were silently resolved.
- §29: Recorded identifier/indexing approach; schema status updated to `DESIGNED`.
- §30: Recorded full API conventions (pagination, filtering, envelope, error schema, idempotency, versioning).
- §35: Updated module status table to reflect `DESIGNED` for foundation modules and `DESIGNED (schema only)` for business modules; Member Portal and Dashboard explicitly noted as intentionally-absent apps.
- §40: Recorded testing tooling decision (`pytest-django` + `factory_boy` + `pytest-cov`, mandatory tenant-isolation test file per app).
- §43: Recorded local-dev approach and a **directional, non-provisioned** AWS service mapping table; explicitly did not provision any actual AWS resources (§48 "no complex AWS architecture without documented reason" — this is planning, not spend).

**Files created:** None.

**Files modified:** `PROJECT_CONTEXT.md` only.

**Files deleted:** None.

**Database changes:** None — schema is designed on paper, no migrations exist, no database was touched.

**API changes:** None — conventions documented, no endpoints exist.

**Frontend changes:** None.

**Business logic changes:** None.

**Architectural decisions:** `DEC-007` through `DEC-020` (see §28 for full detail). All marked `PROPOSED` except where noted; `DEC-010` explicitly flagged for user confirmation before being treated as final.

**Dependencies added/removed:** None installed yet. Named as intended future dependencies (not yet added to any manifest): `djangorestframework`, `djangorestframework-simplejwt`, `django-cors-headers`, `django-filter`, `django-environ`, `django-storages`, `celery`, `redis`, `pytest-django`, `factory_boy`, `pytest-cov`. Actual `requirements.txt`/`pyproject.toml` pinning deferred to the scaffolding task (per `AGENTS.md` §46, dependencies are recorded when actually added, not pre-emptively pinned before a project exists to add them to).

**Tests written:** None (no code exists to test).

**Tests executed:** NOT EXECUTED — nothing to run.

**Test results:** N/A.

**Bugs discovered:** None.

**Failed implementation attempts:** None.

**Corrections:** None required.

**Security implications:** This iteration establishes (but does not yet implement) the tenant-isolation enforcement layering (`DEC-008`), the authorization approach (`DEC-011`), the authentication mechanism (`DEC-010`, flagged), the PK/UUID anti-enumeration strategy (`DEC-012`), and the financial-integrity/webhook-idempotency mechanics (`DEC-018`). No code changed, so no security surface actually changed yet — these are commitments for the next (scaffolding) phase to honor and for tests to verify.

**Performance implications:** Indexing plan recorded per model (§29); `select_for_update()` concurrency approach recorded (`DEC-020`) to avoid the capacity/PT-balance race condition without resorting to unbounded polling/retries.

**Migration implications:** None yet — no migrations exist.

**TODO added:** Confirm or override `DEC-010` (authentication mechanism) before Django scaffolding begins; then proceed to Django/Vue foundation scaffolding per the updated "Immediate sequence" in §54.

**Blockers:** None hard-blocking. `DEC-010` is a soft gate — scaffolding *can* proceed on the proposed JWT approach, but should not be treated as unchangeable/`APPROVED` until the user responds.

**Open questions:** No new ones raised; existing OQ-001..OQ-010 (§38) remain open and are explicitly cross-referenced from the relevant new decisions/models (e.g. `Organization.freeze_policy` schema exists, but which policy is the default remains OQ-005).

**Git branch:** `master`

**Git commit at start of iteration:** `ad2b40b` (with GYM-002's uncommitted `PROJECT_CONTEXT.md` changes on top, still not committed — see §50).

**Next recommended task:**
1. User confirms or overrides `DEC-010` (authentication mechanism).
2. Django project + `core`/`accounts`/`organizations`/`branches` app scaffolding (models, migrations, admin registration) — the first genuine "application code" task, matching `AGENTS.md` §58 Phase 0.
3. Vue project scaffolding (routing shell, auth store, API client) in parallel/afterward.
4. Do not scaffold `payments`/`billing` business logic yet — that is a later, separately-scoped task per the one-task-at-a-time rule.

---

### GYM-004 — Authentication Mechanism Approved (DEC-010)

**Date:** 2026-09-28

**Type:** Decision approval (documentation only, no code)

**User task/prompt (verbatim):** "Jwt" — in direct response to the GYM-003 report's explicit question: "Would you like to confirm the JWT approach in `DEC-010`, or do you want session-based auth instead before I move to scaffolding?"

**Objective:** Record the user's explicit approval of `DEC-010` so it is no longer a soft-gated/`PROPOSED` decision, unblocking Django foundation scaffolding.

**Implementation summary:** Updated `PROJECT_CONTEXT.md` only:
- §28 ADR log: `DEC-010` status → `APPROVED BY USER — 2026-09-28`.
- §28 `DEC-010` detail block: heading and "why flagged" note updated to reflect resolution; design content itself unchanged (approved as originally proposed — access token in memory, rotating refresh token in `httpOnly` cookie, `djangorestframework-simplejwt`).
- Corrected an inconsistent status label on `DEC-008` (previously read "flagged for review" in the ADR table, which overstated it as a blocking question — it was actually presented as an architect decision, not put to the user as a question, unlike `DEC-010`). Corrected to "architect decision" for accuracy. This is a small self-correction, recorded per `AGENTS.md` §57 rather than silently fixed.
- §35, §54, §55, §58: removed "pending confirmation" language for `DEC-010`/authentication; marked Django foundation as the next task.

**Files created:** None. **Files modified:** `PROJECT_CONTEXT.md` only. **Files deleted:** None.

**Database/API/Frontend/business logic changes:** None.

**Architectural decisions:** `DEC-010` status changed from `PROPOSED` to `APPROVED BY USER`. No other decision's status was changed to "approved by user" — `DEC-007`–`DEC-009` and `DEC-011`–`DEC-020` remain `PROPOSED — architect decision` (i.e., decided under delegated architect authority, not individually confirmed by the user, since only `DEC-010` was put to the user as an explicit question). This distinction is intentional and must not be blurred in future updates — do not mark a decision "APPROVED BY USER" without an actual user statement approving it.

**Tests:** None (nothing to test — documentation change only).

**Security implications:** None new — this only finalizes the approval status of an already-documented design.

**Blockers:** None. The soft gate on Django scaffolding is now lifted.

**Git branch:** `master`. **Git commit:** `ad2b40b` unchanged; `PROJECT_CONTEXT.md` still uncommitted (GYM-002+003+004 changes stacked, not committed per standing instruction to only commit when explicitly asked).

**Next recommended task:** Django foundation scaffolding — `core`, `accounts`, `organizations`, `branches` apps (models, migrations, admin, JWT wiring per `DEC-010`) — **to be started on explicit go-ahead**, since it is a new bounded task that creates many files and installs dependencies for the first time.

---

### GYM-005 — Django Foundation Scaffolding (core, accounts, organizations, branches)

**Date:** 2026-09-28

**Type:** Backend implementation (first application code in the repository)

**User task/prompt (verbatim):** "complete tasks in loop and if required run multiple agents" — interpreted, per the standing `AGENTS.md` "Continue" protocol and the already-recorded Next Task, as authorization to proceed through the Phase 0→ roadmap continuously without re-confirming after each bounded task, using parallel subagents for independent chunks of work.

**Objective:** Implement, migrate, and test the Phase 0 Django foundation exactly as decided in `DEC-007`–`DEC-020`: `core` (shared abstractions), `accounts` (custom `User` + JWT auth per `DEC-010`), `organizations` (tenant root), `branches` (branch + access grants per `DEC-009`).

**Requirement IDs affected:** REQ-060 (security baseline), REQ-066 (tenant isolation), REQ-053 (branch isolation) — architecture now has a first real implementation; none of these requirements are `COMPLETE` yet (only the foundation layer exists, no business-feature API surface).

**Module:** Accounts/Auth, Organizations, Branches, Authorization — status moves from `DESIGNED` to `IMPLEMENTING` (backend foundation implemented and tested; no frontend pages consume it yet beyond the parallel Vue foundation task).

**Environment discovery (recorded because it materially shaped the approach):** The sandbox has no system Python pip/venv (`ensurepip` missing, no apt/sudo access) and no Node/npm installed, with no path to install them at the OS level. Docker *is* available and working. Rather than block on missing local tooling, all backend work was done via a `backend/Dockerfile` + `docker-compose.yml`, matching the local-dev approach already approved in `DEC-017`. This turned out to be the right call regardless of the tooling gap — it is the intended dev workflow.

**Host port conflict discovered:** The host already runs unrelated pre-existing Docker containers (`Mysql_Container`/MariaDB on 3306, `Redis_Container` on 6379, `apache_ssl_proxy` on 80/443, and others under an unrelated project). Initial `docker-compose.yml` tried to publish `db`/`redis` on those same host ports and failed. **Corrected** by removing the host-port publication for `db`/`redis` entirely (they only need to be reachable from `backend`/`celery_worker` over the internal compose network, not from the host) — no pre-existing container was stopped, modified, or touched.

**Implementation summary:**
- `backend/Dockerfile`, `backend/requirements.in` (loose spec) + `backend/requirements.txt` (exact pinned versions via `pip freeze` inside the built image, per `AGENTS.md` §46 "pin production dependencies").
- Django project `gymportal` scaffolded via `django-admin startproject`; settings converted into a package (`gymportal/settings/{base,dev,staging,production}.py`) per `DEC-017`. `base.py` wires: `django-environ` config loading, MySQL `DATABASES` from env vars, DRF (`REST_FRAMEWORK` — pagination/filter/exception-handler per `DEC-015`), `SIMPLE_JWT` (15 min access / 7 day rotating+blacklisted refresh per `DEC-010`), CORS (credentials allowed, explicit allow-list per `DEC-010`), Celery/Redis config (`DEC-013`), structured logging.
- `gymportal/celery.py` + `__init__.py` wiring the Celery app (`DEC-013`).
- **`core` app** (no DB table — abstract only): `TimestampedModel`, `TenantScopedModel` (+`TenantScopedQuerySet`/`TenantScopedManager` providing `.for_organization()`/`.for_user()`), `SoftDeleteModel`; `pagination.StandardPageNumberPagination` (envelope `{data, meta}` per `DEC-015`); `exceptions.api_exception_handler` (error envelope `{error: {code, message, field_errors}}`, never leaks internals per `AGENTS.md` §32.2); `permissions.py` (`IsOrgMember`, `HasRole`, `HasBranchAccess`, `TenantScopedViewSetMixin` per `DEC-011`).
- **`organizations` app:** `Organization` (tenant root — deliberately does NOT inherit `TenantScopedModel`, it IS the tenant), `OrganizationSettings` (1:1 split per §27.A). `freeze_policy` field stores the *choice* only; OQ-005 remains open.
- **`branches` app:** `Branch` (tenant-scoped), `BranchAccess` (grant table, unique `(user, branch)`).
- **`accounts` app:** custom `User` (`AbstractBaseUser`+`PermissionsMixin`, `UserManager`), `PasswordResetToken`; `LoginView`/`RefreshView`/`LogoutView`/`MeView` implementing the exact `DEC-010` cookie/body split; `accounts/urls.py` wired at `/api/v1/auth/`.
- Admin registration for all four apps' models.
- `pytest.ini` + `tests/` package per app (`factories.py` via `factory_boy`, `test_models.py`, `test_tenant_isolation.py` for the two genuinely tenant-owned apps — `organizations` is the tenant root so has no isolation test of its own).
- `docker-compose.yml` (db/redis/backend/celery_worker/frontend services), `.env.example`, `.gitignore` (new — none existed before).

**Implementation refinements vs. the architecture-phase design (documented, not silent, per `AGENTS.md` §5.3):**
1. **`accounts.User.email` is globally unique**, not merely per-organization as the original §27.A sketch said — Django's `authenticate()`/`USERNAME_FIELD` machinery assumes one global identity per credential, and no PRD user story describes a "select your gym" login step. `members.Member.phone` per-organization uniqueness (REQ-022) is unaffected.
2. **`accounts.User.organization` is nullable**, but only to allow a platform-level Django superuser (infrastructure/ops account per `AGENTS.md` §8.1, explicitly NOT a new product role) — every real business user is required (via `clean()`) to have both `organization` and (for non-OWNER roles) `home_branch` set.
3. **DEC-008's model-layer enforcement is implemented via explicit `for_organization()`/`for_user()` queryset helpers**, not by disabling `.objects.all()` outright — fully disabling the default manager would also break Django admin/`createsuperuser`/migrations, which need legitimate unscoped access. The *view* layer (`TenantScopedViewSetMixin`) is the actual hard boundary once viewsets exist (Phase 1+); this is recorded as the intended, not weakened, implementation of `DEC-008`.
4. **`BranchAccess.member` (member-side branch-access grants) is deferred to the Phase 1 Members task** — a `ForeignKey("members.Member")` cannot be resolved by Django's migration framework while the `members` app does not yet exist. Phase 0 ships the staff/trainer (`user`) half of the grant table only; the `member` FK + updated constraint will be added via a new migration in GYM-006.

**Files created:** 47 files under `backend/` (full list retained in the GYM-005 shell transcript; see `backend/` directory itself as the authoritative record — `Dockerfile`, `requirements.{in,txt}`, `pytest.ini`, `manage.py`, `gymportal/{__init__,asgi,celery,urls,wsgi}.py`, `gymportal/settings/{__init__,base,dev,staging,production}.py`, and for each of `core`/`accounts`/`organizations`/`branches`: `__init__.py`, `apps.py`, `admin.py`, `models.py`, `views.py`, `migrations/`, `tests/` — plus `accounts/managers.py`, `accounts/serializers.py`, `accounts/urls.py`). Also created at repo root: `docker-compose.yml`, `.env.example`, `.gitignore`.

**Files modified:** None outside `backend/` and the new repo-root files above.

**Files deleted:** Default `tests.py` stubs (replaced by `tests/` packages) in all four apps.

**Database changes:** 4 migrations created and applied against a real MySQL 8.0 container: `organizations.0001_initial`, `accounts.0001_initial`, `accounts.0002_initial`, `branches.0001_initial`. Tables: `organizations_organization`, `organizations_organizationsettings`, `accounts_user`, `accounts_passwordresettoken`, `branches_branch`, `branches_branchaccess`, plus Django/DRF-SimpleJWT built-ins (`auth_*`, `admin_*`, `sessions`, `token_blacklist_*`). Indexes: `(organization, role)` on User, `(organization, status)` on Branch, unique `(user, branch)` on BranchAccess, unique `uuid` on every tenant-scoped model.

**API changes:** First real endpoints — `POST /api/v1/auth/login/`, `POST /api/v1/auth/refresh/`, `POST /api/v1/auth/logout/`, `GET /api/v1/auth/me/`. All conform to `DEC-015` envelopes.

**Frontend changes:** None by this iteration directly (parallel Vue foundation subagent task covers this — see separate report once it completes).

**Business logic changes:** None (foundation only — no Members/Memberships/etc. business rules yet).

**Architectural decisions:** None new; four documented refinements to existing decisions (see above), none of which change `DEC-007`–`DEC-020`'s conclusions.

**Dependencies added:** `Django==5.0.14`, `djangorestframework==3.15.2`, `djangorestframework-simplejwt==5.3.1`, `django-cors-headers==4.4.0`, `django-filter==24.2`, `django-environ==0.11.2`, `django-storages==1.14.6`, `boto3==1.34.162`, `mysqlclient==2.2.8`, `celery==5.4.0`, `redis==5.0.8`, `pytest==8.2.2`, `pytest-django==4.8.0`, `factory-boy==3.3.3`, `pytest-cov==5.0.0` (+ transitive deps) — all previously named as intended in `DEC-013`/`DEC-016`/`DEC-014`/`DEC-010`, now actually installed and pinned in `backend/requirements.txt`.

**Tests written:** 21 tests across 4 apps — `organizations` (model defaults/str, 2 tests), `branches` (grant creation + uniqueness, 2; tenant isolation, 3), `accounts` (model validation/password hashing/global-email-uniqueness, 5; tenant isolation, 2; full JWT auth flow — login/refresh-rotation/logout-blacklist/me/wrong-password/unauthenticated, 7).

**Tests executed:** YES — `docker compose run --rm backend pytest -v` against a real MySQL 8.0 container (not SQLite/mocked).

**Test results:** **21 passed, 0 failed** (after two real bugs found and fixed during this run — see Failed Attempts below). Coverage of the 4 apps' application code: 86% (`core.permissions`/`core.pagination` at 0% since no viewset yet exercises them — expected, they activate in Phase 1).

**Failed attempts / corrections (per `AGENTS.md` §5.3, preserved not erased):**
1. *Attempt:* `python3 -m venv` for a host virtualenv. *Failure:* `ensurepip` not available, no `python3.14-venv` package, no sudo. *Correction:* switched to Docker-based workflow entirely (see Environment discovery above). *Result:* PASS.
2. *Attempt:* `docker compose up db redis` with host ports `3306`/`6379` published, matching a generic docker-compose template. *Failure:* `Bind for 0.0.0.0:6379 failed: port is already allocated` — pre-existing unrelated containers on the host. *Correction:* removed host-port publication for `db`/`redis` (internal-network-only, which is all the app actually needs). *Result:* PASS, and no pre-existing container was touched.
3. *Attempt:* `branches.BranchAccess.member = ForeignKey("members.Member", ...)` as originally designed in §27.A. *Failure:* would have made `makemigrations` unable to resolve the app (doesn't exist yet) — caught before running, not as a runtime error. *Correction:* deferred `member` FK to Phase 1 per the "Phased Schema Note" now in `branches/models.py` and this record. *Result:* N/A (avoided, not a runtime failure).
4. *Attempt:* first `manage.py check` run. *Failure:* `admin.E108` — `BranchAccessAdmin.list_display` still referenced the removed `member` field. *Correction:* updated `list_display`. *Result:* PASS.
5. *Attempt:* first `pytest` run against MySQL. *Failure:* `(1044, "Access denied for user 'gymportal'@'%' to database 'test_gymportal'")` — the MySQL user created by `MYSQL_USER`/`MYSQL_PASSWORD` env vars only has privileges on the named primary database, not the `test_` database pytest-django creates. *Correction:* granted `gymportal` explicit privileges on `test_gymportal.*` only (not `*.*`) via a one-off `docker compose exec db mysql ...` command against this disposable local dev container. *Result:* PASS.
6. *Attempt:* first tenant-isolation test for `accounts.User`. *Failure:* `AttributeError: 'UserManager' object has no attribute 'for_organization'` — the custom auth `UserManager` didn't inherit the tenant-scoping queryset methods. *Correction:* changed `UserManager` to extend `BaseUserManager.from_queryset(core.models.TenantScopedQuerySet)` instead of plain `BaseUserManager`. *Result:* PASS.

**Known issues:** None open. (The `BranchAccess.member` deferral is tracked as planned Phase 1 work, not a bug.)

**Security review:** JWT access token never persisted server-side beyond signing; refresh token only ever travels as `httpOnly`/`SameSite=Lax` cookie scoped to `/api/v1/auth/`, never in a JSON body (verified by `test_login_returns_access_token_and_sets_httponly_refresh_cookie`); refresh rotation + blacklist-on-rotation and blacklist-on-logout both verified by tests (reuse of a blacklisted/rotated token correctly returns 401); wrong-password login returns a generic `401` without revealing whether the email exists; error envelope never leaks stack traces (verified by manual `/admin/` and `/api/v1/auth/me/` smoke test returning clean status codes, not Django's debug error page, with `DEBUG` still on in dev only). Tenant isolation verified by dedicated tests for both `branches` and `accounts` per `AGENTS.md` §16.4.

**Performance review:** Indexes created as designed (`(organization, role)`, `(organization, status)`); no N+1 risk yet since no list endpoints beyond the 4 auth views exist. `StandardPageNumberPagination`/`TenantScopedViewSetMixin` are in place and will apply automatically to every future viewset without per-view boilerplate.

**Migration implications:** First migrations in the project. Rollback = `docker compose run --rm backend python manage.py migrate <app> zero` (not exercised, low risk — no production data exists).

**TODO added:**
- Add `members.Member` FK to `BranchAccess` when the Members app is scaffolded (Phase 1) — tracked here, not forgotten.
- Wire `members`/`memberships`/etc. into `INSTALLED_APPS` as each is scaffolded.

**Blockers:** None.

**Open questions:** None newly raised; OQ-001..OQ-010 unchanged.

**Git branch:** `master`. **Git commit:** `ad2b40b` unchanged (all work in this iteration is uncommitted, per standing instruction to only commit on explicit request) — see §50 for the exhaustive file list.

**Next recommended task:** Phase 1 — `members` app (Member model + admin + tenant-isolation tests), then `memberships` app (MembershipPlan/Membership/MembershipFreeze), plus the deferred `BranchAccess.member` FK migration. Continuing the loop per the user's instruction.

---

### GYM-006 — Phase 1: Members + Memberships Apps

**Date:** 2026-09-28

**Type:** Backend implementation (continuing the GYM-005 loop, same user instruction: "complete tasks in loop and if required run multiple agents")

**Objective:** Implement the `members` app (Member profile, REQ-021..REQ-026) and `memberships` app (MembershipPlan/Membership/MembershipFreeze lifecycle + freeze/renew services, REQ-005/007/020/023/024/025), plus the `BranchAccess.member` FK deferred from GYM-005.

**Requirement IDs affected:** REQ-021 (member profile fields) → IMPLEMENTING. REQ-022 (duplicate phone prevention) → IMPLEMENTING, tested. REQ-023 (status derivation) → PARTIAL/NOT_STARTED (field exists but the actual recomputation-from-membership-state service is not yet wired — recorded as a known gap, not claimed done). REQ-024 (freeze history not deletable by normal staff) → IMPLEMENTING (model/service never deletes; permission-layer enforcement of "normal staff can't delete" still needs a viewset, not yet built). REQ-025 (membership history preserved on renewal) → IMPLEMENTING, tested (`test_renew_preserves_old_membership_row_and_creates_new_one`). REQ-007/REQ-020 (freeze) → IMPLEMENTING, tested.

**Module:** Members → IMPLEMENTING. Memberships → IMPLEMENTING. Branches → the `member`-side grant half of `BranchAccess` completed (was deferred from GYM-005).

**Implementation summary:**
- **`members` app:** `Member(TenantScopedModel, SoftDeleteModel)` with all §27.A fields (identity/contact/fitness/consent/photo), `clean()` validation (assigned trainer must have `role=TRAINER`; `home_branch` must belong to the same organization), unique constraints `(organization, phone)` and `(organization, member_code)` (REQ-022). Registered in `INSTALLED_APPS`. Admin registered with `autocomplete_fields`.
- **`branches` app update:** added the `member` FK to `BranchAccess` (deferred from GYM-005) with the exactly-one-of-`user`-or-`member` `CheckConstraint`, via a new migration (`branches.0002_...`).
- **`memberships` app:** `MembershipPlan`, `Membership` (full `TenantScopedModel`, denormalized `organization` kept in sync with `member.organization` via `clean()`), `MembershipFreeze` (scoped transitively through `membership`, never independently — matches original §27.A sketch). `memberships/services.py`: `apply_freeze()`, `unfreeze_membership()`, `renew_membership()` — all `@transaction.atomic` with `select_for_update()` on the membership row (`DEC-020` concurrency rule).
- Admin registration (`MembershipPlanAdmin`, `MembershipAdmin` with an inline for freeze history).
- Tests: `members` (6 model tests + 3 tenant-isolation tests), `memberships` (4 model tests + 8 service tests + 2 tenant-isolation tests) = 23 new tests.

**⚠️ Freeze-policy caveat (recorded, not silently assumed — OQ-005 remains OPEN):** `memberships/services.py` implements the *arithmetic* for both named policies already present in the `Organization.freeze_policy` schema field (`EXTEND_BY_FREEZE_DAYS`: end_date pushed out by the frozen-day count; `PAUSE_NO_EXTEND`: end_date unchanged). This is a reasonable, documented implementation of what the PRD already describes generically ("system must calculate revised expiry according to configured freeze policy"), and both behaviors are fully tested. **What remains open is which policy should be the *default* for a new organization** — the schema currently defaults to `EXTEND_BY_FREEZE_DAYS`, and this default must not be treated as an approved business decision until OQ-005 is resolved with the user/product owner.

**Known gap (recorded honestly, not hidden):** `Member.status` is a plain field, not yet recomputed automatically from `Membership` state (REQ-023 requires this — "Member.status is DERIVED... do not duplicate membership status logic independently", per `AGENTS.md` §19.2). A `recompute_member_status()` service is the natural next addition once there's a concrete trigger point (membership creation/expiry/freeze/renewal) to call it from — deferred rather than bolted on ad hoc to avoid scattering the derivation logic across multiple call sites before the pattern is settled. Tracked as TODO below, not silently skipped.

**Files created:** `backend/members/{admin,models}.py`, `backend/members/migrations/0001_initial.py`, `backend/members/tests/{__init__,factories,test_models,test_tenant_isolation}.py`; `backend/memberships/{admin,models,services}.py`, `backend/memberships/migrations/{0001_initial,0002_alter_membership_created_by_and_more}.py`, `backend/memberships/tests/{__init__,factories,test_models,test_services,test_tenant_isolation}.py`.

**Files modified:** `backend/gymportal/settings/base.py` (added `members`, `memberships` to `LOCAL_APPS`); `backend/branches/models.py` (added `member` FK + constraint to `BranchAccess`, restored via new migration `branches/migrations/0002_branchaccess_member_alter_branchaccess_user_and_more.py`); `backend/branches/admin.py` (restored `member` to `list_display`); `backend/core/models.py` (added `TenantScopedSoftDeleteQuerySet`/`Manager` — see Failed Attempts); `backend/requirements.{in,txt}` (added `Pillow==10.4.0` for `ImageField`).

**Files deleted:** None.

**Database changes:** 4 new migrations applied against the real MySQL container: `members.0001_initial`, `branches.0002_branchaccess_member_alter_branchaccess_user_and_more`, `memberships.0001_initial`, `memberships.0002_alter_membership_created_by_and_more`. New tables: `members_member`, `memberships_membershipplan`, `memberships_membership`, `memberships_membershipfreeze`. New/changed constraints: unique `(organization, phone)` and `(organization, member_code)` on `Member`; `BranchAccess` gained `member_id` + the exactly-one-of check constraint.

**API changes:** None (no viewsets yet — models + services + admin only, per the phase's actual scope; API surface is a follow-on task).

**Frontend changes:** None.

**Business logic changes:** First real business-rule code in the repo — membership freeze/unfreeze/renewal state machine, all transactional and history-preserving as mandated.

**Architectural decisions:** None new.

**Dependencies added:** `Pillow==10.4.0` (required for `members.Member.photo` `ImageField`; not previously listed as a direct dependency, though implied by `DEC-014` file-upload support — recorded here per `AGENTS.md` §46 dependency policy: reason = Django `ImageField` hard-requires it, verified compatible, no existing dependency covers it).

**Tests written:** 23 new tests (members: 6 model + 3 isolation; memberships: 4 model + 8 service + 2 isolation).

**Tests executed:** YES — `docker compose run --rm backend pytest -v` against the real MySQL container, full suite (all apps).

**Test results:** **44 passed, 0 failed** (project-wide total, up from 21 in GYM-005). Two bugs found and fixed during this run (see below).

**Failed attempts / corrections (preserved per `AGENTS.md` §5.3):**
1. *Attempt:* `Member(TenantScopedModel, SoftDeleteModel)` relying on each parent's own `objects` manager. *Failure:* Django only keeps one `_default_manager` when multiple abstract bases each define one — `SoftDeleteModel.objects` was silently shadowed by `TenantScopedModel.objects`, so `Member.objects.alive()` raised `AttributeError`. Caught by `test_member_soft_delete`, not assumed to work. *Correction:* added `core.models.TenantScopedSoftDeleteQuerySet`/`Manager` combining both mixins' queryset methods, and `Member` now explicitly sets `objects = TenantScopedSoftDeleteManager()`. Documented in both `core/models.py` and this record so the next model that needs both mixins doesn't repeat the mistake. *Result:* PASS.
2. *Attempt:* `MembershipFreeze.requested_by` / `Membership.created_by` as `null=True` only (no `blank=True`), then called `full_clean()` on them from `memberships/services.py` with the field left unset. *Failure:* `ValidationError: {'created_by': ['This field cannot be blank.']}` — Django's `full_clean()`/`clean_fields()` treats `blank` (not `null`) as the "is this field allowed to be empty" signal, independent of the DB-level nullability. *Correction:* added `blank=True` to both fields; regenerated migration `memberships.0002_...`. *Result:* PASS.
3. *(Recorded from before this iteration but only discovered while adding `members`.Member.photo`)* `manage.py check` failed with `fields.E210: Cannot use ImageField because Pillow is not installed`. *Correction:* added `Pillow==10.4.0` to `requirements.in`/`.txt`, rebuilt the backend image, verified the exact resolved version via `pip freeze` before pinning. *Result:* PASS.

**Known issues:**
- `Member.status` derivation from `Membership` state is not yet automatic (see "Known gap" above) — tracked as TODO, not claimed complete.
- No API/viewset layer yet for either app — `core.permissions.TenantScopedViewSetMixin` remains untested by a real endpoint (still 0% coverage on `core/permissions.py` as of this iteration).

**Security review:** Tenant isolation verified for both new apps via dedicated `test_tenant_isolation.py` files (`AGENTS.md` §16.4). `Member.medical_notes` is flagged in-code as sensitive (§37) — no additional field-level encryption implemented yet; access control for it will be enforced once the API/permission layer exists (tracked, not yet a gap since there is no API exposing it yet). Freeze/unfreeze services never hard-delete freeze history (§19.1/§59.4), verified by `test_freeze_history_is_never_deleted_by_unfreeze`.

**Performance review:** Indexes added: `(organization, status)` on `Member`, `(organization, status)` on `MembershipPlan`, `(member, status)` and `(end_date)` on `Membership` (the latter anticipating future expiring-membership dashboard queries, PRD §8.8/REQ-005). `select_for_update()` used in all three freeze/unfreeze/renew services to close the concurrency race window per `DEC-020`, at the cost of a row lock held for the transaction duration — acceptable given these are low-frequency administrative actions, not high-throughput paths.

**Migration implications:** 4 new migrations, all additive (no data loss risk); rollback via `migrate <app> <previous_migration>` untested but low-risk (no production data exists).

**TODO added:**
- Implement `recompute_member_status()` triggered from membership create/expire/freeze/renew, to satisfy REQ-023 fully.
- Build the first real DRF viewsets (`members`, `memberships`) to finally exercise `core.permissions`/`core.pagination` (currently untested by any endpoint).
- Resolve OQ-005 (freeze policy default) with the user before treating either named policy as the production default.

**Blockers:** None.

**Open questions:** None newly raised; OQ-005 explicitly re-flagged as still relevant to this module (see caveat above).

**Git branch:** `master`. **Git commit:** `ad2b40b` unchanged; all work still uncommitted.

**Next recommended task:** Continuing the loop — Phase 2 `attendance` app (check-in, QR, eligibility per REQ-003/004/026..030), per the roadmap in §32.

---

### GYM-007 — Phase 2: Attendance App

**Date:** 2026-09-28

**Type:** Backend implementation (continuing the GYM-005/006 loop, same standing user instruction)

**Objective:** Implement the `attendance` app — check-in eligibility, QR identifier, manual-override path — per REQ-003/004/026..030 and `AGENTS.md` §20.

**Requirement IDs affected:** REQ-027 (multi-method check-in) → IMPLEMENTING, tested for STAFF_SEARCH/QR/MANUAL_OVERRIDE (BIOMETRIC method exists as an enum value; the actual biometric adapter interface is `integrations` app scope, later). REQ-028 (eligibility validation) → IMPLEMENTING, tested (active membership, branch permission, duplicate-checkin). REQ-029 (every check-in records member/branch/timestamp/method) → COMPLETE at the model level (fields exist and are always populated; not yet exposed via API). REQ-030 (manual override audit) → PARTIAL — `recorded_by`/`override_reason` captured on the row itself (baseline auditability), but no `audit.AuditLog` entry yet since that app doesn't exist (same tracked gap as GYM-006).

**Module:** Attendance → IMPLEMENTING.

**Implementation summary:**
- `Attendance(TenantScopedModel)`: member/branch/checkin_at/checkout_at/method/device_id/recorded_by/override_reason, with `clean()` enforcing override_reason+recorded_by are set when `method=MANUAL_OVERRIDE`. Indexes on `(member, checkin_at)` and `(branch, checkin_at)` for the check-in path and future dashboard/trend queries (PRD §8.8).
- `QRToken(TenantScopedModel)`: one-to-one with `Member`, deliberately reuses the base `uuid` field as the scannable QR payload rather than adding a redundant second opaque identifier (see in-code docstring).
- `attendance/services.py::check_in()` — the actual eligibility-checked check-in operation, `@transaction.atomic`:
  - Rejects soft-deleted members outright (`ACCOUNT_BLOCKED`) — even under override.
  - Normal methods (`STAFF_SEARCH`/`QR`/`BIOMETRIC`) check: active membership covering today (`MEMBERSHIP_NOT_ACTIVE`), branch permission via home_branch or `BranchAccess` grant (`BRANCH_NOT_PERMITTED`), and a duplicate-checkin window (`DUPLICATE_CHECKIN`).
  - `MANUAL_OVERRIDE` intentionally bypasses the branch-permission and duplicate-checkin checks (that is the purpose of an override) but requires `override_reason` + `recorded_by` (`OVERRIDE_REQUIRES_REASON`), enforced in the service before any other side effect, not only in `Model.clean()`.
  - Raises `AttendanceEligibilityError` with a machine-readable `.code` for each rejection reason, so a future API layer can surface "clear reason" text per `AGENTS.md` §20.
- Admin registration for both models.
- 8 service tests + 1 tenant-isolation test.

**⚠️ Duplicate-checkin interval caveat (recorded, not silently assumed):** PRD §8.2 leaves the exact duplicate-checkin interval as "configurable rules" without a number. `MIN_CHECKIN_INTERVAL_MINUTES = 120` in `attendance/services.py` is a provisional default chosen only so the eligibility logic is testable end-to-end — it is explicitly documented in-code as not-yet-approved and a candidate for the same per-organization-configurable treatment as `Organization.freeze_policy`. Not silently treated as final.

**Files created:** `backend/attendance/{admin,models,services}.py`, `backend/attendance/migrations/0001_initial.py`, `backend/attendance/tests/{__init__,factories,test_services,test_tenant_isolation}.py`.

**Files modified:** `backend/gymportal/settings/base.py` (added `attendance` to `LOCAL_APPS`).

**Files deleted:** Default `attendance/tests.py` stub.

**Database changes:** 1 migration (`attendance.0001_initial`) applied against the real MySQL container — new tables `attendance_attendance`, `attendance_qrtoken`.

**API changes:** None yet (service layer only, matching this task's actual scope).

**Frontend changes:** None.

**Business logic changes:** First check-in eligibility logic in the repo — performance-sensitive path per `AGENTS.md` §60, kept to simple indexed lookups (no N+1, no full scans) per the in-code performance note.

**Architectural decisions:** None new.

**Dependencies added:** None.

**Tests written:** 9 (8 service + 1 tenant isolation).

**Tests executed:** YES — `docker compose run --rm backend pytest -v`, full project suite.

**Test results:** **53 passed, 0 failed** (project-wide, up from 44). No bugs found this time — first app in this session's loop to pass cleanly without a correction cycle.

**Failed attempts / corrections:** None this iteration.

**Known issues:**
- `AttendanceEligibilityError` is not yet surfaced through an API (no viewset yet) — tracked with the same "build first real viewsets" TODO as GYM-006.
- Manual-override auditability is model-level only until the `audit` app exists (tracked, not hidden).
- `BIOMETRIC` method enum exists but there is no actual biometric/RFID adapter implementation — correctly deferred to the `integrations` app / OQ-003 (vendor still undecided).

**Security review:** Soft-deleted members cannot check in under any method including override (`test_soft_deleted_member_cannot_check_in_even_with_override`) — this is the "ineligible member must not be silently checked in" invariant (`AGENTS.md` §59.11). Branch permission check reuses the same `BranchAccess`/`home_branch` model as `DEC-009`, no duplicated logic. Tenant isolation verified.

**Performance review:** All eligibility checks are indexed lookups; no query executes an unbounded scan. This directly addresses the `AGENTS.md` §20.4/§60 check-in performance sensitivity — full validation, in a transaction, executes in milliseconds against MySQL in local testing (not load-tested; that is a Phase 7 production-readiness task, not claimed here).

**Migration implications:** 1 new additive migration; no rollback risk (no production data).

**TODO added:**
- Make `MIN_CHECKIN_INTERVAL_MINUTES` organization-configurable once product confirms the real rule.
- Wire `audit.AuditLog` calls into `check_in()` for `MANUAL_OVERRIDE` once the `audit` app exists.
- Build the biometric/RFID adapter interface in `integrations` once OQ-003 (vendor) is resolved.

**Blockers:** None.

**Open questions:** None newly raised.

**Git branch:** `master`. **Git commit:** `ad2b40b` unchanged; all work still uncommitted.

**Next recommended task:** Continuing the loop — Phase 3 `billing` + `payments` apps (invoices, Razorpay provider abstraction behind the `integrations` interface, webhook idempotency) per REQ-030..REQ-037/REQ-067.

---

### GYM-008 — Phase 3: Billing + Payments Apps

**Date:** 2026-09-28

**Type:** Backend implementation (continuing the GYM-005/006/007 loop, same standing user instruction: "continue")

**User task/prompt (verbatim):** "continue"

**Objective:** Finish the Phase 3 billing/payments domain layer: invoice uniqueness/totals, payment state machine, cash collection, gateway initiate via provider abstraction, webhook signature + idempotency, refunds that preserve payment history, tenant isolation, migrations, and an executed test run.

**Requirement IDs affected:** REQ-018 → IMPLEMENTING (cash recording service tested, no API). REQ-031 → IMPLEMENTING. REQ-032 → IMPLEMENTING (full status enum; transitions only through `payments.services`). REQ-033 → IMPLEMENTING (`gst_details` remains a JSON snapshot — OQ-004 OPEN). REQ-034 → IMPLEMENTING at model only (`Subscription`; no charge/retry job). REQ-035 → IMPLEMENTING (duplicate webhook tested). REQ-036 / REQ-061 → IMPLEMENTING (no card/CVV columns). REQ-037 → IMPLEMENTING (refund rows; original amount immutable). REQ-006 / REQ-067 → IMPLEMENTING (provider interface + FakePaymentProvider + Razorpay HMAC; real Razorpay HTTPS **NOT EXECUTED**).

**Module:** Billing → IMPLEMENTING. Payments → IMPLEMENTING.

**Change-risk classification:** CRITICAL (payment state, webhook idempotency, refunds, tenant isolation).

**What changed / why / invariants / rollback:**
- Added `billing.Invoice` / `InvoiceLineItem` and `payments.Payment` / `PaymentEvent` / `Refund` / `Subscription`.
- Invariants protected: tenant scope via `TenantScopedModel`; invoice number unique per org; webhook idempotency via unique `gateway_event_id`; refunds never mutate `Payment.amount`; money is `Decimal`.
- Rollback: additive migrations only; no production data.

**Implementation summary:**
- Invoice totals derived from line items (`recompute_totals`). `gst_details` is intentionally unstructured pending OQ-004.
- `InvoiceLineItem.related_pt_package` deferred (same phased-FK pattern as GYM-005/006) because the `pt` app does not exist yet.
- `payments.services`: `record_cash_payment` (optional idempotency key), `initiate_gateway_payment`, `handle_webhook_event` (HMAC then unique event insert; `IntegrityError` → `DuplicateWebhookEvent` with no second side effect), `process_refund`.
- `_recompute_invoice_status` uses **net collected** (credited payment amounts minus processed refunds). An earlier draft counted only `SUCCESSFUL` rows, which would have marked a partially refunded invoice as `ISSUED`. Corrected before the suite was treated as green.
- `PaymentProvider` ABC + `RazorpayProvider` + `FakePaymentProvider`. `verify_webhook_signature` is local HMAC-SHA256 and unit-tested. `create_order` / `process_refund` call Razorpay's HTTPS API and are **NOT EXECUTED** in this environment (no network/creds).
- Admin registration for invoices and payments.

**Files created:** `backend/billing/{models,admin,apps}.py`, `backend/billing/migrations/0001_initial.py`, `backend/billing/tests/{factories,test_models,test_tenant_isolation}.py`, `backend/payments/{models,admin,apps,providers,services}.py`, `backend/payments/migrations/0001_initial.py`, `backend/payments/tests/{factories,test_services,test_tenant_isolation}.py`.

**Files modified:** `backend/gymportal/settings/base.py` (`billing`, `payments` already in `LOCAL_APPS` from the in-progress write), `backend/payments/services.py` (net-paid invoice recompute), `backend/billing/tests/test_models.py` (unique-number factory now keeps member.organization aligned), `PROJECT_CONTEXT.md`.

**Files deleted:** None of substance (default Django view stubs remain unused).

**Database changes:** `billing.0001_initial`, `payments.0001_initial` applied against the compose MySQL service.

**API changes:** None. `billing/views.py` and `payments/views.py` are still Django stubs.

**Frontend changes:** None.

**Tests written:** 4 billing + 14 payments (cash, partial, idempotency, gateway initiate, webhook success, duplicate webhook, invalid signature, Razorpay HMAC, full/partial refund, refund bounds, non-successful refund rejection, invoice status after refund, tenant isolation).

**Tests executed:** YES — `docker compose run --rm backend sh -c 'python manage.py makemigrations billing payments && python manage.py migrate && python manage.py check && pytest -v --tb=short'`

**Test results:** **71 passed, 0 failed.** `System check identified no issues (0 silenced).`

**Failed attempts / corrections:** Invoice status after refund initially ignored net collected (SUCCESSFUL-only). Diagnosed from the refund bookkeeping rule (amount stays on the Payment row) and corrected in `_recompute_invoice_status` with tests for PARTIALLY_PAID and return-to-ISSUED.

**Known issues:**
- No billing/payments HTTP API.
- `Subscription` is a table only — recurring charge/retry not implemented (REQ-034 incomplete).
- Real Razorpay Orders/Refunds API **NOT EXECUTED**.
- `related_pt_package` FK deferred until Phase 4 `pt` app.
- Vue foundation still missing (`frontend/` absent).

**Security review:** Webhook signature verified before any write. Duplicate `gateway_event_id` cannot apply a second financial effect. Tenant isolation tests for Invoice and Payment. No raw card fields. Client-supplied organization IDs are not used in these services (org comes from the invoice/payment row).

**Performance review:** Webhook and cash paths lock a single payment/invoice row (`select_for_update`). No unbounded scans. Not load-tested.

**TODO added:** Recurring billing service; Razorpay sandbox verification; billing/payments viewsets.

**Blockers:** None for this layer. OQ-004 still blocks treating GST JSON keys as legal invoice fields.

**Open questions:** None newly raised. OQ-004 remains OPEN.

**Git branch:** `master`. **Git commit:** `ad2b40b` unchanged; all work still uncommitted.

**Next recommended task:** Vue foundation (Phase 0 leftover — `frontend/` does not exist; compose already declares the service). Then first domain viewsets.

---

### GYM-009 — Phase 0 leftover: Vue foundation (auth shell)

**Date:** 2026-09-28

**Type:** Frontend foundation (continuing the same "continue" loop after GYM-008)

**User task/prompt (verbatim):** "continue"

**Objective:** Scaffold the Vue 3 application that `docker-compose.yml` already declared, with a DEC-010-compliant auth client (access token in memory, refresh via httpOnly cookie).

**Requirement IDs affected:** REQ-060 (security baseline — token storage) → IMPLEMENTING on the frontend side. No business-domain requirements completed.

**Module:** Frontend → IMPLEMENTING.

**Change-risk classification:** HIGH (authentication client; token handling).

**Implementation summary:**
- Vue 3.5 + Vite 5 + Pinia + Vue Router, pinned in `frontend/package.json` + `package-lock.json`.
- `src/api/client.js` talks to `VITE_API_BASE_URL` (`http://localhost:8000/api/v1`), sends `credentials: "include"` so the `gymportal_refresh` cookie (path `/api/v1/auth/`) is attached, unwraps the `{data}` / `{error}` envelope, and retries once after `/auth/refresh/` on 401.
- Access token stored only on `window.__gymportalAccessToken`. Vitest asserts it is not written to `localStorage` / `sessionStorage`.
- Routes: `/login` (public), `/` (requires bootstrap-via-refresh or login). Role helper `canSeeStaffNav` exists for later UX-only nav; no domain menus yet.
- Dockerfile (`node:20-alpine`) for the existing compose `frontend` service.

**Files created:** `frontend/package.json`, `frontend/package-lock.json`, `frontend/vite.config.js`, `frontend/index.html`, `frontend/Dockerfile`, `frontend/.dockerignore`, `frontend/src/{main.js,App.vue,styles.css,api/client.js,api/client.test.js,stores/auth.js,router/index.js,views/LoginView.vue,views/HomeView.vue}`.

**Files modified:** `PROJECT_CONTEXT.md`.

**Database changes:** None.

**API changes:** None.

**Frontend changes:** First Vue application in the repository.

**Tests written:** 1 vitest (`access token memory slot`).

**Tests executed:** YES — `docker compose run --rm frontend sh -c 'npm test && npm run build'`

**Test results:** **1 passed** (vitest). `vite build` succeeded (32 modules). Backend suite not re-run this iteration (unchanged).

**Failed attempts / corrections:** `package-lock.json` was not present inside a `compose run` because the image `npm install` wrote the lock only into the image layer; regenerated onto the mounted volume with `npm install --package-lock-only`.

**Known issues:**
- No domain screens.
- No product-seeded demo user (a local compose user was created only to verify the login path in the browser; that is not a committed seed).
- `npm audit` reported 4 vulnerabilities in the Vite/jsdom tree; not force-upgraded (AGENTS.md §46 — no opportunistic major upgrades).

**Browser verification (2026-09-28):** Login at `http://localhost:5173/login` against a local OWNER succeeded; home showed name/email/role; Sign out returned to `/login`. Logout first 401'd (expired/missing access) then the client refreshed and logout returned 204 — the intended DEC-010 retry path.

**Security review:** Access token never persisted to web storage. Refresh cookie remains httpOnly and path-scoped to `/api/v1/auth/`. Frontend role helper is UX-only.

**Performance review:** Auth client is a single fetch path; no N+1. Production bundle ~94 kB JS gzip 37 kB.

**TODO added:** None new beyond the already-listed first domain viewsets.

**Blockers:** None.

**Git branch:** `master`. **Git commit:** `ad2b40b` unchanged; still uncommitted.

**Next recommended task:** First domain viewsets (members → memberships → attendance → billing/payments), using `TenantScopedViewSetMixin`.

---

### GYM-011 — Phase 4 classes + PT

**2026-09-28**

- Added `classes` (`gym_classes`) and `pt` apps with migrations.
- Capacity-safe booking, overlap, PT consume; waitlist = Booking status; no auto-promote (DEC-021).
- Vue staff Classes book screen. 102 backend tests passing.

## GYM-010 — First domain HTTP APIs + front-desk Vue

**Date:** 2026-09-28

**Type:** Backend API + frontend wiring (standing instruction: "ok complete end to end in a loop")

**User task/prompt (verbatim):** "ok complete end to end in a loop"

**Objective:** Expose tenant-scoped HTTP APIs for members → memberships → attendance → billing → payments, and wire the Vue front-desk path: register → sell membership → collect cash → check in.

**Requirement IDs affected:** REQ-002, REQ-003, REQ-018 → IMPLEMENTING (API + Vue). REQ-031–037 remain IMPLEMENTING (cash/webhook now have HTTP). REQ-035 webhook now has an HTTP endpoint with HMAC + duplicate 200.

**Module:** Members, Memberships, Attendance, Billing, Payments, Branches (read API), Frontend.

**Change-risk classification:** HIGH (authorization, tenant isolation, financial cash recording, webhook).

**Implementation summary:**
- Shared `core/api.py` (`EnvelopeMixin`, UUID lookup, `authorized_branch_ids`).
- Viewsets use organization from `request.user` only. Role scopes: OWNER org-wide; STAFF_ADMIN authorized branches; TRAINER assigned members; MEMBER own rows.
- Staff write (create/update/destroy/check-in/cash/freeze/renew) limited to OWNER + STAFF_ADMIN.
- Member DELETE is soft-delete.
- `POST /payments/webhooks/razorpay/` is `AllowAny`; authenticity is HMAC. Duplicate events return 200 `{data: {duplicate: true}}`.
- Vue: `/members`, `/members/:id` (add plan, sell + cash), `/check-in`.

**Files created:** `backend/core/api.py`, `backend/core/tests/api.py`, serializers/views/urls for members, memberships, attendance, billing, payments, branches; API tests; Vue `AppShell`, `MembersView`, `MemberDetailView`, `CheckInView`, `src/api/domain.js`.

**Files modified:** `backend/gymportal/urls.py`, `backend/gymportal/settings/base.py` (Razorpay env keys), `.env.example`, Vue router/home/styles, `PROJECT_CONTEXT.md`.

**Database changes:** None (no new migrations).

**API changes:** First business-domain HTTP surface (see §30).

**Frontend changes:** Front-desk members/check-in/sell+cash screens.

**Tests written:** 14 API tests.

**Tests executed:** YES — full `pytest -q` and `frontend npm test && npm run build`.

**Test results:** **85 passed, 0 failed** (backend). Vitest 1 passed. `vite build` succeeded.

**Failed attempts / corrections:** Member create 400 because `member_code` was required on the serializer; made optional and auto-generated (`GYM-######`).

**Browser verification:** Login as local OWNER → register Priya Shah → add Monthly plan → sell + cash (`INV-000001` PAID, membership ACTIVE 2026-09-28–2026-10-28) → search/check-in at Main Floor (`POST /attendance/check-in/` 201, UI: "Checked in Priya Shah at Main Floor.").

**Known issues:**
- No member-portal domain screens.
- No classes/PT APIs.
- Real Razorpay order/refund HTTPS still NOT EXECUTED.
- Vue staff-route guard is UX-only; backend remains authoritative.

**Security review:** Tenant isolation tests for members/memberships/payments. Client `organization_id` ignored. Staff branch filter on list/retrieve. Webhook unsigned/invalid rejected via HMAC. Trainer/member cannot write staff actions.

**Performance review:** List endpoints paginated (max 100). Check-in still uses the existing indexed eligibility service. Vue lists unwrap the pagination `data` array.

**TODO added:** None beyond Phase 4 classes/PT.

**Blockers:** None.

**Git branch:** `master`. **Git commit:** `ad2b40b` unchanged; still uncommitted.

**Next recommended task:** Phase 4 classes / personal training (capacity-safe booking, overlap rules, PT balance).

---

### GYM-011 — Phase 4 classes + PT (capacity-safe booking and consume)

**Date:** 2026-09-28

**Type:** Backend domain + API + frontend wiring (standing instruction: "continue")

**User task/prompt (verbatim):** "continue"

**Objective:** Implement Phase 4 class booking and personal-training consumption with tenant isolation, capacity locking, overlap rules, and no invented waitlist auto-promotion.

**Requirement IDs affected:** REQ-038, REQ-039, REQ-040, REQ-041, REQ-042, REQ-043, REQ-044, REQ-045 → IMPLEMENTING / TESTING.

**Module:** Classes, Personal Training, Frontend.

**Change-risk classification:** HIGH (capacity, trainer/member overlap, PT balance).

**Implementation summary:**
- Django apps `classes` (label `gym_classes`) and `pt`.
- `GymClass` / `ClassOccurrence` / `Booking`; waitlist is `Booking.WAITLISTED` (DEC-021).
- `book_occurrence` locks the occurrence (`select_for_update`); capacity vs `effective_capacity`; CLASS_FULL or WAITLISTED; no auto-promote on cancel.
- Shared member/trainer overlap checks in `pt.services` across class + PT holds.
- `PTPackage` / `PTSession`; `complete_session` locks the package and increments `sessions_consumed` once; cancel does not consume (REQ-045 default).
- Read APIs + book/cancel + PT schedule/complete/cancel. Catalog/occurrence writes are not implemented.
- Vue `/classes` staff book-for-member screen.

**Files created:** `backend/classes/**`, `backend/pt/**` (models, services, serializers, views, urls, admin, migrations, factories, tests).

**Files modified:** `backend/gymportal/settings/base.py`, `backend/gymportal/urls.py`, `frontend/src/api/domain.js`, `frontend/src/router/index.js`, `frontend/src/components/AppShell.vue`, `frontend/src/views/ClassesView.vue` (new), `PROJECT_CONTEXT.md`.

**Database changes:** `gym_classes.0001_initial`, `pt.0001_initial` applied on local compose MySQL. Constraints: `gym_class_capacity_positive`, `pt_consumed_lte_purchased`.

**API changes:** `/api/v1/classes/` and `/api/v1/pt/` (see §30).

**Frontend changes:** Staff Classes nav + book flow.

**Tests written:** 17 classes/PT service, isolation, and API tests.

**Tests executed:** YES — full `pytest -q` and `frontend npm test && npm run build`.

**Test results:** **102 passed, 0 failed** (backend). Vitest 1 passed. `vite build` succeeded.

**Failed attempts / corrections:**
- `makemigrations classes` failed because the app label is `gym_classes`.
- Admin E040: `ClassOccurrenceAdmin` needed `search_fields` for Booking autocomplete.
- `test_member_cannot_book_overlapping_sessions` used two overlapping occurrences of the same trainer; first book raised TRAINER_CONFLICT. Test now uses two gym classes with different trainers.

**Browser verification:** Login `owner.verify@example.com` → `/classes` listed seeded Morning Yoga 0/8 → Book for Priya Shah (GYM-000001) → UI “Booked Priya Shah (BOOKED).” and capacity 1/8. Members list still showed Priya Shah ACTIVE.

**Known issues:**
- No staff API/UI to create gym classes or occurrences (seeded via Django shell for browser verify).
- No PT Vue screen (APIs only).
- No threaded last-seat / double-complete concurrency tests yet.
- `billing.InvoiceLineItem.related_pt_package` FK still deferred.
- Waitlist auto-promotion not implemented (intentional).
- MySQL cannot enforce partial unique (occurrence, member) for non-cancelled bookings.

**Security review:** Tenant isolation tests for classes and PT. Book/cancel ignore client organization IDs. TRAINER cannot book/cancel classes. MEMBER books self only. PT schedule/complete/cancel restricted to front desk + trainer (trainer only own clients on schedule).

**Performance review:** Occurrence list annotates `booked_count` (no per-row COUNT). Book path locks one occurrence row. Overlap class query is indexed; PT overlap currently iterates scheduled sessions for the member/trainer (acceptable at V1 scale; revisit if session volume grows).

**TODO added:** Staff class/occurrence write + PT Vue; InvoiceLineItem PT FK; threaded concurrency tests.

**Blockers:** None.

**Decisions:** DEC-021 waitlist-as-booking-status; no auto-promote.

**Git branch:** `master`. **Git commit:** `ad2b40b` unchanged; still uncommitted.

**Next recommended task:** Staff class/occurrence write APIs + PT front-desk Vue (schedule/complete/cancel).

---

### GYM-012 — Staff class/occurrence write + PT front-desk Vue

**Date:** 2026-09-28

**Type:** Backend API + frontend (standing instruction: "complete all task in a loop and continue in loop")

**User task/prompt (verbatim):** "complete all task in a loop and continue in loop"

**Objective:** Let front-desk staff create gym classes and occurrences (with trainer-conflict rejection) and operate PT packages/sessions in Vue.

**Requirement IDs affected:** REQ-038, REQ-041 (occurrence create is the trainer-assignment gate), REQ-042, REQ-043, REQ-044.

**Module:** Classes, Personal Training, Frontend.

**Change-risk classification:** HIGH (trainer conflict at schedule time).

**Implementation summary:**
- `POST /classes/catalog/` and `POST /classes/occurrences/` for OWNER/STAFF_ADMIN.
- `create_occurrence` rejects TRAINER_CONFLICT against existing class/PT holds.
- Occurrence cancel refused while BOOKED rows exist (does not invent cascade-cancel or waitlist promote).
- `GET /classes/trainers/` lists org trainers.
- `POST /pt/packages/` for front desk; existing schedule/complete/cancel.
- Vue Classes: create class, schedule session, book. Vue `/pt`: sell package, schedule, complete, cancel.

**Files created:** `frontend/src/views/PTView.vue`

**Files modified:** `backend/classes/{services,serializers,views,urls}.py`, `backend/pt/{serializers,views}.py`, API tests, `frontend/src/{api/domain.js,router/index.js,components/AppShell.vue,views/ClassesView.vue,views/HomeView.vue}`, `PROJECT_CONTEXT.md`.

**Database changes:** None.

**API changes:** Class/occurrence write + trainers + PT package create (see §30).

**Frontend changes:** Classes create/schedule; new PT screen.

**Tests written:** 4 API tests (class+occurrence create, trainer conflict, member 403, PT package+schedule).

**Tests executed:** YES — full pytest + frontend vitest + vite build.

**Test results:** **106 passed, 0 failed** (backend). Vitest 1 passed. `vite build` succeeded.

**Failed attempts / corrections:** None on this iteration.

**Browser verification:** OWNER created Evening Spin → scheduled 2026-09-29 18:00–19:00 (0/10) → PT sold 10 sessions for Priya Shah → scheduled 2026-09-30 10:00 → Complete → remaining **9 / 10**, status COMPLETED.

**Known issues:**
- Member portal still missing (most members have no linked User login).
- No-show/reschedule PT APIs not implemented.
- Occurrence cancel does not auto-cancel bookings.
- Threaded concurrency tests still pending.

**Security review:** Write actions HasRole OWNER/STAFF_ADMIN. Branch access checked on class/occurrence create. Trainer must be org TRAINER. Member 403 on class create.

**Performance review:** Trainer list is a small org-scoped user query. Occurrence create uses existing overlap helpers.

**TODO added:** Phase 5 member portal.

**Blockers:** None.

**Git branch:** `master`. **Git commit:** `ad2b40b` unchanged; still uncommitted.

**Next recommended task:** Phase 5 member self-service portal (provision MEMBER login + membership/classes/PT/attendance views using existing APIs).

---

### GYM-013 — Member portal login + self-service Vue

**Date:** 2026-09-28

**Type:** Backend API + frontend (same standing loop instruction)

**User task/prompt (verbatim):** "complete all task in a loop and continue in loop"

**Objective:** Let staff provision a MEMBER login and let that member use the same backend APIs from a self-service Vue screen.

**Requirement IDs affected:** REQ-055 → IMPLEMENTING / TESTING.

**Module:** Members, Frontend (Member Portal).

**Change-risk classification:** MEDIUM (new login identity; no new money rules).

**Implementation summary:**
- `provision_member_login` creates a `User(role=MEMBER)` in the member's org/home branch and links `Member.user`.
- `POST /members/{uuid}/provision-login/` front-desk only.
- `GET /members/me/` MEMBER only.
- Vue member detail: Enable portal. Vue `/portal`: membership, invoices, book class as self, attendance, PT.
- Router: `/portal` requires `role === MEMBER`.

**Files created:** `backend/members/services.py`, `frontend/src/views/MemberPortalView.vue`

**Files modified:** `backend/members/{serializers,views}.py`, `backend/members/tests/test_api.py`, Vue router/AppShell/Home/MemberDetail/domain.js, `PROJECT_CONTEXT.md`.

**Database changes:** None (uses existing `Member.user` FK).

**API changes:** `/members/me/`, `/members/{uuid}/provision-login/`.

**Frontend changes:** Portal enable form + `/portal`.

**Tests written:** 1 API test (provision + me).

**Tests executed:** YES — full pytest + frontend vitest + vite build.

**Test results:** **107 passed, 0 failed** (backend). Vitest 1 passed. `vite build` succeeded.

**Failed attempts / corrections:** First MemberSerializer edit accidentally moved `create()` onto `ProvisionLoginSerializer`, causing member create 500 (`organization_id` null). Methods restored onto `MemberSerializer`.

**Browser verification:** Staff member-detail showed Portal login form. Password field fill was blocked by the browser tool policy. Portal login for Priya was provisioned via Django shell (`priya.member@example.com`). `/members/me/` covered by pytest. Interactive MEMBER `/portal` session NOT EXECUTED in the browser.

**Known issues:**
- Workout/progress not started.
- Member cannot request freeze from the portal yet (policy still OQ-005).
- Browser MEMBER login path not exercised.

**Security review:** Provision is front-desk only. Email uniqueness checked. MEMBER `/me` scoped to `user=request.user`. Portal book uses existing MEMBER self-book path (no client member_id).

**Performance review:** Portal loads existing paginated list endpoints.

**TODO added:** Workouts / progress.

**Blockers:** None.

**Git branch:** `master`. **Git commit:** `ad2b40b` unchanged; still uncommitted.

**Next recommended task:** Phase 5 workouts / progress (Program→Day→Exercise, logs, measurements) — do not add AI coaching.

---

### GYM-014 — Workouts, progress, audit, reports, notifications, CRM, import, concurrency

**Date:** 2026-09-28

**Type:** Multi-app backend + Vue surfaces (standing loop; parallel agents authorized; no permission prompts)

**User task/prompt (verbatim):** "create your own plan and todos for all of these and complete all in a loop by running multiple agents at a time , no need to ask for permissions also"

**Objective:** Close the documented pending Phase 5–6 foundation work without inventing waitlist auto-promote, GST, freeze policy, live Razorpay, or AWS.

**Requirement IDs affected:** REQ-001, REQ-004, REQ-008, REQ-010, REQ-011, REQ-013, REQ-038, REQ-043, REQ-044, REQ-048, REQ-049, REQ-051, REQ-052, REQ-055, REQ-056, REQ-057, REQ-069 → IMPLEMENTING / TESTING.

**Module:** Workouts, Progress, Audit, Reports, Notifications, CRM, Data Migration, Classes, PT, Payments, Memberships, Frontend.

**Change-risk classification:** HIGH (concurrency tests, payment notify hooks, import confirm).

**Implementation summary:**
- New Django apps: `workouts`, `progress`, `audit`, `reports` (no tables), `notifications`, `crm`, `data_migration`.
- Leftovers: `InvoiceLineItem.related_pt_package`, `OrganizationSettings.min_checkin_interval_minutes`, PT no-show, member QR payload, staff list, audit hooks on freeze/check-in override/refund.
- Domain `enqueue_notification` via `transaction.on_commit` for MEMBERSHIP_CREATED, PAYMENT_SUCCESSFUL, CLASS_BOOKING, PT_BOOKING, FREEZE_APPROVED (DEC-022). Waitlist and duplicate webhooks do not notify.
- Threaded tests: last-seat class booking; PT double-complete consume-once.
- Vue: Dashboard (OWNER), Workouts (trainer_id required), Progress, Leads, Import (preview then confirm), member QR token, portal workouts/progress.

**Files created:** `backend/{workouts,progress,audit,reports,notifications,crm,data_migration}/**`, `backend/classes/tests/test_concurrency.py`, `backend/pt/tests/test_concurrency.py`, `backend/notifications/tests/test_hooks.py`, Vue `DashboardView`, `WorkoutsView`, `ProgressView`, `LeadsView`, `ImportView`.

**Files modified:** `gymportal/settings/base.py`, `gymportal/urls.py`, `classes/services.py`, `pt/services.py`, `payments/services.py`, `memberships/{services,serializers}.py`, `billing/models.py`, `organizations` settings, Vue router/AppShell/auth/domain/MemberDetail/MemberPortal, `PROJECT_CONTEXT.md`.

**Database changes:** Migrations `workouts.0001`, `progress.0001`, `audit.0001`, `notifications.0001`, `crm.0001`, `data_migration.0001`, `billing.0002`, `organizations.0002`. Applied on local compose MySQL.

**API changes:** `/workouts/`, `/progress/`, `/audit/`, `/reports/dashboard/`, `/notifications/`, `/crm/`, `/data-migration/`, `/members/{uuid}/qr/`, `/pt/sessions/{uuid}/no-show/`, `/auth/staff/`.

**Frontend changes:** Dashboard, Workouts, Progress, Leads, Import; portal workouts/progress/QR; front-desk Import nav (not TRAINER).

**Tests written:** New-app unit/API/tenant-isolation tests; notification hook tests; threaded concurrency tests.

**Tests executed:** YES — `docker compose run --rm backend pytest -q`; `docker compose run --rm frontend sh -c 'npm test && npm run build'`.

**Test results:** **167 passed, 0 failed** (backend). Vitest 1 passed. `vite build` succeeded.

**Failed attempts / corrections:** Wave 1 agents wrote apps before settings/urls were wired (parent wired them). Workouts Vue initially omitted `trainer_id` (OWNER would 400); trainer select added. Parent browser MCP blocked; Import/member-QR were exercised earlier in a child agent session. MEMBER `/portal` interactive session NOT EXECUTED this iteration.

**Known issues:**
- Recurring `Subscription` charge/retry still model-only (REQ-034).
- Real Razorpay HTTPS NOT EXECUTED.
- Reminder/birthday/expiry notifications have no scheduler.
- Waitlist auto-promote remains unimplemented (required).
- AWS / production not started.
- Staff/trainer management UI not built.

**Security review:** New apps use `TenantScopedAPIMixin` + role checks. AuditLog is append-only. Import never inserts unvalidated rows. Dashboard OWNER only. Notification enqueue cannot roll back financial/booking transactions.

**Performance review:** Dashboard aggregates from authoritative tables (no shadow store). Check-in path unchanged except settings lookup. Concurrency uses existing `select_for_update`.

**Decisions:** DEC-022 console/in-app notifications until vendors chosen.

**TODO added:** Staff/trainer directory; Celery reminder jobs; REQ-050 export.

**Blockers:** Live Razorpay needs test-mode keys. Recurring charge needs retry policy. Waitlist promote / GST / freeze-request remain product-open.

**Git branch:** `master`. **Git commit:** `ad2b40b` unchanged; still uncommitted (user did not ask to commit).

**Next recommended task:** Staff/trainer directory (REQ-046) + basic compensation calc only (REQ-047, no payroll), then Celery in-app reminder jobs. Do not invent waitlist auto-promote, GST, freeze policy, or vendor HTTP.

---

### GYM-015 — Staff/trainer directory, compensation calc, reminder jobs, dashboard CSV

**Date:** 2026-09-28

**Type:** Backend + Vue (standing loop; parallel agents; no permission prompts)

**User task/prompt (verbatim):** "create your own plan and todos for all of these and complete all in a loop by running multiple agents at a time , no need to ask for permissions also"

**Objective:** Close the documented Next Task after GYM-014: REQ-046/047 staff directory + read-only compensation, Celery in-app reminders, and REQ-050 CSV. Do not invent payroll, waitlist auto-promote, GST, freeze policy, live Razorpay, or AWS.

**Requirement IDs affected:** REQ-046, REQ-047, REQ-050, REQ-051 → IMPLEMENTING / TESTING.

**Module:** Accounts, Trainers, Notifications, Reports, Frontend.

**Change-risk classification:** HIGH (staff provisioning / activation; money-adjacent compensation display).

**Implementation summary:**
- OWNER POST `/auth/staff/` creates STAFF_ADMIN or TRAINER (never OWNER/MEMBER). Activate/deactivate OWNER-only; cannot deactivate self or OWNER; tenant-scoped 404 across orgs.
- `trainers.TrainerProfile` 1:1 with TRAINER users. Compensation calc is read-only Decimal math. REVENUE_SHARE `computed_amount` is None (revenue base undefined).
- Reminder scans: MEMBERSHIP_EXPIRING (7d), CLASS_REMINDER (24h BOOKED), PT_REMINDER (24h SCHEDULED). Idempotent per org+event+member+resource id. Celery beat schedule + `celery_beat` compose service.
- OWNER `GET /reports/dashboard.csv` from the same `owner_dashboard()` payload. Vue `/staff` + dashboard download.

**Files created:** `backend/trainers/**`, `backend/accounts/tests/test_staff_views.py`, `backend/notifications/tasks.py`, `backend/notifications/tests/test_reminders.py`, `frontend/src/views/StaffView.vue`.

**Files modified:** `accounts/{views,urls,serializers}.py`, `notifications/services.py`, `reports/{views,urls,tests/test_api}.py`, `gymportal/{settings/base,urls}.py`, `docker-compose.yml`, Vue router/AppShell/domain/client/DashboardView, `PROJECT_CONTEXT.md`.

**Database changes:** `trainers.0001_initial` applied on local compose MySQL.

**API changes:** POST `/auth/staff/`, POST `/auth/staff/{uuid}/activate|deactivate/`, `/trainers/` GET/PATCH + `/compensation/`, GET `/reports/dashboard.csv`.

**Frontend changes:** `/staff` front-desk nav; dashboard CSV button.

**Tests written:** staff create/activate isolation; trainer tenant isolation; compensation PER_SESSION/PER_CLASS/REVENUE_SHARE; reminder idempotency; dashboard CSV auth.

**Tests executed:** YES — full pytest + frontend vitest + vite build.

**Test results:** **197 passed, 0 failed** (backend). Vitest 1 passed. `vite build` succeeded.

**Failed attempts / corrections:** Empty JSON lists failed Django `full_clean` (`specializations`/`certifications` cannot be blank). Fixed with `blank=True`. Compensation API now stringifies Decimals.

**Known issues:**
- Birthday and MEMBERSHIP_EXPIRED scans not built.
- REVENUE_SHARE has no computed amount (intentional).
- Recurring charge / live Razorpay / AWS still out of scope.
- Waitlist auto-promote remains unimplemented.
- Browser E2E of `/staff` NOT EXECUTED this iteration.

**Security review:** Staff create is OWNER-only. Org A cannot deactivate org B. Compensation is OWNER-only. Reminder scans stay tenant-scoped via membership/booking/session org.

**Performance review:** Reminder jobs are periodic scans; idempotency uses existing NotificationLog filters. Compensation counts two indexed querysets.

**Decisions:** REVENUE_SHARE does not invent a revenue base. Reminder windows: 7 days / 24 hours (PRD does not specify exact windows; recorded here as implementation defaults, not a new product policy).

**TODO added:** Birthday / MEMBERSHIP_EXPIRED scans.

**Blockers:** Same as GYM-014 for Razorpay keys, recurring-charge policy, waitlist, GST, freeze-request.

**Git branch:** `master`. **Git commit:** `ad2b40b` unchanged; still uncommitted.

**Next recommended task:** Birthday + MEMBERSHIP_EXPIRED in-app scans (remaining REQ-051). Then production-readiness items that do not require AWS keys. Do not invent waitlist auto-promote, GST, freeze policy, or vendor HTTP.

---

### GYM-016 — Birthday/expired scans, health probes, PAYMENT_FAILED, notification UI

**Date:** 2026-09-28

**Type:** Backend + Vue (standing loop; parallel agents; no permission prompts)

**User task/prompt (verbatim):** "create your own plan and todos for all of these and complete all in a loop by running multiple agents at a time , no need to ask for permissions also"

**Objective:** Close documented Next Task after GYM-015: remaining REQ-051 scans plus local production-readiness health checks. Do not invent waitlist auto-promote, GST, freeze policy, live Razorpay, or AWS.

**Requirement IDs affected:** REQ-023, REQ-051, REQ-063 → IMPLEMENTING / TESTING.

**Module:** Memberships, Notifications, Payments, Core, Frontend.

**Change-risk classification:** HIGH (membership status transition ACTIVE→EXPIRED by date).

**Implementation summary:**
- `expire_overdue_memberships` marks ACTIVE rows with `end_date < today` as EXPIRED. FROZEN/CANCELLED untouched.
- `emit_membership_expired_reminders` expires then notifies; idempotent on membership_id.
- `emit_birthday_reminders` matches `Member.dob` month/day only (no Feb 29 fallback); idempotent on `birthday_on`.
- Celery beat entries every 6 hours. IN_APP/console only.
- First FAILED webhook enqueues PAYMENT_FAILED after commit; duplicate event id does not.
- `GET /healthz/` liveness; `GET /readyz/` MySQL+Redis. No secrets on 503.
- Vue `/notifications` for staff and members.

**Files created:** `backend/core/tests/test_health.py`, `frontend/src/views/NotificationsView.vue`.

**Files modified:** `memberships/services.py`, `memberships/tests/test_services.py`, `notifications/{services,tasks,tests/test_reminders,tests/test_hooks}.py`, `payments/services.py`, `core/views.py`, `gymportal/{urls,settings/base}.py`, `docker-compose.yml`, Vue router/AppShell/domain.js, `PROJECT_CONTEXT.md`.

**Database changes:** None.

**API changes:** `GET /healthz/`, `GET /readyz/`.

**Frontend changes:** `/notifications` list.

**Tests written:** expire service; birthday/expired reminder isolation; healthz/readyz; PAYMENT_FAILED webhook hook.

**Tests executed:** YES — full pytest + frontend vitest + vite build.

**Test results:** **208 passed, 0 failed** (backend). Vitest 1 passed. `vite build` succeeded.

**Failed attempts / corrections:** None this iteration.

**Known issues:**
- Member.status is not fully date-derived (only membership.status expire job).
- Recurring charge / live Razorpay / AWS still out of scope.
- Waitlist auto-promote remains unimplemented.
- Staff QR camera scan still not built (REQ-004).

**Security review:** Health probes are unauthenticated and leak no DSNs. Expire job is date-only and skips FROZEN. PAYMENT_FAILED cannot roll back settlement. Notification list is tenant-scoped; TRAINER sees none.

**Performance review:** Expire/birthday scans iterate matching rows; acceptable for V1 scale. Readiness pings Redis with a 2s timeout.

**Decisions:** Feb 29 birthdays notify only on exact month/day. Expire job does not unfreeze.

**TODO added:** Staff QR camera scan.

**Blockers:** Unchanged for Razorpay keys, recurring-charge policy, waitlist, GST, freeze-request, AWS.

**Git branch:** `master`. **Git commit:** `ad2b40b` unchanged; still uncommitted.

**Next recommended task:** Staff QR camera scan for check-in using `gymportal:member:{uuid}` (REQ-004). Do not invent biometric vendor integration.

---

### GYM-017 — QR check-in, expired-members CSV, staff freeze UI

**Date:** 2026-09-28

**Type:** Backend + Vue (standing loop; parallel agents; no permission prompts)

**User task/prompt (verbatim):** "create your own plan and todos for all and complete all in a loop by running multiple agents at a time , no need to ask for permissions also"

**Objective:** Close documented Next Task after GYM-016 (REQ-004 QR check-in) plus two implementable Must leftovers: REQ-015 expired export and REQ-007 staff freeze UI. Do not invent waitlist auto-promote, GST, member freeze-request policy, live Razorpay, or AWS.

**Requirement IDs affected:** REQ-004, REQ-007, REQ-015 → IMPLEMENTING / TESTING.

**Module:** Attendance, Reports, Memberships, Frontend.

**Change-risk classification:** MEDIUM (check-in identifier path; no new money rules).

**Implementation summary:**
- POST `/attendance/check-in/` accepts exactly one of `member_id` or `qr_payload` (`gymportal:member:{uuid}`). QR defaults method to QR. Other-org UUID is 400 without existence leak.
- Check-in Vue: paste token; optional `BarcodeDetector` camera. No new npm packages. No biometric vendor.
- OWNER `GET /reports/expired-members.csv` from stored Membership.status=EXPIRED. Dashboard download button.
- Member detail: Freeze (start/end/reason) and Unfreeze via existing APIs. Expiry math stays on the backend.

**Files created:** None required beyond edits.

**Files modified:** `attendance/serializers.py`, `attendance/tests/test_api.py`, `reports/{services,views,urls,tests/test_api}.py`, `frontend/src/views/{CheckInView,DashboardView,MemberDetailView}.vue`, `frontend/src/api/domain.js`, `PROJECT_CONTEXT.md`.

**Database changes:** None.

**API changes:** `qr_payload` on check-in; `GET /reports/expired-members.csv`.

**Frontend changes:** QR paste/scan; expired CSV; freeze/unfreeze.

**Tests written:** QR payload success/malformed/other-org; expired CSV tenant isolation + 403.

**Tests executed:** YES — full pytest + frontend vitest + vite build.

**Test results:** **213 passed, 0 failed** (backend). Vitest 1 passed. `vite build` succeeded.

**Failed attempts / corrections:** None this iteration.

**Known issues:**
- BarcodeDetector is Chrome/Edge-only; paste always works.
- Staff renew UI not built.
- Member freeze-request still OQ-005.
- Recurring charge / live Razorpay / AWS still out of scope.
- Waitlist auto-promote remains unimplemented.

**Security review:** QR lookup is org-scoped. Expired CSV is OWNER-only. Freeze uses existing front-desk authorization.

**Performance review:** Check-in still a single member lookup by UUID. CSV iterates expired memberships for one org.

**Decisions:** No npm QR library; native BarcodeDetector + paste. Member freeze-request not implemented.

**TODO added:** Staff renew UI.

**Blockers:** Unchanged for Razorpay keys, recurring-charge policy, waitlist, GST, freeze-request, AWS.

**Git branch:** `master`. **Git commit:** `ad2b40b` unchanged; still uncommitted.

**Next recommended task:** Staff renew UI on member detail using existing POST `/memberships/{uuid}/renew/`. Do not invent pricing or GST.

---

### GYM-018 — Close remaining implementable V1 leftovers

**Date:** 2026-09-28

**Type:** Backend + Vue (standing loop; four parallel agents; no permission prompts)

**User task/prompt (verbatim):** "create your own plan and todos for all and complete all in a loop by running multiple agents at a time , no need to ask for permissions also, in  this process complete overall  gym management portal , dont left any tasks for leftovers"

**Objective:** Close every implementable leftover after GYM-017. Mark remaining items DEFERRED/BLOCKED so Active TODO has no leftover coding tasks. Do not invent waitlist auto-promote, GST legal rules, recurring-retry policy, live Razorpay HTTPS, or AWS.

**Requirement IDs affected:** REQ-005, REQ-006, REQ-009, REQ-012, REQ-014, REQ-016, REQ-020, REQ-023, REQ-024, REQ-025, REQ-027, REQ-034, REQ-043, REQ-054, REQ-055, REQ-060, REQ-068 → IMPLEMENTING / TESTING.

**Module:** Memberships, PT, Classes, Reports, Payments, Attendance, Accounts, Frontend.

**Change-risk classification:** HIGH (membership status sync, freeze-request approval, payment initiate). Freeze arithmetic reused `apply_freeze`. Payment initiate uses FakePaymentProvider when Razorpay keys are empty.

**Implementation summary:**
- `sync_member_status` maps latest membership → Member.status; called from freeze/unfreeze/renew/expire/create.
- `FreezeRequest` PENDING until staff approve (calls `apply_freeze`) or reject. No auto-approve. Dates required.
- Staff member detail: Renew (invoice+cash optional; GST skipped if invoice fails), pending request approve/reject, payment history.
- Portal: freeze request, cancel BOOKED/WAITLISTED, payments list, Pay → `POST /payments/initiate/`.
- PT: in-place reschedule (status stays SCHEDULED); Vue Today + datetime-local reschedule.
- Dashboard `revenue.by_branch` including zeros; login `ScopedRateThrottle` 5/min; `AccessControlAdapter` interface + Fake parse_event.
- GET `/payments/subscriptions/` read-only; no charge/retry.

**Files created:** `backend/memberships/migrations/0003_freeze_request.py`, `backend/attendance/adapters.py`, `backend/attendance/tests/test_adapters.py`, `frontend/src/views/SubscriptionsView.vue`.

**Files modified:** memberships `{models,services,serializers,views,urls,admin,tests/*}`; pt `{services,serializers,views,tests}`; payments `{serializers,views,urls,tests}`; reports `{services,serializers,views}`; accounts `{views,tests}`; gymportal/settings/base.py; frontend `{api/domain.js, router, AppShell, HomeView, MemberDetailView, MemberPortalView, PTView, DashboardView}`; `PROJECT_CONTEXT.md`.

**Database changes:** `memberships_freezerequest` table.

**API changes:** freeze-request CRUD-lite; PT reschedule; payments initiate; payments subscriptions list; dashboard `by_branch`.

**Frontend changes:** renew, approve/reject freeze request, portal cancel/pay, PT Today/reschedule, subscriptions page, branch revenue.

**Tests written:** freeze request approve/reject/isolation; sync_member_status; PT reschedule overlap/completed; login 429; adapter parse; subscriptions isolation; member initiate own invoice only.

**Tests executed:** YES — full pytest + frontend vitest + vite build.

**Test results:** **245 passed, 0 failed** (backend). Vitest 1 passed. `vite build` succeeded.

**Failed attempts / corrections:** Parallel agents overlapped on `MemberDetailView` / `domain.js` without conflict markers; parent added staff approve/reject UI and member initiate after agents returned.

**Known issues:**
- Live Razorpay HTTPS still NOT EXECUTED.
- Recurring charge/retry not implemented (policy).
- Waitlist auto-promote remains unimplemented (§23.4).
- GST legal columns still OQ-004.
- AWS not started.
- Browser E2E NOT EXECUTED (host npm unavailable; Docker vitest + build only).

**Security review:** Freeze approve is front-desk only. Member initiate scoped to own invoice. Login throttle is view-scoped. Subscription list org/member scoped. Adapter has no vendor HTTP.

**Performance review:** Dashboard by_branch uses the same month window as monthly_collection. Login throttle uses cache.

**Decisions:** Freeze request is human-approve only. PT reschedule is in-place (no second row). Subscriptions are visibility-only. Payment initiate uses FakePaymentProvider when keys are empty.

**TODO added:** None implementable. Remaining items recorded as Deferred/blocked.

**Blockers:** Unchanged for Razorpay keys, recurring-charge policy, waitlist, GST, WhatsApp/SMS, AWS.

**Git branch:** `master`. **Git commit:** `ad2b40b` unchanged; still uncommitted.

**Next recommended task:** None implementable. Remaining work requires product decisions or credentials. Commit only if the user asks.

---

### GYM-019 — Apex Pulse domain styling

**Date:** 2026-09-28

**Type:** Frontend presentation only (Stitch pack applied; no API/business-rule change)

**User task/prompt (verbatim):** "i have added styling apply styling for every module and complete overall domain styling in a loop" (path: `stitch_pulse_gym_management_platform (1)`)

**Objective:** Apply the Apex Pulse design system from `DESIGN.md` to every Vue module: login, shell, and all staff/owner/member screens.

**Requirement IDs affected:** Presentation only (REQ-055 UX, owner dashboard presentation). No new product rules.

**Module:** Frontend.

**Change-risk classification:** LOW (CSS/layout; same endpoints and forms).

**Implementation summary:**
- Global tokens from Stitch DESIGN.md: canvas `#0B0D10`, lime `#C6FF3D`, Inter + Plus Jakarta Sans.
- AppShell: 260px rail (collapses under 960px), grouped nav, command header.
- Login: split hero using copied gym interior image + glass card.
- PageHeader on every domain view; dashboard KPI cards; status pills via `data-status`.
- No Tailwind CDN, no new npm packages.

**Files created:** `frontend/src/components/PageHeader.vue`, `frontend/public/login-hero.png`.

**Files modified:** `frontend/index.html`, `frontend/src/styles.css`, `AppShell.vue`, `LoginView.vue`, and all domain views (Home, Dashboard, Members, MemberDetail, CheckIn, Classes, PT, Workouts, Progress, Leads, Import, Subscriptions, Staff, Notifications, MemberPortal). `PROJECT_CONTEXT.md`.

**Database changes:** None.

**API changes:** None.

**Frontend changes:** Apex Pulse visual system across all modules.

**Tests written:** None (styling).

**Tests executed:** YES — frontend vitest + vite build. Home, Members, Dashboard opened in browser.

**Test results:** Vitest 1 passed. `vite build` succeeded (50 modules). Browser: login redirected (existing session) to styled Home; Members search/register and Dashboard headings visible. Background `rgb(11, 13, 16)`.

**Failed attempts / corrections:** First login screenshot was empty (session already signed in). Viewport 722px uses stacked rail (intended mobile breakpoint).

**Known issues:** Browser MCP viewport is tablet-width; desktop sidebar shows at ≥960px. Stitch HTML used Tailwind CDN; we ported tokens into project CSS instead.

**Security review:** No auth/tenant change. Login hero is a static public image.

**Performance review:** Google Fonts + one hero image. No new JS dependencies.

**Decisions:** Port Stitch tokens into `styles.css` rather than adding Tailwind. Keep Apex Pulse as visual brand name.

**TODO added:** None.

**Blockers:** Unchanged (Razorpay keys, recurring policy, waitlist, GST, WhatsApp/SMS, AWS).

**Git branch:** `master`. **Git commit:** `ad2b40b` unchanged; still uncommitted.

**Next recommended task:** Product/ops blocked items only. Commit if the user asks.

---

# 47. Prompt Capture Rules

For every meaningful implementation prompt, capture:

- iteration ID
- date
- exact or substantially exact prompt
- objective
- requirement IDs
- module
- submodule
- implementation summary
- files changed
- database changes
- API changes
- frontend changes
- tests
- test results
- security review
- performance review
- decisions
- failed attempts
- corrections
- TODO
- blockers
- next task

Trivial conversational messages do not need to become historical entries.

Examples of meaningful interactions:

- new feature implementation
- schema change
- API change
- architecture change
- security fix
- billing/payment change
- authorization change
- concurrency fix
- migration work
- major refactor
- production configuration
- important bug fix

Examples that normally do not need a full iteration entry:

- asking what a function does
- asking what a library means
- general conceptual questions
- wording changes with no engineering effect

---

# 48. Failed Iteration History

Failed attempts must remain visible.

No implementation history should be rewritten to make the project look cleaner than it actually was.

Example structure:

```text
### GYM-XXX — Initial Attempt

Result:
FAILED

Problem:
...

Impact:
...

Correction:
...

Regression Test:
...

Final Result:
PASS / FAILED / BLOCKED
```

Current failed iterations:

**None.**

---

# 49. Change History

## Initial Project State

**2026-09-25**

- Project context initialized.
- No application code implemented.
- PRD baseline captured.
- V1 scope captured.
- Product requirements captured.
- Technical baseline captured.
- roadmap captured.
- risks/open questions captured.

## GYM-002 — Requirement Traceability Correction

**2026-09-25**

- Verified `AGENTS.md` and `PROJECT_CONTEXT.md` already satisfied the full engineering-operating-system mandate; no `AGENTS.md` rewrite performed.
- Found and corrected a requirement-ID convention defect: renumbered `REQ-US-001..020` → `REQ-001..020`.
- Extended requirement traceability from 20 user-story-only entries to 69 entries (`REQ-001..069`) covering PRD §7 user stories, §8 functional modules, and §9–§10 non-functional/architectural requirements, each with independent implementation/test/verification status.
- No application code, database, API, or frontend changes.
- No architecture decisions made or changed; no open questions resolved.

## GYM-003 — Approved Technical Architecture

**2026-09-25**

- Finalized 20-app Django decomposition (`DEC-007`) with per-app rationale.
- Decided multi-tenancy enforcement strategy: shared DB/schema, mandatory `organization` scoping, layered enforcement (`DEC-008`).
- Decided branch-access model: home branch + `BranchAccess` grants (`DEC-009`).
- **Proposed** authentication mechanism: JWT with rotating refresh (`DEC-010`) — **explicitly flagged for user confirmation, not yet final**.
- Decided authorization implementation, PK/UUID identifier strategy, background processing (Celery/Redis), file storage (S3), API conventions, testing tooling, environment/config strategy, financial-integrity mechanics, audit-logging mechanics, and concurrency-control mechanics (`DEC-011`–`DEC-020`).
- Produced full schema-level data model (models/fields/relationships/constraints/indexes) for all 20 apps — design only, no `models.py` or migrations written.
- Updated module status: Accounts/Auth, Organizations, Branches, Authorization → `DESIGNED`; all other business modules → `DESIGNED (schema only)`.
- No application code, database, API, or frontend changes. No open questions silently resolved — OQ-001..OQ-010 remain open.

## GYM-004 — Authentication Mechanism Approved

**2026-09-28**

- User confirmed `DEC-010` (JWT authentication) in response to the explicit question raised in GYM-003.
- `DEC-010` status updated from `PROPOSED` to `APPROVED BY USER`. Design content unchanged.
- Corrected an inconsistent status label on `DEC-008` ("flagged for review" → "architect decision") — a documentation accuracy fix, not a design change.
- Soft gate on Django foundation scaffolding lifted.
- No application code, database, API, or frontend changes.

## GYM-008 — Billing + Payments Domain Layer

**2026-09-28**

- Implemented `billing` and `payments` models, services, provider abstraction, migrations, and tests.
- Webhook idempotency and refund history immutability covered by executed tests (71 passed project-wide).
- Invoice status after refund derived from net collected, not SUCCESSFUL-only rows.
- No public billing/payments API. Real Razorpay HTTPS not executed.
- Vue still not started.

## GYM-009 — Vue Auth Shell

**2026-09-28**

- Scaffolded Vue 3 + Vite + Pinia + Vue Router under `frontend/`.
- DEC-010 client: in-memory access token, httpOnly refresh cookie, 401→refresh retry.
- Vitest 1 passed; `vite build` succeeded.
- No domain screens. First viewsets remain next.

## GYM-011 — Phase 4 classes + PT

**2026-09-28**

- Added `classes` (`gym_classes`) and `pt` apps with migrations.
- Capacity-safe booking, overlap, PT consume; waitlist = Booking status; no auto-promote (DEC-021).
- Vue staff Classes book screen. 102 backend tests passing.

## GYM-018 — Implementable leftover close-out

**2026-09-28**

- Closed remaining implementable Must leftovers: renew UI, freeze request+approve, portal cancel/pay, PT Today/reschedule, member status sync, branch revenue, login throttle, biometric adapter interface, subscription list, Fake initiate.
- Added `memberships.0003_freeze_request`.
- Full pytest: 245 passed. No leftover implementable Active TODO items.

Future changes must record:

- what changed
- why
- affected modules
- affected requirements
- affected APIs
- affected database
- affected tests
- security implications
- performance implications

---

# 50. Git State

## Current Repository State

```text
Branch: master
HEAD: ad2b40b — "chore: initialize gym management portal" (unchanged)

Working tree: large uncommitted set covering GYM-005..GYM-018
(backend Django apps, Vue frontend, docker-compose, .env.example,
.gitignore, PROJECT_CONTEXT.md). No commit created — commits only when
the user explicitly instructs (AGENTS.md §45.3 / §90.5).
```

The AI must never fabricate Git state.

After each meaningful task, record the actual state.

---

# 51. Active Requirement-to-Module Mapping

| Requirement Area | Primary Module(s) |
|---|---|
| Authentication | Accounts |
| Roles | Authorization |
| Tenant model | Organizations |
| Branch model | Branches |
| Member registration | Members |
| Membership plans | Memberships |
| Membership lifecycle | Memberships |
| Freeze | Memberships |
| Renewal | Memberships |
| Check-in | Attendance |
| QR | Attendance |
| Biometric/RFID adapter | Integrations / Attendance |
| Invoices | Billing |
| Payments | Payments / Billing |
| Razorpay | Payments |
| Recurring billing | Billing / Payments |
| Refunds | Payments / Billing |
| Classes | Classes |
| Booking | Classes |
| Capacity | Classes |
| PT packages | Personal Training |
| PT sessions | Personal Training |
| Trainers | Trainers |
| Staff | Trainers / Accounts |
| Compensation reports | Trainers / Reports |
| Leads | CRM |
| Dashboard | Dashboard |
| Reports | Reports |
| Notifications | Notifications |
| Member portal | Member Portal |
| Workouts | Workouts |
| Progress | Progress |
| Data migration | Migration / Integrations |
| Audit | Audit |
| AWS | Operations |

---

# 52. V1 MoSCoW Baseline

## Must

- Member Management
- Membership Plans / Renewals
- Freeze / Hold
- Attendance
- QR Check-in
- Billing
- Razorpay
- Recurring Billing
- Invoices
- Classes
- Class Booking
- PT
- Trainer Management
- Workout Tracking
- Progress Tracking
- Member Portal
- Multi-Branch
- Owner Dashboard
- Core Reports
- Notifications

## Should

- Biometric/RFID adapter
- Lead CRM
- WhatsApp automation

## Later

- Native mobile
- Accounting integration
- AI coaching
- advanced payroll
- POS / inventory
- advanced platform features

---

# 53. Phase Entry and Exit Rules

## Phase 0 — Foundation

Must define/verify:

- architecture
- authentication design
- authorization design
- tenant design
- branch design
- data model
- API conventions
- testing strategy
- environments
- logging

Do not prematurely implement all business modules.

## Feature Phase Rule

A feature can move from implementation to complete only when:

```text
Requirement understood
        ↓
Business rules known
        ↓
Data model implemented
        ↓
Backend logic implemented
        ↓
Authorization verified
        ↓
API implemented
        ↓
Frontend implemented where required
        ↓
Tests written
        ↓
Tests executed
        ↓
Security reviewed
        ↓
Performance reviewed
        ↓
PROJECT_CONTEXT updated
        ↓
Actual Git state recorded
```

---

# 54. Current Recommended Next Task

## Task

GYM-018 closed every implementable leftover after GYM-017.

There is **no next implementable V1 coding task**. Remaining items are product/ops blocked:

- Recurring charge/retry — DEFERRED (policy)
- Live Razorpay test-mode — BLOCKED (keys)
- Waitlist auto-promote — MUST stay unimplemented until approved
- GST named columns — BLOCKED (OQ-004)
- WhatsApp/SMS vendors — BLOCKED (OQ-001/002)
- AWS / production — NOT STARTED (OQ-009)

Do **not** invent those behaviors. If the user asks to continue without a decision, report this blocked set instead of starting an unrelated module.

### Immediate sequence

```text
1–21. Foundation through GYM-018                         ✅ DONE (GYM-002..018)
22. Recurring billing charge/retry                       DEFERRED (policy)
23. Live Razorpay test-mode                              BLOCKED (keys)
24. AWS / production                                     NOT STARTED
```

---

# 55. Handoff

## Project

Gym Management Portal

## Current Phase

GYM-019 Apex Pulse styling applied to every Vue module. Implementable V1 leftovers remain closed.

## Current Module

None — implementable V1 scope is closed. Remaining items are blocked/deferred.

## Current Task

Do not start waitlist auto-promote, GST, recurring retry, live Razorpay, or AWS without an explicit decision or keys. Optional: commit the uncommitted GYM-005..018 tree when the user asks.

## Last Completed

GYM-018: renew UI, freeze request+approve, portal cancel/pay, PT Today/reschedule, member status sync, branch revenue, login throttle, biometric adapter interface, subscription list, Fake initiate. 245 backend tests.

## Application Code

Django domain + APIs through workouts, progress, audit, reports, notifications, CRM, data_migration, trainers. Vue staff + owner dashboard + member portal + subscriptions.

## Tests

Backend: 245 passed (GYM-018). Frontend: 1 vitest passed + `vite build` succeeded.

## Database

Local compose MySQL including `memberships.0003_freeze_request`. Reports has no tables.

## API

`/api/v1/auth/`, `/branches/`, `/members/`, `/memberships/` (incl. freeze-requests), `/attendance/`, `/billing/`, `/payments/` (incl. initiate + subscriptions), `/classes/`, `/pt/` (incl. reschedule), `/workouts/`, `/progress/`, `/audit/`, `/reports/`, `/notifications/`, `/crm/`, `/data-migration/`, `/trainers/`.

## Frontend

Vue staff Members (renew/approve freeze/payments), Check-in, Classes, PT (Today/reschedule), Workouts, Progress, Leads, Import, Staff, Subscriptions, Notifications; OWNER Dashboard (JSON + CSV + by_branch); MEMBER `/portal` (cancel/pay/freeze-request) + `/notifications`.

## Deployment

Local docker-compose only.

## Current Blockers

None blocking the next staff/trainer task. Deferred/blocked elsewhere: live Razorpay (needs test-mode keys), recurring charge retry policy, waitlist auto-promote (must stay unimplemented), GST legal rules, AWS.

## Open Questions

See Section 38.

## Important Product Priorities

```text
Member
→ Membership
→ Payment
→ Attendance
→ Booking
→ PT
→ Member Self-Service
→ Renewal
→ Retention
```

## Important Engineering Risks

- tenant isolation
- authorization leakage
- membership state correctness
- freeze calculations
- payment/webhook correctness
- class capacity concurrency
- PT package concurrency
- data migration quality
- owner report trust
- production security

## Continue From

**No implementable leftover.** Remaining work is blocked/deferred: live Razorpay keys, recurring-charge policy, waitlist auto-promote, GST legal columns, WhatsApp/SMS vendors, AWS. Do not invent those. Commit the uncommitted GYM-005..018 tree only if the user asks.

---

# 56. Context Recovery Protocol

A new AI session must be able to continue this project by reading:

```text
AGENTS.md
PRD.md
PROJECT_CONTEXT.md
```

The next AI session must determine from this file:

- where the project is
- what has been completed
- what is incomplete
- what changed
- why it changed
- which requirements are affected
- what remains
- what is blocked
- what the next task is

A new session must not assume that previous chat history is available.

---

# 57. Context Integrity Rules

1. Never fabricate implementation status.
2. Never claim tests passed without execution.
3. Never claim deployment without evidence.
4. Never erase failed implementation history.
5. Never silently change product requirements.
6. Never silently resolve open questions that materially affect behavior.
7. Never overwrite an approved decision without recording the new decision.
8. Never mark a feature complete based on UI appearance alone.
9. Never omit security-sensitive changes from the history.
10. Never omit database changes from the history.
11. Never omit payment changes from the history.
12. Never omit tenant/authorization changes from the history.
13. Never delete historical context because it is old.
14. Prefer appending corrections to changing old history.
15. Keep this document synchronized with the actual repository.

---

# 58. Current Overall Status

```text
PROJECT
  ↓
INITIALIZATION
  ↓
PRD BASELINE                      ✅
AGENTS OPERATING CONTRACT         ✅
PROJECT CONTEXT                   ✅
REQUIREMENT TRACEABILITY          ✅
ARCHITECTURE                      ✅ (GYM-003 — DEC-007..DEC-020, all APPROVED)
AUTHENTICATION                    ✅ (DEC-010 — JWT, APPROVED by user GYM-004)
AUTHORIZATION                     ✅ (DEC-011)
TENANT / BRANCH SECURITY          ✅ (DEC-008, DEC-009 — design only, not yet implemented/tested)
DATA MODEL                        ✅ (§27.A — schema design only, no migrations)
API CONTRACT                      ✅ (§30, DEC-015 — conventions only, no endpoints)
DJANGO FOUNDATION                 ✅ (GYM-005)
VUE FOUNDATION                    ✅ (GYM-009)
MEMBERS                           🟡
MEMBERSHIPS                       🟡
ATTENDANCE                        🟡
BILLING                           🟡
PAYMENTS / RAZORPAY               🟡 (fake provider + cash; live HTTPS NOT EXECUTED)
CLASSES                           🟡
PT                                🟡
TRAINERS                          🟡 (GYM-015 directory + calc; no payroll)
WORKOUTS                          🟡 (GYM-014)
PROGRESS                          🟡 (GYM-014)
MEMBER PORTAL                     🟡 (GYM-013/014)
NOTIFICATIONS                     🟡 (GYM-016 all 11 in-app events; vendors open)
DASHBOARD                         🟡 (GYM-014/015)
REPORTS                           🟡 (GYM-015 CSV; no PDF)
CRM                               🟡 (GYM-014 Should)
DATA MIGRATION                    🟡 (GYM-014 members CSV)
SECURITY HARDENING                🟡 (GYM-018 login throttle; AWS HTTPS not started)
PERFORMANCE HARDENING             ⬜
AWS / PRODUCTION                  ⬜ (local healthz/readyz only)
UAT                               ⬜
PRODUCTION                        ⬜
```

Legend:

```text
✅ Established / captured
🟡 Active
⬜ Not started
🔴 Blocked
```

---

# 59. Final Handoff Statement

At this point, implementable V1 leftovers after GYM-018 are **closed**.

The repository has a product baseline, living context, Django/Vue implementation through Phase 6, and 245 passing backend tests. Remaining gaps (live Razorpay, recurring charge, waitlist auto-promote, GST legal columns, WhatsApp/SMS vendors, AWS) are blocked or deferred — they are not leftover coding tasks.

Do not invent those missing product/ops decisions. If asked to continue without them, report the blocked set.

The established path was:

```text
PRD
 ↓
Requirements
 ↓
Architecture
 ↓
Security / Tenancy / Authorization
 ↓
Data Model
 ↓
API Contract
 ↓
Foundation
 ↓
Modules
 ↓
Testing
 ↓
Production
```

Every future meaningful change must update this file according to `AGENTS.md`.
