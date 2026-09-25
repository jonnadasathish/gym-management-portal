# AGENTS.md — Gym Management Portal

> **Status:** Project operating contract
>
> **Product:** Gym Management Portal
>
> **PRD baseline:** `PRD.md` — Version 1.0, dated September 24, 2026
>
> **Purpose:** This file defines how AI coding agents (especially Cursor) must reason about, modify, test, document, and hand off this project.

---

# 1. Purpose and Operating Principle

You are not an autonomous product designer. You are the project's engineering agent operating under an approved Product Requirements Document (PRD), explicit user decisions, existing architecture decisions, and the current project state.

Your job is to:

1. Understand before changing.
2. Preserve approved requirements.
3. Make small, reviewable changes.
4. Verify behavior with tests and evidence.
5. Keep the project state continuously recoverable.
6. Record meaningful prompts, decisions, implementation history, failures, tests, TODOs, blockers, and next steps.
7. Never claim work is complete without evidence.
8. Never invent missing requirements and silently implement them.

The project must remain understandable to another developer who has never seen the previous Cursor conversation.

## Core principle

```text
Understand → Design → Implement → Test → Review → Record → Commit → Continue
```

The project must never depend on hidden chat history as its only source of engineering knowledge.

---

# 2. Mandatory Source-of-Truth Hierarchy

Use the following hierarchy whenever sources conflict:

```text
1. Explicit user-approved requirement or decision in the current project
2. Previously recorded user-approved decision in PROJECT_CONTEXT.md
3. PRD.md
4. Approved architecture/data/API decisions recorded in PROJECT_CONTEXT.md
5. Existing source code and tests as implementation evidence
6. Agent assumptions
```

### 2.1 Current user instruction

A direct user instruction can intentionally change an existing requirement. When it does:

- do not silently overwrite the old requirement;
- record the requirement change in `PROJECT_CONTEXT.md`;
- identify the affected requirement IDs;
- identify affected modules, APIs, database structures, tests, and documentation;
- record whether the change is approved, proposed, or pending clarification.

### 2.2 PRD is the product baseline

`PRD.md` defines what the product is expected to do. Do not replace PRD requirements with general industry assumptions.

### 2.3 Code is not automatically the specification

Because this is a new application, implemented behavior may be incomplete, wrong, or inconsistent with the PRD. Do not conclude that an implementation is correct merely because it already exists.

### 2.4 Never silently resolve conflicts

If two authoritative sources conflict on a material business rule, stop the affected implementation, record the conflict under `Open Questions / Conflicts`, and ask for an explicit decision when required.

Do not guess when the guess could change money, permissions, member eligibility, tenant isolation, scheduling, or stored business data.

---

# 3. Minimal Documentation Model

Keep project memory intentionally simple.

The project uses these core files:

```text
PRD.md
AGENTS.md
PROJECT_CONTEXT.md
```

## 3.1 PRD.md

Contains product requirements and agreed product scope.

Do not rewrite it during implementation unless a user-approved requirement change is being made.

## 3.2 AGENTS.md

Contains the permanent operating rules for AI-assisted engineering.

Do not put temporary task state in this file.

## 3.3 PROJECT_CONTEXT.md

Contains the living state of the project.

This is the persistent memory of implementation work and must contain enough information for a fresh AI session or a new developer to continue safely.

Do not create separate tracking files such as:

```text
progress.md
tracker.md
prompts.md
iterations.md
blockers.md
todo.md
decisions.md
handoff.md
```

unless a future architectural decision explicitly determines that a separate file is necessary.

The default is to keep the project memory centralized in `PROJECT_CONTEXT.md`.

---

# 4. Mandatory PROJECT_CONTEXT.md Sections

If `PROJECT_CONTEXT.md` does not exist, create it before implementation begins.

It must contain, at minimum, these sections:

```markdown
# Gym Management Portal — Project Context

## 1. Current State
## 2. Product Baseline
## 3. Requirement Traceability
## 4. Current Phase
## 5. Current Module
## 6. Current Task
## 7. Completed Work
## 8. Active TODO
## 9. Blockers
## 10. Open Questions / Conflicts
## 11. Architecture Decisions
## 12. Data Model Decisions
## 13. API Decisions
## 14. Security Decisions
## 15. Database / Migration State
## 16. Module Status
## 17. Testing Status
## 18. Environment / Deployment State
## 19. Dependencies
## 20. Known Bugs / Risks
## 21. Prompt / Iteration History
## 22. Change History
## 23. Git State
## 24. Next Task
## 25. Handoff
```

The exact section names may be expanded when needed, but the information must remain discoverable.

---

# 5. Automatic Capture Rule — Mandatory

The agent must automatically maintain `PROJECT_CONTEXT.md` after every meaningful development interaction.

The human should not need to remember to say:

- update progress;
- update TODO;
- log the prompt;
- record the decision;
- record changed files;
- update blockers;
- document tests;
- prepare handoff.

The agent must do this as part of its normal completion workflow.

## 5.1 What must be captured

For every meaningful implementation iteration record:

- iteration ID;
- date/time if available;
- user task/prompt verbatim when practical;
- objective;
- relevant PRD requirement IDs;
- module;
- submodule;
- dependencies;
- preconditions;
- implementation summary;
- files created;
- files modified;
- files deleted;
- database changes;
- migrations;
- indexes/constraints;
- API changes;
- frontend changes;
- business-rule changes;
- architectural decisions;
- security changes;
- performance changes;
- dependencies added/removed;
- tests added;
- tests executed;
- test results;
- failures;
- failed approaches and corrections;
- known issues;
- TODOs;
- blockers;
- open questions;
- approval status where relevant;
- Git branch;
- commit identifier if known;
- next recommended task.

## 5.2 Prompt capture

The important user implementation prompt must be retained in the iteration record.

Do not rewrite the user's requirement in a way that changes its meaning.

A concise summary may accompany the verbatim prompt, but the original task wording should be preserved for meaningful implementation tasks whenever reasonably possible.

## 5.3 Capture failed iterations too

Never delete or rewrite history merely because the first implementation was wrong.

Record failures such as:

```text
Attempt → Failure → Diagnosis → Correction → Verification
```

This is required because future developers need to know not only what works, but what was tried and rejected.

## 5.4 Automatic capture is not optional

If code was changed but project memory was not updated, the task is incomplete.

---

# 6. Iteration IDs

Use sequential project-wide IDs:

```text
GYM-001
GYM-002
GYM-003
...
```

Never reuse an iteration ID.

An iteration represents a meaningful engineering boundary, not every conversational sentence.

## 6.1 What counts as a meaningful iteration

Capture an iteration for:

- architecture work;
- requirement analysis;
- database model changes;
- migrations;
- API changes;
- frontend feature work;
- backend business logic;
- authentication/authorization changes;
- security fixes;
- payment changes;
- concurrency fixes;
- significant refactors;
- dependency changes;
- environment/deployment changes;
- production issues;
- integration work;
- test strategy changes;
- important bug fixes;
- important discoveries;
- decisions that could affect future work.

## 6.2 Trivial conversations

Do not clutter project history with purely conversational questions that do not affect implementation.

Examples that normally do not require an iteration:

- asking what a function means;
- asking for a conceptual explanation;
- asking how Django works in general;
- asking for a command without changing project state.

If the answer changes project architecture or implementation, record it.

---

# 7. Requirement Traceability

Every meaningful PRD requirement must eventually have a stable requirement ID.

Use:

```text
REQ-001
REQ-002
REQ-003
...
```

Requirement IDs must not be reused.

Each requirement record must include:

| Field | Required |
|---|---|
| Requirement ID | Yes |
| PRD reference | Yes |
| Requirement text | Yes |
| Priority | Yes |
| Module | Yes |
| Dependencies | Yes when applicable |
| Implementation status | Yes |
| Test status | Yes |
| Verification status | Yes |
| Notes | When applicable |

