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

**Status:** INITIALIZATION

**Overall MVP Progress:** 0%

**Current Phase:** Phase 0 — Foundation / Product & Architecture Preparation

**Current Module:** None

**Current Task:** Establish project context and AI-assisted development operating state.

**Application Code Status:** Not started.

**Database Schema Status:** Not started.

**API Status:** Not started.

**Frontend Status:** Not started.

**Infrastructure Status:** Not started.

**Testing Status:** Not started.

**Production Status:** Not started.

## 1.3 Important Current Fact

The application implementation has **not** started yet.

Do not claim that authentication, database models, APIs, Vue screens, payments, AWS infrastructure, or tests have been implemented until actual evidence exists in the repository.

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

Requirements will be tracked as:

```text
REQ-001
REQ-002
REQ-003
...
```

Requirement IDs must never be reused.

## 9.2 Requirement Status

Allowed statuses:

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

## 9.3 User Story Requirement Baseline

| ID | Requirement | Priority | Module | Status |
|---|---|---|---|---|
| REQ-US-001 | Owner can see today's revenue | Must | Dashboard/Billing | NOT_STARTED |
| REQ-US-002 | Admin can register a member | Must | Members | NOT_STARTED |
| REQ-US-003 | Admin can check member in quickly | Must | Attendance | NOT_STARTED |
| REQ-US-004 | Member can use QR check-in | Must | Attendance | NOT_STARTED |
| REQ-US-005 | Owner can see expiring memberships | Must | Dashboard/Memberships | NOT_STARTED |
| REQ-US-006 | Member can pay dues online | Must | Member Portal/Payments | NOT_STARTED |
| REQ-US-007 | Admin can freeze a membership | Must | Memberships | NOT_STARTED |
| REQ-US-008 | Member can book a class | Must | Classes | NOT_STARTED |
| REQ-US-009 | Trainer can see today's PT sessions | Must | PT/Trainer | NOT_STARTED |
| REQ-US-010 | Trainer can record workouts | Must | Workouts | NOT_STARTED |
| REQ-US-011 | Member can view progress | Must | Progress | NOT_STARTED |
| REQ-US-012 | Owner can compare branch revenue | Should | Reports | NOT_STARTED |
| REQ-US-013 | Admin can import existing members | Must | Migration | NOT_STARTED |
| REQ-US-014 | Member can view payment history | Must | Member Portal/Payments | NOT_STARTED |
| REQ-US-015 | Owner can view expired members | Must | Members/Reports | NOT_STARTED |
| REQ-US-016 | Member can cancel class booking | Must | Classes | NOT_STARTED |
| REQ-US-017 | Trainer can manage client workout plans | Must | Workouts | NOT_STARTED |
| REQ-US-018 | Admin can record cash payments | Must | Billing/Payments | NOT_STARTED |
| REQ-US-019 | Owner can configure staff permissions | Could | Authorization/Settings | NOT_STARTED |
| REQ-US-020 | Member can request membership freeze | Should | Memberships/Member Portal | NOT_STARTED |

### Traceability Rule

Each implementation task must link back to the relevant requirement IDs.

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

## 26.1 Suggested Django Domains

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

Exact implementation strategy remains a design decision to be finalized and recorded before coding.

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

### Data Model Status

**PRD baseline captured.**

**Django implementation: NOT_STARTED.**

The final data model must be reviewed for missing relationships, lifecycle requirements, auditability, constraints, indexing, financial history, concurrency and migration compatibility before models are created.

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

### Decisions Still Required

- exact Django project/app boundary
- exact authentication mechanism
- token/session strategy
- multi-tenant enforcement implementation
- permission implementation details
- branch-scope implementation
- exact API error schema
- API pagination/filtering conventions
- Redis/Celery implementation details
- file storage implementation
- AWS service selection
- CI/CD architecture
- observability stack
- WhatsApp provider
- SMS provider
- biometric vendor strategy
- exact GST invoice behavior
- membership freeze policy configuration
- cross-branch membership policy
- trial membership behavior
- accounting integration design

No engineering assumption above should be treated as approved until recorded as such.

---

# 29. Database / Migration State

## Current State

Database schema: NOT_STARTED

Django migrations: NONE

Seed/reference data: NONE

Production migration tooling: NONE

Data import tooling: NONE

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

Expected API namespace:

```text
/api/v1/
```

## Expected Domain Groups

```text
/api/v1/auth
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
/api/v1/reports
```

## Current API Status

No APIs implemented.

## API Contract Requirements

Before frontend dependence, each meaningful endpoint should define:

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