## 7.1 Requirement status

Use:

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

## 7.2 Never mark requirements complete casually

A requirement is `COMPLETE` only when its implementation, validation, authorization, tests, documentation, and relevant verification are complete.

---

# 8. Product Baseline From PRD — Do Not Drift

The product is a multi-location gym management SaaS platform for India.

PRD baseline:

- Target market: India
- Target customers: independent gyms and small multi-location gym chains
- Initial scale: approximately 100–500 members/location
- Platform: responsive web portal
- Member functionality is part of the same platform in V1
- Frontend: Vue
- Backend: Python Django
- Database: MySQL
- Cloud: AWS
- Initial delivery target: 8 weeks
- Currency: INR
- Default timezone: IST
- English UI in V1
- Initial payment gateway: Razorpay
- Other gateways must remain replaceable through a provider abstraction
- Native mobile applications are Phase 2
- AI coaching is outside V1

## 8.1 Fixed roles

The PRD defines these roles:

```text
OWNER
STAFF_ADMIN / FRONT_DESK
TRAINER / COACH
MEMBER
```

Do not invent additional business roles as part of normal implementation.

Technical/service accounts may exist if required by infrastructure, but they are not automatically product roles.

## 8.2 Core product flow

The PRD's operational North Star is:

```text
Acquire
  → Register
  → Sell membership
  → Collect payment
  → Check in
  → Schedule
  → Train
  → Track progress
  → Renew
  → Retain
```

The strongest V1 workflow chain is:

```text
Member
  → Membership
  → Attendance
  → Payment
  → Booking
  → PT
  → Member self-service
```

Use this dependency chain when deciding implementation order.

---

# 9. PRD Scope and Priority Rules

## 9.1 V1 Must-have areas

The PRD identifies these as Must-level capabilities:

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
- Personal Training
- Trainer Management
- Workout Tracking
- Progress Tracking
- Member Portal
- Multi-Branch
- Owner Dashboard
- Core Reports
- Notifications

## 9.2 Should areas

- Biometric / RFID adapter
- Lead CRM
- WhatsApp automation
- Other advanced transactional/engagement improvements explicitly marked Should in the PRD

## 9.3 Later areas

- Native mobile application
- Accounting integration
- AI coaching
- Advanced payroll
- POS / inventory
- Other Phase 2/3 capabilities in the PRD

Do not pull later-phase functionality into MVP implementation unless explicitly approved.

## 9.4 Non-goals

Do not silently add:

- full accounting/ERP;
- full payroll processing;
- advanced HR;
- native iOS/Android V1;
- AI workout generation;
- AI personal trainer;
- nutrition/meal planning engine;
- marketplace;
- equipment IoT management;
- franchise royalty management;
- advanced marketing automation;
- video streaming;
- insurance management;
- hardware manufacturing;
- direct universal biometric hardware control;
- international tax compliance;

unless the user explicitly changes scope.

---

# 10. Core Architecture Baseline

The PRD describes this high-level architecture:

```text
Vue Frontend
      ↓ HTTPS
Django Backend / REST API / Auth
      ↓
MySQL
      +
Redis / Background Workers where required
      ↓
External integrations such as:
- Razorpay
- WhatsApp / SMS providers
- Email
- Biometric/RFID adapters
```

Do not introduce microservices merely for architectural fashion.

Start with a modular Django application unless an approved architectural decision explicitly requires otherwise.

## 10.1 Suggested Django domains from the PRD

The PRD names/indicates domains including:

```text
accounts
tenants / organizations
branches
members
memberships
attendance
payments
billing
classes
pt / personal training
trainers
workouts
progress
notifications
reports
crm
integrations
audit
```

The exact Django app decomposition may be adjusted during architecture design, but any structural change must be documented.

---

# 11. First-Run Rule — Do Not Code Immediately

On the first project session, do not start building business features.

Perform these stages first:

```text
1. Read PRD
2. Create/read PROJECT_CONTEXT
3. Extract requirements
4. Establish requirement IDs
5. Identify dependencies
6. Design architecture
7. Design authorization
8. Design authentication
9. Design data model
10. Design API contracts
11. Establish test strategy
12. Only then scaffold application code
```

The first coding task must be foundation work after the design checkpoints are reviewed.

---

# 12. Mandatory Session-Start Protocol

At the beginning of every new meaningful Cursor session:

1. Read `AGENTS.md`.
2. Read `PRD.md`.
3. Read `PROJECT_CONTEXT.md`.
4. Identify current phase.
5. Identify current module.
6. Identify current task.
7. Read relevant architecture decisions.
8. Read relevant requirement records.
9. Read relevant previous iteration entries.
10. Read active TODOs and blockers.
11. Check Git branch and working tree state.
12. Inspect affected code before changing it.

Then report internally/briefly:

```text
Current phase:
Current module:
Current task:
Last completed task:
Relevant requirements:
Dependencies:
Known risks:
Open questions:
Active blockers:
Tests currently known:
Next task:
```

Do not rely on an older chat session to reconstruct state.

---

# 13. Mandatory Task-Start Protocol

Before modifying code for a meaningful task:

## Step 1 — Identify scope

State:

- what will change;
- what will not change;
- which requirement IDs are affected;
- which module(s) are affected;
- dependencies;
- risks.

## Step 2 — Inspect existing implementation

Read the relevant source before making assumptions.

Look at:

- models;
- services;
- serializers;
- views/controllers;
- permissions;
- URLs/routes;
- migrations;
- frontend pages/components;
- API clients;
- tests;
- configuration;
- related modules.

## Step 3 — Determine acceptance criteria

Use PRD acceptance criteria first.

If the PRD does not define sufficient detail, record the missing detail as an open question instead of inventing a hidden business rule.

## Step 4 — Plan the smallest safe change

Prefer one coherent task boundary.

Do not bundle unrelated features merely because they are nearby in the repository.

---

# 14. Task Execution Protocol

For a meaningful feature, follow:

```text
Requirement
   ↓
Business rules
   ↓
Data model
   ↓
Database migration
   ↓
Service / business logic
   ↓
Authorization
   ↓
Tenant / branch enforcement
   ↓
API
   ↓
Frontend
   ↓
Tests
   ↓
Review
   ↓
Context update
```

Not every task requires every layer, but the agent must consciously determine which layers apply.

---

# 15. Backend Engineering Rules — Django

Use Django as the backend framework and Django REST Framework for REST APIs unless an approved architectural decision says otherwise.

## 15.1 Layering

Prefer a clear separation:

```text
HTTP / View / API Layer
        ↓
Application / Service Layer
        ↓
Domain / Business Rules
        ↓
ORM / Persistence
        ↓
MySQL
```

Views should not become large collections of business logic.

Serializers should not secretly become the complete domain/service layer.

Do not create abstractions only to satisfy a pattern. Every abstraction must have a concrete reason.

## 15.2 Business rules

Business truth belongs on the backend.

Do not rely on Vue for authoritative:

- permissions;
- membership state;
- payment state;
- eligibility;
- class capacity;
- PT package balances;
- billing totals;
- tenant boundaries.

## 15.3 Transactions

Use database transactions for operations where partial completion would corrupt business state, especially:

- payment workflows;
- refund workflows;
- membership freeze/unfreeze where multiple records change;
- membership renewal when multiple financial/state records change;
- class booking when capacity is affected;
- class cancellation when capacity/waitlist changes;
- PT session completion/consumption;
- other finite-resource state transitions.

## 15.4 Decimal for money

Never use floating-point arithmetic for currency values.

Use a Decimal-compatible database/application representation.

## 15.5 Date/time

The product baseline is India/IST, but the data model should retain timezone-safe timestamps where the domain requires them.

Do not mix naive and aware datetime handling casually.

Do not change date semantics merely because another implementation style looks cleaner.

---

# 16. Multi-Tenant and Multi-Branch Security Rules

This is one of the highest-risk parts of the system.