Frontend project: NOT_STARTED

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
| Accounts / Auth | Must | NOT_STARTED | Architecture | — |
| Organizations / Tenants | Must | NOT_STARTED | Architecture | — |
| Branches | Must | NOT_STARTED | Architecture | — |
| Authorization | Must | NOT_STARTED | Architecture | — |
| Members | Must | NOT_STARTED | — | Depends on foundation |
| Memberships | Must | NOT_STARTED | — | Depends on members |
| Attendance | Must | NOT_STARTED | — | Depends on members/memberships |
| Billing | Must | NOT_STARTED | — | Depends on membership/payment design |
| Payments | Must | NOT_STARTED | — | Razorpay/provider design |
| Classes | Must | NOT_STARTED | — | Depends on trainers/branch/member |
| Personal Training | Must | NOT_STARTED | — | Depends on trainers/members |
| Trainers / Staff | Must | NOT_STARTED | — | Depends on foundation |
| Workouts | Must | NOT_STARTED | — | Depends on member/trainer design |
| Progress | Must | NOT_STARTED | — | Depends on member/workout design |
| Member Portal | Must | NOT_STARTED | — | Depends on core APIs |
| Notifications | Must | NOT_STARTED | — | Provider decisions pending |
| Dashboard | Must | NOT_STARTED | — | Depends on core data |
| Reports | Must | NOT_STARTED | — | Depends on core data |
| CRM / Leads | Should | NOT_STARTED | — | Core MVP should take priority |
| Data Migration | Must | NOT_STARTED | — | Depends on final data model |
| Integrations | Must/Should by integration | NOT_STARTED | — | Vendor decisions pending |
| Audit | Must for sensitive actions | NOT_STARTED | — | Architecture dependency |
| Production / Operations | Must | NOT_STARTED | — | Later phase |

---

# 36. Active TODO

## Immediate

- [ ] Verify repository contains `PRD.md`
- [ ] Verify `AGENTS.md` is present and approved
- [ ] Maintain this `PROJECT_CONTEXT.md`
- [ ] Complete requirements traceability
- [ ] Perform architecture design
- [ ] Finalize authentication approach
- [ ] Finalize multi-tenant enforcement approach
- [ ] Finalize branch authorization strategy
- [ ] Design complete data model
- [ ] Design API conventions
- [ ] Design test strategy
- [ ] Establish Django project foundation
- [ ] Establish Vue project foundation

## Not Yet Started

All product modules remain unimplemented.

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

No tests implemented yet.

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

Status: NOT_STARTED

## Staging

Status: NOT_STARTED

## Production

Status: NOT_STARTED

## AWS

Status: NOT_STARTED

## CI/CD

Status: NOT_STARTED

## Monitoring

Status: NOT_STARTED

## Backups

Status: NOT_STARTED

## Restore Verification

Status: NOT_STARTED

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

The exact branch, commit and working-tree state must be filled from the actual repository.

```text
Branch:
UNKNOWN — inspect repository

HEAD:
UNKNOWN — inspect repository

Working Tree:
UNKNOWN — inspect repository
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

Perform the complete requirements and architecture analysis before creating business application code.

### Immediate sequence

```text
1. Requirement traceability
2. Architecture design
3. Authentication design
4. Authorization design
5. Multi-tenant design
6. Branch access design
7. Full data model
8. API conventions
9. Testing strategy
10. Environment strategy
11. Django foundation
12. Vue foundation
```

No business module should be declared complete before these foundations are sufficiently established.

---

# 55. Handoff

## Project

Gym Management Portal

## Current Phase

Phase 0 — Foundation

## Current Module

None

## Current Task

Requirements + architecture preparation

## Last Completed

Initial project context created from PRD.

## Application Code

Not started.

## Tests

Not started.

## Database

Not started.

## API

Not started.

## Frontend

Not started.

## Deployment

Not started.

## Current Blockers

No active blockers.

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

**Requirements traceability and architecture design.**

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
REQUIREMENT TRACEABILITY          ⬜
ARCHITECTURE                      ⬜
AUTHENTICATION                    ⬜
AUTHORIZATION                     ⬜
TENANT / BRANCH SECURITY          ⬜
DATA MODEL                        ⬜
API CONTRACT                      ⬜
DJANGO FOUNDATION                 ⬜
VUE FOUNDATION                    ⬜
MEMBERS                           ⬜
MEMBERSHIPS                       ⬜
ATTENDANCE                        ⬜
BILLING                           ⬜
PAYMENTS / RAZORPAY               ⬜
CLASSES                           ⬜
PT                                ⬜
TRAINERS                          ⬜
WORKOUTS                          ⬜
PROGRESS                          ⬜
MEMBER PORTAL                     ⬜
NOTIFICATIONS                     ⬜
DASHBOARD                         ⬜
REPORTS                           ⬜
CRM                               ⬜
DATA MIGRATION                    ⬜
SECURITY HARDENING                ⬜
PERFORMANCE HARDENING             ⬜
AWS / PRODUCTION                  ⬜
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

At this point, the project is intentionally **not implemented**.

The repository has a product baseline and a living context model.

The next implementation step is not to build random features.

The next step is to establish the engineering foundation from the PRD:

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