The PRD requires multiple gyms/organizations and multiple branches.

## 16.1 Tenant hierarchy

Reason in this shape:

```text
User
  ↓
Organization / Tenant
  ↓
Branch
  ↓
Resource
```

## 16.2 Tenant isolation is mandatory

Every tenant-owned business record must be traceable to an organization/tenant directly or through a controlled relationship.

Every query must enforce tenant scope.

Never trust an organization ID supplied by the client.

Never trust a branch ID supplied by the client simply because it is syntactically valid.

The authenticated user's authorized organization/branch scope must determine access.

## 16.3 Branch authorization

The PRD states:

- Owner can operate across branches;
- Staff default access is assigned-branch only;
- Trainer operates within assigned operational scope;
- Member has a home branch and may have additional branch access if configured.

The implementation must preserve those distinctions.

## 16.4 Tenant-isolation tests

For every tenant-owned domain, include tests proving:

```text
Organization A cannot read Organization B data.
Organization A cannot modify Organization B data.
Branch A staff cannot access unauthorized Branch B records.
A client-provided tenant ID cannot bypass authorization.
```

These are security acceptance criteria, not optional tests.

---

# 17. Authorization Rules

Backend authorization is authoritative.

Frontend role checks are for UX only and must never be relied upon for security.

Use the PRD role-permission matrix as the baseline.

## 17.1 Owner

Full organization-level administrative scope as described by the PRD.

## 17.2 Front Desk/Admin

Operational management permissions appropriate to assigned branch, with restrictions on owner-only settings.

## 17.3 Trainer

Operational access limited to assigned clients/classes/PT sessions and allowed trainer actions.

## 17.4 Member

Own profile, own membership, own payment records, own attendance, own classes/PT, own workout/progress data, subject to configured business policies.

## 17.5 Permission leakage

Do not infer permission from URL visibility.

Do not assume hidden frontend buttons provide protection.

Every protected backend operation must enforce authorization.

## 17.6 Audit sensitive actions

At minimum consider audit logging for:

- manual check-in override;
- membership freeze/unfreeze;
- financial corrections;
- refunds;
- permission/role changes;
- member status changes;
- destructive/administrative operations;
- migration/import operations;
- other sensitive actions discovered during implementation.

---

# 18. Authentication Rules

The exact authentication mechanism must be decided during architecture design and recorded in `PROJECT_CONTEXT.md`.

Regardless of mechanism, the implementation must address:

- credential security;
- secure password storage;
- login;
- logout;
- session/token expiration;
- refresh/re-authentication if applicable;
- password reset/recovery;
- rate limiting / abuse protection where needed;
- organization/branch resolution;
- role resolution;
- inactive/disabled accounts.

Do not invent authentication behavior in scattered views.

Centralize authentication concerns.

---

# 19. Membership Domain Rules

Membership is a core business domain and must be implemented as a stateful lifecycle, not as a collection of unrelated CRUD endpoints.

The PRD requires:

- current membership;
- historical memberships;
- plan;
- start/end dates;
- price;
- discount;
- payment status;
- freeze history;
- renewal history.

## 19.1 Freeze

The PRD requires administrative freeze support with:

- start date;
- end date;
- reason;
- notes;
- history;
- revised expiry according to configured policy.

Membership freeze history must not be silently deleted by normal staff.

The exact freeze calculation policy is configurable and is also an open product question in the PRD. Do not hard-code an unapproved policy when product configuration has not been defined.

## 19.2 Membership state

Do not duplicate membership status logic independently in Vue and Django.

Django owns authoritative status.

Common states may include active/frozen/expired/cancelled as appropriate, but do not add unsupported business states without documenting why they are needed.

## 19.3 Renewal

Renewal must preserve historical membership records.

Do not overwrite historical financial or membership history merely to simplify the current view.

---

# 20. Attendance and Check-in Rules

The PRD supports:

1. staff search by name/mobile/member ID;
2. QR code;
3. biometric/RFID through an adapter layer.

## 20.1 Eligibility

Check-in must validate the PRD requirements, including:

- membership is active;
- branch is permitted;
- account is not blocked;
- duplicate check-in is prevented according to configured rules.

## 20.2 Auditability

Every attendance record must contain enough information to answer:

- who;
- where;
- when;
- how.

The PRD explicitly requires branch, timestamp, member, and method; device ID applies where relevant.

## 20.3 Manual override

Manual override must be auditable.

## 20.4 Performance

Respect both PRD targets:

- check-in interaction target: ≤10 seconds under normal conditions;
- backend processing target: <2 seconds.

Do not add expensive synchronous work to the critical check-in path without justification.

---

# 21. Billing and Payment Rules

Billing and payment code is high risk.

## 21.1 Supported payment concepts

The PRD requires support for:

- one-time payments;
- recurring memberships;
- installments;
- discounts;
- taxes;
- partial payments;
- cash;
- UPI;
- card;
- online gateway payments.

## 21.2 Payment states

The PRD defines:

```text
Pending
Initiated
Successful
Failed
Refunded
Partially Refunded
Cancelled
```

Do not collapse these states merely to simplify code.

## 21.3 Payment provider abstraction

The initial gateway is Razorpay.

The system must keep the payment domain provider-agnostic:

```text
PaymentService
      ↓
PaymentProvider interface
      ↓
RazorpayProvider
```

Future providers may be added without redesigning the core payment data model unless an explicit architecture change is approved.

## 21.4 Webhooks

Webhook processing must be idempotent.

A repeated webhook must not create duplicate payments or duplicate financial side effects.

Verify webhook authenticity according to the provider's supported verification mechanism.

Record provider transaction identifiers and relevant references.

## 21.5 No raw card data

Never store raw card numbers, CVV, or other prohibited payment credentials.

## 21.6 Refunds

Refunds must update financial records through controlled workflows.

Do not mutate historical payment rows in a way that destroys financial auditability.

## 21.7 Financial transactions

Financial changes must be transactional.

Do not permit a state where the database says a payment succeeded but the associated invoice/membership state remains silently inconsistent because the transaction was only partially committed.

## 21.8 Reconciliation

Because the PRD calls out owner trust in reports and payment reconciliation risk, preserve:

- internal payment ID;
- gateway transaction ID;
- timestamps;
- status history where appropriate;
- refund references;
- audit records.

---

# 22. Invoice and GST-Ready Rules

V1 is India-focused and GST-ready.

Invoices should support the PRD's fields such as:

- invoice number;
- gym details;
- GST details where applicable;
- member;
- items;
- discount;
- tax;
- total;
- payment method;
- payment status;
- date.

The exact legal/tax treatment must not be invented by the agent.

The PRD explicitly says GST invoice rules must be confirmed with finance/legal.

Record unresolved tax questions rather than guessing.

---

# 23. Classes and Scheduling Rules

The class domain includes:

- group classes;
- personal training sessions where applicable;
- trainer calendars;
- recurring classes;
- one-off sessions;
- capacity limits;
- waitlists;
- booking;
- cancellation;
- no-show tracking.

## 23.1 Capacity is authoritative on the backend

Never rely on frontend count checks to protect class capacity.

The final capacity decision must be concurrency-safe.

## 23.2 Concurrency

The last available seat is a race-condition boundary.

Test concurrent booking attempts.

Expected invariant:

```text
successful bookings <= configured capacity
```

## 23.3 Overlapping sessions

The PRD requires that a member cannot book overlapping sessions.

Trainers must not be allowed conflicting sessions.

Implement and test these rules at the authoritative backend layer.

## 23.4 Cancellation / waitlist

Cancellation must release capacity and, where waitlist logic is enabled, permit controlled promotion.

Do not silently create automatic promotion behavior if the exact business policy has not been finalized.

---

# 24. Personal Training Rules

PT packages track:

- price;
- purchased sessions;
- consumed sessions;
- remaining sessions;
- expiry;
- assigned trainer.

PT sessions track:

- member;
- trainer;
- date/time;
- duration;
- status;
- notes;
- workout;
- session number.

States from the PRD:

```text
Scheduled
Completed
Cancelled
No-show
Rescheduled
```

## 24.1 Consumption invariant

A completed session decrements the package balance.

A cancelled session does not decrement balance unless a configured gym policy explicitly says it should.

## 24.2 Concurrency

Two simultaneous completion requests must not consume the same PT package balance twice.

Protect the finite session balance with transactional/concurrency-safe logic.

---

# 25. Staff and Trainer Rules

Staff records include:

- name;
- mobile;
- email;
- role;
- branch;
- joining date;
- employment status.

Trainer records additionally include:

- specializations;
- certifications;
- assigned members;
- classes;
- PT sessions;
- compensation model.

V1 supports basic compensation calculations:

- fixed salary;
- per-session amount;
- per-class amount;
- revenue percentage.

Payroll disbursement is explicitly outside V1.

Do not build a payroll system under the trainer compensation requirement.

---

# 26. CRM Rules

Lead CRM is a `Should` capability.

It includes:

- name;
- phone;
- source;
- interested plan;
- branch;
- assigned staff;
- trial date;
- status;
- next follow-up;
- notes.

Pipeline baseline:

```text
New
↓
Contacted
↓
Trial Scheduled
↓
Trial Attended
↓
Proposal
↓
Converted
↓
Lost
```

Do not pull advanced marketing automation into V1 without approval.

---

# 27. Member Portal Rules

V1 member experience is responsive web, not native mobile.

The portal must expose member self-service for the PRD capabilities:

## Membership

- plan;
- expiry;
- freeze request;
- renewal;
- history.

## Payments

- dues;
- invoices;
- payment history.

## Classes

- browse;
- book;
- cancel;
- waitlist where enabled;
- booking history.

## Attendance

- history;
- visit frequency.

## PT

- trainer;
- sessions;
- booking.

## Workout

- assigned plan;
- workout log;
- sets/reps/weight.

## Progress

- weight;
- body measurements;
- progress photos;
- personal bests where implemented.

Member actions must use the same authoritative backend domain logic as staff flows.

Do not duplicate billing or membership logic in a member-specific implementation.

---

# 28. Workout and Progress Rules

The PRD models:

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

Workout tracking includes logs for sets, reps, weight, duration, and notes.

Progress includes:

- body weight;
- BMI where applicable;
- body measurements;
- strength PRs;
- workout completion;
- progress photos.

AI-generated coaching is outside V1.

Do not add AI recommendation logic under the V1 workout requirement.

---

# 29. Notifications Rules

The PRD identifies channels including:

- WhatsApp;
- SMS;
- Email;
- In-app notification.

Core transactional events include:

- membership created;
- payment successful;
- payment failed;
- membership expiring;
- membership expired;
- class booking;
- class reminder;
- PT booking;
- PT reminder;
- birthday;
- freeze approved.

## 29.1 Provider abstraction

External messaging providers should not be hard-coded into business logic.

Use provider/adaptor boundaries where appropriate.

## 29.2 Asynchronous delivery

Large or slow external-notification operations should not block critical user workflows unnecessarily.

Evaluate background processing for the relevant use cases.

## 29.3 Delivery and audit

For important transactional notifications, preserve enough state to diagnose whether the notification was generated, attempted, succeeded, or failed.

---

# 30. Reporting and Dashboard Rules

Owner dashboard requirements come from the PRD.

At minimum, consider:

### Revenue

- today's collection;
- monthly collection;
- pending dues;
- refunds;
- revenue by branch;
- revenue by membership plan.

### Membership

- active;
- expired;
- expiring within 7 days;
- expiring within 30 days;
- new;
- cancelled;
- frozen.

### Attendance

- today's check-ins;
- daily trend;
- monthly trend;
- average visits/member;
- peak hours.

### PT

- sessions;
- completed sessions;
- remaining package sessions;
- PT revenue.

Reports must be derived from authoritative records.

Do not create a second shadow financial calculation path just for the dashboard.

Large reports should follow the PRD's asynchronous-generation expectation where appropriate.

---

# 31. Data Migration Rules

The PRD requires CSV/Excel-based migration capability.

Migration flow:

```text
Upload
 ↓
Validate
 ↓
Preview errors
 ↓
Fix / download error file
 ↓
Confirm
 ↓
Import
 ↓
Import report
```

Never directly insert unvalidated uploaded rows into production business tables.

Migration must account for likely legacy-data problems identified in the PRD:

- duplicates;
- missing phone numbers;
- invalid dates;
- duplicate payments;
- inconsistent membership status.

Migration operations should be auditable.

Do not destroy existing production data during import to “clean it up” unless an explicit migration plan authorizes the operation.

---

# 32. API Rules

Use a versioned API boundary:

```text
/api/v1/
```

Every meaningful endpoint must define:

- HTTP method;
- path;
- authentication requirements;
- authorization requirements;
- organization/branch scope;
- request schema;
- validation rules;
- response schema;
- error behavior;
- side effects;
- transaction boundaries where relevant;
- idempotency behavior where relevant;
- audit behavior where relevant.

## 32.1 API behavior

Do not let frontend assumptions become undocumented API behavior.

If the backend behavior changes, update the API documentation in `PROJECT_CONTEXT.md` or the approved API documentation location.

## 32.2 Error handling

Errors should be consistent, safe, and useful.

Do not leak secrets, stack traces, SQL, internal identifiers, or sensitive data to clients.

---

# 33. Frontend Engineering Rules — Vue

Use Vue for the responsive web portal.

## 33.1 Responsibilities

Frontend handles:

- presentation;
- user interaction;
- local UI state;
- client-side form ergonomics;
- optimistic UX only where safe;
- navigation;
- loading/error states;
- role-aware navigation visibility.

Backend handles:

- authorization;
- business rules;
- financial truth;
- membership truth;
- eligibility;
- tenant isolation;
- class capacity;
- PT balance;
- stored data.

## 33.2 Forms

Frontend validation improves UX but must never replace backend validation.

## 33.3 Member portal

Design mobile-first behavior where appropriate because member use is expected to be heavily mobile-browser oriented.

## 33.4 Front desk UX

The PRD explicitly prioritizes:

1. check-in;
2. member lookup;
3. payment collection;
4. renewal;
5. class booking;
6. member registration.

Do not make these workflows unnecessarily deep or click-heavy.

---

# 34. Database Rules — MySQL

Use MySQL as the primary relational database.

## 34.1 Schema changes

Every schema change must be deliberate and migrated.

Before changing a table/column/constraint:

1. identify consumers;
2. identify queries;
3. identify API effects;
4. identify data backfill needs;
5. identify rollback considerations;
6. test migration behavior.

## 34.2 Constraints

Use database constraints when they represent true invariants, especially for:

- uniqueness;
- foreign-key integrity;
- valid relationships;
- tenant scoping where appropriate;
- non-negative finite balances where the DB can safely enforce them.

## 34.3 Indexes

Add indexes based on actual query patterns.

At minimum evaluate indexes for frequent filters and joins involving:

- organization/tenant;
- branch;
- member identifiers;
- membership dates/status;
- attendance timestamps;
- class schedule times;
- booking uniqueness;
- payment status/reference IDs.

Do not create every possible index blindly.

## 34.4 Financial history

Do not hard-delete financial records merely to simplify application logic.

Use explicit state transitions, refunds, reversals, or correction records where appropriate.

---

# 35. Performance Rules

The PRD targets are:

| Metric | Target |
|---|---:|
| Standard API p95 | <500ms |
| Dashboard API p95 | <1.5s |
| Check-in backend processing | <2s |
| Initial page load | <3s on standard broadband |
| Search | <500ms |

## 35.1 Performance review checklist

Before declaring a high-traffic feature complete, inspect:

- N+1 queries;
- unnecessary serialization;
- unbounded queries;
- pagination;
- database indexes;
- repeated frontend requests;
- redundant calculations;
- synchronous third-party calls;
- expensive dashboard aggregation;
- large report generation.

Do not optimize through guesswork. Measure or reason from query/access patterns and record important performance decisions.

---

# 36. Security Rules

Security is part of every feature.

The PRD requires protection against:

- unauthorized access;
- tenant leakage;
- CSRF issues where applicable;
- XSS;
- SQL injection;
- unsafe file uploads;
- exposed secrets;
- abuse/rate attacks;
- unsafe payment handling.

## 36.1 Secrets

Never hard-code:

- API keys;
- passwords;
- gateway secrets;
- database credentials;
- cloud credentials;
- JWT/session secrets;
- encryption keys.

Use environment/secret management mechanisms appropriate to the environment.

## 36.2 Logging

Never log:

- passwords;
- raw payment credentials;
- secrets;
- access tokens;
- unnecessary personal data.

## 36.3 File uploads

If implementing profile photos, progress photos, imports, or other uploads:

- validate file type;
- validate file size;
- generate safe storage names;
- prevent executable content from being served unsafely;
- validate authorization to access files;
- avoid trusting the client-provided filename.

---

# 37. Personal Data Rules

The PRD identifies sensitive operational/member information such as:

- name;
- phone;
- email;
- address;
- emergency contact;
- fitness/medical notes;
- attendance;
- payment information;
- progress data;
- photos.

Treat these as sensitive business data.

The implementation should support appropriate consent, data-access/deletion workflows, and security controls applicable to India's Digital Personal Data Protection framework, while recognizing that exact legal/tax requirements may require finance/legal review.

Do not invent legal policy text as if it were confirmed legal advice.

Record legal/compliance unknowns as open questions.

---

# 38. Audit Logging Rules

Audit logging is a platform capability, not merely a debugging log.

An audit event should answer, where relevant:

```text
Who performed the action?
What organization/branch?
What resource?
What action?
When?
What changed?
Was it system or user initiated?
```

Prioritize auditability for:

- financial operations;
- refunds;
- membership freeze/unfreeze;
- manual overrides;
- permission changes;
- sensitive profile changes;
- imports/migrations;
- administrative changes.

Do not expose internal audit events to members unless a specific product requirement supports that view.

---

# 39. Background Processing Rules

Redis/Celery/background workers are optional infrastructure and must be introduced for a concrete use case.

Good candidates include:

- large report generation;
- notifications;
- retryable external integrations;
- scheduled expiry reminders;
- reconciliation jobs;
- imports where asynchronous processing is required.

Do not move simple request/response logic into background processing solely to appear scalable.

When using jobs:

- make them idempotent where possible;
- define retry behavior;
- avoid duplicate financial side effects;
- log failures;
- expose operational visibility.

---

# 40. External Integration Rules

Treat external systems behind explicit boundaries.

Known integrations include:

- Razorpay;
- WhatsApp/SMS providers;
- email provider;
- biometric/RFID device/vendor adapters;
- future accounting or other services only when approved.

Do not couple core domain logic directly to vendor-specific request/response formats.

Use adapters/services/interfaces where the boundary is genuinely useful.

---

# 41. Testing Rules

Testing is part of implementation, not a final cleanup phase.

## 41.1 Minimum testing expectations

Test according to risk:

- unit tests;
- service/business-rule tests;
- API tests;
- authorization tests;
- tenant-isolation tests;
- database/integration tests;
- frontend tests where business behavior is present;
- concurrency tests for race-prone domains;
- end-to-end tests for critical user journeys.

## 41.2 High-risk mandatory coverage

The following areas require explicit regression coverage:

- tenant isolation;
- authorization;
- membership lifecycle;
- membership freeze;
- renewal;
- attendance eligibility;
- duplicate check-in prevention;
- class capacity;
- overlapping class booking;
- PT balance consumption;
- payment status transitions;
- payment webhook idempotency;
- refunds;
- migration import validation.

## 41.3 Test claims

Never say “tests pass” unless tests were actually run and the result is known.

If tests cannot be run, state:

```text
NOT EXECUTED
```

and explain why.

## 41.4 Regression behavior

When fixing a bug, first add or identify a regression test when practical, then implement the fix.

---

# 42. Acceptance and Definition of Done

A meaningful module or feature is not `COMPLETE` just because code exists.

A feature is complete only when applicable criteria below are satisfied:

```text
[ ] PRD requirement mapped
[ ] Business rules identified
[ ] Data model implemented
[ ] Database migration created
[ ] Backend business logic implemented
[ ] Authentication considered
[ ] Authorization implemented
[ ] Tenant isolation verified
[ ] Branch access verified where applicable
[ ] API implemented
[ ] Validation implemented
[ ] Frontend implemented where applicable
[ ] Tests written
[ ] Tests executed
[ ] Relevant concurrency risks tested
[ ] Security reviewed
[ ] Performance reviewed
[ ] API/behavior documentation updated
[ ] Project context updated
[ ] TODO updated
[ ] Blockers updated
[ ] Next task recorded
```

Not every checkbox applies to every task; the agent must state which are not applicable rather than silently ignoring them.

---

# 43. Change-Risk Classification

Classify meaningful changes as:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

## LOW

Examples:

- copy changes;
- simple visual fixes;
- safe refactors with strong test coverage.

## MEDIUM

Examples:

- API changes;
- schema additions;
- new frontend workflows;
- non-critical integration changes.

## HIGH

Examples:

- authentication;
- authorization;
- membership lifecycle;
- billing;
- class capacity;
- PT consumption;
- migration logic;
- production configuration.

## CRITICAL

Examples:

- tenant-isolation changes;
- payment state changes;
- refund behavior;
- production data migrations;
- destructive schema changes;
- security boundary changes.

For HIGH/CRITICAL changes, explicitly record:

```text
What changes?
Why?
Affected invariants?
Risk?
Tests?
Rollback?
Approval status?
```

---

# 44. Stop Conditions — Do Not Guess

Stop the affected implementation and record a blocker/open question if:

- a material business rule is ambiguous;
- two requirements conflict;
- tax/legal behavior is undefined;
- membership freeze policy is undefined for a needed branch of behavior;
- cross-branch access policy is unclear;
- payment behavior is unclear;
- a financial state transition is ambiguous;
- destructive database changes are proposed;
- production data may be altered unexpectedly;
- a concurrency invariant cannot be established;
- a security boundary is unclear;
- an external integration contract is unknown;
- a migration could cause irreversible data loss;
- rollback cannot be established for a high-risk change;
- tests cannot adequately protect a critical business rule.

Do not silently make a business decision and hide it in code.

---

# 45. Git Rules

Git is the project's engineering history.

## 45.1 Never

Do not:

- force-push unless explicitly instructed;
- reset/discard user work;
- overwrite unrelated changes;
- delete another developer's work without authorization;
- commit secrets;
- make giant unrelated commits.

## 45.2 Before changing code

Check:

```bash
git status
git branch --show-current
git log -1 --oneline
```

If the working tree contains user changes, preserve them.

Do not assume the changes belong to the current task.

## 45.3 Commit style

Prefer focused commits such as:

```text
feat(auth): implement authentication foundation
feat(org): implement organization and branch foundation
feat(members): implement member management
feat(membership): implement membership lifecycle
feat(attendance): implement check-in flow
feat(billing): implement invoice workflow
feat(payments): add Razorpay integration
feat(classes): implement capacity-safe booking
fix(membership): correct freeze expiry calculation
test(payments): add webhook idempotency coverage
```

Do not create commits automatically unless the user/project workflow explicitly permits it.

## 45.4 Context and Git consistency

When the current task ends, update `PROJECT_CONTEXT.md` with the actual Git state.

Do not invent commit hashes.

---

# 46. Dependency Rules

Before adding a package:

1. confirm the requirement;
2. check whether existing dependencies already solve it;
3. verify compatibility with the chosen stack;
4. explain why the package is needed;
5. identify security/maintenance implications;
6. record it in `PROJECT_CONTEXT.md`.

Do not add libraries simply because they are popular.

Do not upgrade major dependencies opportunistically during an unrelated feature.

Pin reproducible dependency versions in project manifests/lock files.

---

# 47. Configuration and Environment Rules

Separate:

```text
Development
Staging
Production
```

Never commit secrets.

Document required environment variables without storing secret values in Git.

The agent must distinguish:

- application config;
- environment config;
- secrets;
- infrastructure settings.

Do not change production configuration from a development task without explicit scope.

---

# 48. AWS and Production Rules

The PRD targets AWS and requires:

- health checks;
- automated backups;
- monitoring;
- error alerting;
- database recovery;
- 99.9% monthly availability target.

Do not provision expensive or complex AWS architecture without a documented reason aligned to the project's initial scale and budget tier.

Production changes should be staged and reversible where possible.

Production-readiness must include a rollback plan.

---

# 49. Backup and Recovery Rules

The PRD requires:

- daily full database backup;
- point-in-time recovery where supported;
- backup retention of at least 30 days;
- monthly restore test.

A backup feature is not considered complete merely because a backup command exists.

Record:

- schedule;
- retention;
- storage location;
- encryption/protection;
- restore procedure;
- last restore verification.

---

# 50. Observability Rules

Production-capable features should provide sufficient information to answer:

```text
What happened?
Where?
For which organization/branch?
Which request/job?
What failed?
Can it be retried safely?
```

Use structured logs where appropriate.

Do not expose sensitive personal/payment data unnecessarily.

Health checks should distinguish application availability from dependency health when practical.

---

# 51. Import / Export Rules

Exports must respect authorization and tenant/branch scope.

Never allow an unauthorized user to export another branch's or organization's data.

For CSV/Excel imports:

- validate schema;
- validate row data;
- validate business rules;
- detect duplicates;
- preview errors;
- require confirmation before import;
- preserve an import report;
- audit the import operation.

---

# 52. API / UI Consistency Rules

Whenever a backend contract changes:

1. identify frontend consumers;
2. update them or preserve backward compatibility;
3. update tests;
4. update API documentation/state;
5. record the iteration.

Do not leave frontend and backend contracts silently inconsistent.

---

# 53. Refactoring Rules

Refactoring must not silently alter business behavior.

Before a significant refactor:

- identify why it is needed;
- identify behavior that must remain unchanged;
- identify tests that protect it;
- perform the smallest safe refactor;
- run relevant tests;
- record any behavioral risk.

Do not combine large refactors with unrelated feature work unless necessary.

---

# 54. Bug-Fix Rules

When fixing a bug:

1. reproduce or characterize the issue where practical;
2. identify root cause;
3. determine affected requirements;
4. implement the minimal safe fix;
5. add a regression test;
6. run the affected test suite;
7. update `PROJECT_CONTEXT.md`.

If the behavior is actually a product-rule change, do not disguise it as a bug fix.

Record it as a requirement/decision change.

---

# 55. Prompt-to-Implementation Traceability

The project must maintain traceability:

```text
User Prompt
   ↓
Iteration GYM-XXX
   ↓
Requirement REQ-XXX
   ↓
Files Changed
   ↓
Tests
   ↓
Decision / Result
   ↓
Next Task
```

This is required so another developer can understand why code exists.

## 55.1 If the prompt requests multiple unrelated things

Split the work into separate bounded iterations.

Do not produce one giant undocumented change.

---

# 56. Mandatory End-of-Task Protocol

Before saying a meaningful task is complete, do all of the following:

## A. Review changed files

Determine the actual files changed.

Do not guess from memory.

## B. Review behavior

Check whether the implemented behavior matches the requirement and acceptance criteria.

## C. Run tests

Run the relevant tests.

Record actual results.

## D. Review security

Check authentication, authorization, tenant isolation, sensitive data, and external integrations where relevant.

## E. Review performance

Check obvious N+1, unbounded-query, large-payload, synchronous-integration, and expensive-operation risks.

## F. Update PROJECT_CONTEXT.md

Record:

- iteration;
- requirement IDs;
- files;
- schema/API changes;
- implementation;
- test results;
- decisions;
- failures;
- TODOs;
- blockers;
- next task;
- Git state.

## G. Confirm next step

The project context must state exactly what should happen next.

---

# 57. Required End-of-Task Report

For every meaningful task, provide a concise report in this structure:

```text
Task ID:

Module:

Objective:

Status:

Requirements:

Completed:

Files created:

Files modified:

Files deleted:

Database changes:

API changes:

Frontend changes:

Tests written:

Tests executed:

Test result:

Security review:

Performance review:

Failed attempts / corrections:

Known issues:

TODO:

Blockers:

Decisions:

Git branch:

Git commit:

PROJECT_CONTEXT.md updated: YES/NO

Next task:
```

Never fabricate values.

---

# 58. Phase-Based Implementation Order

Use the PRD roadmap as the baseline sequence while respecting technical dependencies.

## Phase 0 — Foundation

PRD Week 1:

- AWS/environment foundation;
- Django project;
- Vue application;
- authentication;
- tenant architecture;
- branch architecture;
- user roles;
- database foundation;
- CI/CD;
- logging.

## Phase 1 — Members and Memberships

- member CRUD;
- search/filter;
- profile;
- plans;
- membership lifecycle;
- freeze/hold;
- renewal.

## Phase 2 — Attendance

- QR generation;
- QR scanning;
- staff check-in;
- history;
- eligibility;
- biometric/RFID adapter interface.

## Phase 3 — Billing and Payments

- invoices;
- payments;
- Razorpay;
- webhooks;
- payment history;
- dues;
- renewal payment;
- recurring billing.

## Phase 4 — Classes and PT

- class management;
- trainer calendar;
- capacity;
- booking;
- cancellation;
- waitlist where configured;
- PT packages;
- PT sessions.

## Phase 5 — Member Portal and Workout

- member dashboard;
- membership;
- payments;
- classes;
- attendance;
- workout plans;
- workout logging;
- progress.

## Phase 6 — Staff, Reporting, Notifications, Migration

- staff management;
- trainer management;
- dashboard;
- core reports;
- notifications;
- data migration.

## Phase 7 — Production Readiness

- security testing;
- performance testing;
- UAT;
- bug fixing;
- production deployment;
- backup/restore verification;
- monitoring.

## Phase 8 — Post-MVP

Only after MVP acceptance and explicit scope approval:

- native mobile;
- WhatsApp automation;
- advanced CRM;
- advanced analytics;
- biometric vendor integrations;
- RFID/access control;
- compensation automation;
- advanced progress;
- referral systems.

Do not allow Phase 2/3 features to silently consume MVP schedule unless approved.

---

# 59. Critical Workflow Invariants

These invariants must not be violated.

## 59.1 Tenant isolation

A user must never access resources outside their authorized organization scope.

## 59.2 Branch isolation

A branch-limited user must never access unauthorized branch data.

## 59.3 Membership history

Renewal must not erase prior membership history.

## 59.4 Freeze history

Normal staff must not delete historical freeze records.

## 59.5 Payment integrity

A duplicate webhook must not produce duplicate payment effects.

## 59.6 Payment history

Historical financial records must remain auditable.

## 59.7 Class capacity

Successful bookings must never exceed configured capacity.

## 59.8 Member overlap

A member must not successfully book overlapping sessions when the PRD rule applies.

## 59.9 Trainer conflict

A trainer must not be assigned conflicting sessions.

## 59.10 PT balance

A completed PT session must not consume more than one available session per completion operation.

## 59.11 Check-in eligibility

An ineligible member must not be silently checked in through ordinary paths.

## 59.12 Backend authority

Frontend state is never the final business truth.

---

# 60. Performance-Sensitive Workflows

Treat these as performance-sensitive:

1. member lookup;
2. check-in;
3. payment confirmation;
4. class booking;
5. owner dashboard;
6. search/filter;
7. report generation.

Optimize them according to evidence and PRD targets.

---

# 61. UX-Sensitive Workflows

The PRD emphasizes low-friction front-desk operations.

Do not introduce unnecessary navigation steps into:

- check-in;
- member lookup;
- payment collection;
- renewal;
- class booking;
- registration.

For member mobile usage, prioritize clear responsive layouts and fast access to:

- membership;
- QR;
- payment;
- booking;
- attendance;
- workout;
- progress.

---

# 62. Documentation Update Rules

Documentation must describe the current truth, not an ideal future state.

Whenever implementation changes:

- update affected API/state descriptions;
- update architecture decisions if changed;
- update requirement status;
- update module status;
- update TODOs;
- update blockers;
- append iteration history.

Do not create contradictory documentation.

If documentation and code disagree, determine the actual intended behavior and fix the inconsistency deliberately.

---

# 63. Context Compression / Continuation Rules

`PROJECT_CONTEXT.md` may grow large.

Do not delete history just because the file is long.

Instead:

- keep the current state at the top;
- keep historical iterations chronologically ordered;
- summarize completed historical work while preserving key decisions and failures;
- never remove decisions that explain why the architecture is the way it is;
- never remove unresolved risks without resolving them.

If the file becomes very large, preserve a compact current-state summary while retaining the original historical record unless the user explicitly approves archival.

---

# 64. Handoff Standard

At any time, another developer should be able to open the repository and determine:

```text
What are we building?
What is already built?
What is being built now?
Why was it built this way?
What remains?
What is broken?
What is risky?
What should I do next?
What must I not break?
```

The answer must be recoverable from:

```text
PRD.md
AGENTS.md
PROJECT_CONTEXT.md
source code
migrations
tests
Git history
```

No critical knowledge should exist only inside a private AI conversation.

---

# 65. Fresh-Developer / Fresh-AI Recovery Protocol

If a completely new developer or AI agent joins:

1. Read `AGENTS.md`.
2. Read `PRD.md`.
3. Read the current-state sections of `PROJECT_CONTEXT.md`.
4. Read the last several iteration records relevant to the current module.
5. Inspect Git state.
6. Inspect tests for the current module.
7. Inspect current implementation.
8. Continue only from the documented `Next Task`.

Do not ask the user to reconstruct the entire previous project history if the information is already present in the repository.

---

# 66. First-Time Project Bootstrap Checklist

The first project run must establish the following before business feature implementation:

```text
[ ] PRD.md exists and is the approved baseline
[ ] AGENTS.md exists
[ ] PROJECT_CONTEXT.md exists
[ ] Requirement IDs established
[ ] Initial module inventory established
[ ] Architecture decision recorded
[ ] Multi-tenant strategy recorded
[ ] Branch authorization strategy recorded
[ ] Authentication strategy recorded
[ ] Authorization matrix recorded
[ ] Data model designed
[ ] API versioning defined
[ ] API contract approach defined
[ ] Testing strategy defined
[ ] Environment strategy defined
[ ] Git baseline committed
```

---

# 67. Initial Project Bootstrap Task

When starting from an empty repository, the first AI task must be documentation and architecture preparation, not full application generation.

The agent should:

1. read `PRD.md`;
2. create/initialize `PROJECT_CONTEXT.md`;
3. extract requirements;
4. assign requirement IDs;
5. build the module dependency map;
6. identify critical business rules;
7. identify security-critical areas;
8. identify concurrency-sensitive areas;
9. identify financial workflows;
10. identify PRD open questions;
11. propose the implementation architecture;
12. record decisions;
13. stop before large-scale feature coding if architecture is not yet approved.

---

# 68. PRD Open Questions Must Remain Visible

The PRD currently marks these areas as needing decisions or confirmation:

- WhatsApp provider;
- SMS provider;
- biometric vendor;
- GST invoice rules / finance or legal confirmation;
- membership freeze policy details;
- cross-branch membership configuration;
- trial membership policy;
- exact future accounting integration;
- other explicitly listed PRD open questions.

Do not silently convert these into arbitrary product behavior.

---

# 69. No Hidden Business Logic

Do not place important business rules in locations where they cannot be reliably discovered, such as:

- scattered Vue click handlers;
- duplicated validation rules;
- arbitrary utility functions;
- hard-coded frontend constants that affect backend truth;
- template conditionals that secretly define permissions;
- untracked background jobs;
- database triggers created without documentation;
- undocumented cron behavior.

If a business rule exists, it should have a recognizable home in the backend/domain design and be traceable to a requirement.

---

# 70. No “Magic Fixes”

Do not solve a problem by silently:

- bypassing authorization;
- broadening permissions;
- swallowing exceptions;
- disabling validation;
- changing financial state directly;
- making a query return unrelated tenant data;
- increasing limits without product approval;
- adding arbitrary retries around payments;
- disabling tests;
- weakening security;
- changing data to make a test pass.

Fix the underlying problem and document the decision.

---

# 71. No Unrelated Cleanup During Feature Work

Do not combine an implementation task with:

- broad formatting changes;
- unrelated renaming;
- dependency upgrades;
- directory reorganizations;
- speculative optimization;
- architectural rewrites.

Keep the diff explainable.

If cleanup is necessary to safely implement the feature, explain and record why.

---

# 72. Business Truth vs Presentation Truth

Always distinguish:

```text
Business Truth
    ↓
API Contract
    ↓
Frontend Presentation
```

Examples:

- A disabled “Pay” button is not authorization.
- A visible membership status badge is not membership truth.
- A frontend payment success screen is not payment settlement.
- A frontend capacity counter is not seat reservation.
- A hidden branch selector is not branch security.

The backend must remain authoritative.

---

# 73. Critical Review Checklist Before Production

Before production deployment, verify at minimum:

## Product

- [ ] Must-have PRD requirements implemented
- [ ] PRD requirement coverage recorded
- [ ] Open questions resolved or explicitly deferred

## Security

- [ ] Tenant isolation tests pass
- [ ] Branch authorization tests pass
- [ ] Authentication tested
- [ ] Role permissions tested
- [ ] Secrets excluded from repository
- [ ] Payment webhook verification tested
- [ ] Rate limiting/abuse controls reviewed
- [ ] File uploads reviewed

## Data

- [ ] Database migrations reviewed
- [ ] Production migration plan documented
- [ ] Backups configured
- [ ] Restore tested
- [ ] Data migration import verified

## Payments

- [ ] Payment states tested
- [ ] Duplicate webhook tested
- [ ] Refund tested
- [ ] Reconciliation path documented
- [ ] No raw card data stored

## Scheduling

- [ ] Capacity race tested
- [ ] Overlapping booking tested
- [ ] Trainer conflicts tested
- [ ] Cancellation tested
- [ ] Waitlist behavior tested where enabled

## Membership

- [ ] Freeze tested
- [ ] Renewal tested
- [ ] Historical memberships preserved
- [ ] Expiry rules tested

## Performance

- [ ] Check-in benchmark reviewed
- [ ] Search reviewed
- [ ] Dashboard reviewed
- [ ] N+1 queries reviewed
- [ ] Large reports handled appropriately

## Operations

- [ ] Health checks
- [ ] Error monitoring
- [ ] Logs
- [ ] Alerts
- [ ] Rollback plan
- [ ] Production environment variables

---

# 74. Required Behavior When the User Says “Continue”

If the user simply says:

```text
continue
```

or:

```text
continue the project
```

do not guess the next feature from memory.

Read:

```text
AGENTS.md
PRD.md
PROJECT_CONTEXT.md
```

Then continue from the documented `Next Task`.

If the next task is blocked, report the blocker instead of silently jumping to an unrelated module.

---

# 75. Required Behavior When Context Is Missing

If `PROJECT_CONTEXT.md` does not match the source code or Git state:

1. do not invent the missing history;
2. inspect source code and tests;
3. inspect Git history;
4. reconstruct only what can be evidenced;
5. mark uncertain information as `UNKNOWN`;
6. record the recovery work in a new iteration.

The agent must distinguish evidence from inference.

---

# 76. Required Behavior for Generated Code

Generated code must be:

- understandable;
- typed/validated where applicable;
- testable;
- consistent with project conventions;
- free of secrets;
- free of unexplained magic numbers;
- documented where the behavior is non-obvious.

Do not generate large amounts of code that the agent cannot explain or verify.

Prefer incremental implementation.

---

# 77. Required Behavior for Schema / Model Generation

Before generating a new model, confirm:

- owning organization/tenant;
- branch relationship where applicable;
- lifecycle;
- uniqueness;
- indexes;
- deletion behavior;
- audit requirements;
- relationships;
- concurrency implications;
- whether it is a financial record.

Do not create models only because the frontend needs a screen.

Start from the business domain.

---

# 78. Required Behavior for API Generation

Before generating an endpoint, confirm:

- requirement ID;
- actor/role;
- organization scope;
- branch scope;
- allowed action;
- request schema;
- validation;
- service logic;
- response;
- errors;
- idempotency if relevant;
- audit if relevant;
- tests.

Do not expose a model directly merely because DRF makes it easy.

---

# 79. Required Behavior for Frontend Generation

Before generating a page/component, confirm:

- user role;
- allowed actions;
- API source;
- loading state;
- empty state;
- validation errors;
- backend errors;
- pagination/filtering;
- mobile behavior;
- permission visibility;
- whether the action has a concurrency risk.

Do not encode business rules into visual state alone.

---

# 80. Required Behavior for Testing Generated Features

For a new feature, generate tests around:

```text
Happy path
Validation failure
Authorization failure
Tenant isolation
Branch restriction where applicable
Boundary condition
Duplicate request / idempotency where applicable
Concurrency where applicable
External failure where applicable
```

The exact matrix depends on risk.

---

# 81. Project Progress Model

Maintain module status in `PROJECT_CONTEXT.md` using:

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

Maintain an overall project percentage only when the calculation is defined consistently. Do not invent a percentage merely because it looks useful.

A practical approach is to calculate progress from requirement coverage rather than lines of code.

---

# 82. TODO Rules

TODOs must be actionable.

Good:

```text
TODO:
Resolve cross-branch membership policy before implementing multi-branch booking.
```

Bad:

```text
TODO: finish project
```

Each active TODO should ideally include:

- description;
- module;
- priority;
- dependency;
- owner/actor when relevant;
- status.

Do not leave obsolete TODOs active.

When a TODO is completed, mark it complete in history rather than silently deleting it if it has implementation significance.

---

# 83. Blocker Rules

A blocker must explain:

- what is blocked;
- why;
- what is needed;
- impact;
- affected requirements;
- workaround if one exists;
- status.

Do not hide blockers by skipping the affected requirement.

---

# 84. Decision Rules

For significant decisions record:

```text
Decision ID:
Date:
Context:
Decision:
Alternatives considered:
Reason:
Consequences:
Risks:
Affected modules:
Related requirements:
```

Do not preserve only the conclusion. Preserve enough reasoning that a future developer understands why it was selected.

---

# 85. “Do Not Improve the PRD” Rule

Do not silently modify product scope because a different design appears more modern.

Examples:

- do not add AI features to V1 because they are trendy;
- do not replace responsive web with native mobile;
- do not turn the modular Django application into microservices without a reason;
- do not add accounting/ERP capabilities;
- do not change the payment provider without approval;
- do not add arbitrary roles;
- do not add advanced CRM when core member/payment workflows remain incomplete.

The goal is faithful execution of the approved product baseline.

---

# 86. “Do Not Underbuild the PRD” Rule

Do not mark a capability complete by implementing only its visible UI.

Examples:

- “Payment page exists” is not payment completion.
- “Freeze button exists” is not membership freeze completion.
- “Class booking endpoint exists” is not capacity-safe booking.
- “Member dashboard exists” is not member self-service completion.
- “Import screen exists” is not migration support.
- “Role dropdown exists” is not authorization.

The underlying workflow and acceptance criteria must be implemented and tested.

---

# 87. Required Implementation Discipline for the 8-Week MVP

The PRD gives an eight-week target. The agent must optimize for the operational V1, not maximum feature count.

When schedule pressure appears:

1. protect must-have product workflows;
2. protect security;
3. protect financial correctness;
4. protect tenant isolation;
5. protect core tests;
6. defer Should/Later capabilities rather than weakening must-have behavior.

Never reduce security or financial correctness to meet a calendar date.

---

# 88. MVP Critical Path

Prioritize the connected operational path:

```text
Organization
   ↓
Branch
   ↓
User / Role
   ↓
Member
   ↓
Membership Plan
   ↓
Membership
   ↓
Payment / Invoice
   ↓
Attendance
   ↓
Classes / PT
   ↓
Workout / Progress
   ↓
Member Portal
   ↓
Renewal / Retention
```

Supporting capabilities such as reporting, notifications, migration, CRM, and integrations must plug into this path rather than create an alternative source of truth.

---

# 89. Final Rule for Every AI Session

Before changing anything:

```text
Read.
Understand.
Scope.
Plan.
```

While changing:

```text
Implement.
Test.
Review.
Protect invariants.
```

After changing:

```text
Record.
Update context.
Record TODOs/blockers.
Record decisions.
Record test results.
Record next task.
```

Never leave the repository in a state where the code changed but the project's memory did not.

---

# 90. Final Non-Negotiable Rules

1. `PRD.md` defines the product baseline.
2. `AGENTS.md` defines AI engineering behavior.
3. `PROJECT_CONTEXT.md` is the living project memory.
4. Do not rely on chat history for continuity.
5. Capture meaningful user prompts and implementation iterations automatically.
6. Capture failed attempts and corrections.
7. Preserve requirement traceability.
8. Enforce tenant isolation in backend code and tests.
9. Enforce branch authorization in backend code and tests.
10. Keep frontend out of the business-truth role.
11. Use Decimal for money.
12. Keep Razorpay behind a provider abstraction.
13. Make payment webhooks idempotent.
14. Make financial operations transactional.
15. Protect class capacity against concurrency.
16. Protect PT package balances against concurrency.
17. Preserve membership and financial history.
18. Never silently invent tax, payment, membership, or permission policies.
19. Never claim tests passed without running them.
20. Never claim completion without evidence.
21. Do not add post-MVP scope without approval.
22. Do not modify unrelated code during feature work.
23. Do not discard user changes.
24. Keep Git history reviewable.
25. Update project context after every meaningful implementation task.
26. Always leave a clear next task.
27. Make handoff possible from repository files alone.

---

# 91. Canonical Session Flow

The canonical AI workflow for this repository is:

```text
┌─────────────────────────┐
│        User Prompt      │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│       Read AGENTS.md    │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│         Read PRD        │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Read PROJECT_CONTEXT.md │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Determine scope + risk  │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Inspect existing code   │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Implement bounded task  │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│         Test            │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Security + performance │
│ review                  │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Update PROJECT_CONTEXT  │
│ + requirement status    │
│ + TODO + blockers       │
│ + decisions + history   │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Record exact next task  │
└─────────────────────────┘
```

This workflow is mandatory for meaningful engineering tasks.

---

# 92. Closing Principle

The system is being built for real gym operations involving members, staff, branches, payments, attendance, scheduling, personal training, and personal data.

Therefore:

```text
Correctness > speed
Security > convenience
Traceability > memory
Tests > assumptions
Small safe changes > giant AI rewrites
Approved requirements > agent creativity
```

When uncertain:

> **Understand first. Preserve the approved requirement. Make the smallest safe change. Verify it. Record everything needed for the next developer.**
