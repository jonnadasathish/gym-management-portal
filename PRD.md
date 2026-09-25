# Gym Management Portal — Product Requirements Document

## 1. Document Info

| Field | Details |
|---|---|
| **Product** | Gym Management Portal |
| **Document Type** | Product Requirements Document |
| **Author** | Senior Product Management |
| **Version** | 1.0 |
| **Date** | September 24, 2026 |
| **Status** | Draft — Product/Engineering Ready |
| **Target Market** | India |
| **Target Customer** | Independent gyms and small multi-location gym chains |
| **Initial Gym Size** | 100–500 members/location |
| **Platform** | Responsive web portal; member functionality included in the same platform |
| **Frontend** | Vue |
| **Backend** | Python Django |
| **Database** | MySQL |
| **Cloud** | AWS |
| **Initial Delivery Target** | 8 weeks |
| **Budget Tier** | Mid-market |

## Assumptions

1. The product supports multiple branches/locations from V1.
2. The target gym has approximately 100–500 active members per location, while the architecture should support growth.
3. The initial market is India, with INR as the default currency.
4. Razorpay is the initial payment gateway. Stripe/other gateways should be abstracted behind a payment-provider interface.
5. WhatsApp/SMS integration is desirable; the MVP prioritizes critical transactional notifications.
6. Members use the same web platform, with role-specific screens and a mobile-responsive member experience. Native apps are Phase 2.
7. Fixed roles are used: Owner, Front Desk/Admin, Trainer/Coach, Member.
8. GST-ready invoicing is included because the product targets Indian gyms.
9. Biometric/RFID devices are integrated through an adapter/API layer.
10. Existing gym software migration initially supports CSV/Excel import and a migration framework.
11. Workout/progress tracking is included, but advanced AI coaching is out of scope for V1.
12. The 8-week timeline prioritizes operational workflows over advanced analytics and automation.

---

## 2. Executive Summary

The Gym Management Portal is a multi-location SaaS platform that enables gym owners and staff to manage members, memberships, attendance, billing, classes, personal training, trainers and member engagement from one system.

The product targets independent gyms and small gym chains in India that currently rely on spreadsheets, paper registers, messaging apps and disconnected payment systems. The platform will reduce front-desk administration while giving owners real-time visibility into membership status, revenue, attendance and member retention.

Members will have self-service access to their membership, payments, bookings, attendance and fitness progress through the same responsive portal.

The MVP focuses on member management, check-in, memberships, payments, scheduling, PT, trainers and member self-service.

---

## 3. Problem Statement

### 3.1 Current Problems

Small and mid-sized gyms frequently manage operations using combinations of:

- Excel/Google Sheets
- Paper attendance registers
- WhatsApp
- Cash/UPI/card payment records
- Separate biometric systems
- Personal trainer notebooks
- Accounting software
- Multiple calendars
- Manual renewal reminders

This creates several operational problems.

### Problem 1 — Membership information is fragmented

Gym staff may need multiple systems to answer:

- Is this member active?
- When does their membership expire?
- Which plan do they have?
- Have they paid?
- Are they currently frozen?
- How many sessions remain?

### Problem 2 — Renewals are manually tracked

Expired and soon-to-expire members can easily be missed.

The system should automatically identify:

- Expiring memberships
- Expired memberships
- Outstanding balances
- Failed recurring payments
- Members returning from a freeze

### Problem 3 — Attendance is inefficient

At peak hours, front-desk employees need to process check-ins quickly. Manual name searches create queues and increase errors.

The product should support:

`QR → member identification → eligibility validation → attendance recorded`

with a target interaction time of a few seconds.

### Problem 4 — Revenue visibility is poor

Owners need to answer:

- How much was collected today?
- How much is pending?
- Which branch generated the most revenue?
- How many memberships expire this week?
- How many members joined this month?
- How many cancelled?
- How much revenue came from PT?

### Problem 5 — Trainer operations are disconnected

Trainers need visibility into:

- Clients
- Scheduled PT sessions
- Completed sessions
- Workout programs
- Client progress
- Session/package balances

### Problem 6 — Members depend too heavily on staff

Members should not need to contact reception for routine tasks such as:

- Checking membership expiry
- Making payments
- Booking classes
- Viewing attendance
- Checking PT sessions
- Viewing workout plans
- Freezing membership

---

## 4. Goals & Success Metrics

### 4.1 Business Goals

| Goal | Target |
|---|---:|
| Reduce manual member-management work | ≥40% |
| Reduce time spent tracking renewals | ≥50% |
| Reduce billing entry errors | ≥60% |
| Enable member self-service | ≥50% of routine requests |
| Reduce average check-in time | <10 seconds |
| Increase digital payment adoption | ≥50% of payments |
| Improve renewal follow-up coverage | ≥90% of expiring members |
| Provide owner visibility | Daily real-time dashboard |
| Support multiple branches | V1 |

### 4.2 Product KPIs

#### Adoption

- % of members with complete profiles
- Daily active staff users
- Weekly active members
- % of memberships managed through platform

#### Revenue

- Monthly recurring revenue processed
- Collection rate
- Outstanding dues
- Renewal conversion rate
- Failed payment recovery rate

#### Engagement

- Average visits/member/month
- Class booking rate
- PT session completion
- Member portal login rate

#### Retention

- Membership renewal rate
- Membership expiry rate
- Freeze rate
- Cancellation rate
- 30/60/90-day member retention

---

## 5. Non-Goals

The following are outside V1:

- Full accounting/ERP system
- Payroll processing
- Advanced HR management
- Native iOS/Android applications
- AI-generated workout plans
- AI personal trainer
- Nutrition/meal planning engine
- Marketplace for gyms/trainers
- Gym equipment IoT management
- Full POS/retail inventory system
- Franchise royalty management
- Advanced marketing automation
- Video workout streaming
- Insurance management
- Hardware manufacturing
- Direct biometric hardware control for every vendor
- International tax compliance

---

## 6. User Personas

### 6.1 Gym Owner

**Primary objective:** Run the business and increase revenue.

**Goals**
- See business performance
- Monitor collections
- Reduce churn
- Monitor staff
- Manage branches
- Understand attendance
- Track renewals

**Frustrations**
- Lack of visibility
- Manual reports
- Missed renewals
- Payment reconciliation
- Staff dependency

**Technical comfort:** Medium

### 6.2 Front Desk/Admin Staff

**Primary objective:** Process daily gym operations quickly.

**Goals**
- Register members
- Collect payments
- Check members in
- Handle renewals
- Manage bookings
- Answer member questions

**Frustrations**
- Slow software
- Repeated data entry
- Long check-in queues
- Searching spreadsheets
- Manual payment tracking

**Technical comfort:** Medium

### 6.3 Trainer/Coach

**Primary objective:** Manage clients and deliver training.

**Goals**
- See today's sessions
- Manage PT clients
- Record workouts
- Track progress
- Complete sessions
- View package balance

**Frustrations**
- Paper workout sheets
- Missing client history
- Scheduling conflicts
- Manual session tracking

**Technical comfort:** Medium

### 6.4 Member

**Primary objective:** Manage gym membership and fitness activity independently.

**Goals**
- Check membership
- Pay dues
- Book classes
- Book PT
- Check attendance
- View workout plans
- Track progress

**Frustrations**
- Calling reception
- Unclear membership expiry
- Payment uncertainty
- Class booking through WhatsApp
- Losing workout history

**Technical comfort:** Medium–High

### Role-Permission Matrix

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

---

## 7. User Stories / Use Cases

| ID | Persona | Story | Priority | Acceptance Criteria |
|---|---|---|---|---|
| US-001 | Owner | I want to see today's revenue so that I know business performance | Must | Dashboard shows today's collected, pending and refunded amounts |
| US-002 | Admin | I want to register a member so that they can start their membership | Must | Member can be created with mandatory fields and assigned plan |
| US-003 | Admin | I want to check a member in quickly so that queues don't form | Must | Valid member can be checked in within 10 seconds |
| US-004 | Member | I want to scan my QR code so that I can enter quickly | Must | Valid QR records attendance |
| US-005 | Owner | I want to see expiring memberships so that staff can follow up | Must | Dashboard shows configurable expiry windows |
| US-006 | Member | I want to pay my dues online so that I don't need reception assistance | Must | Successful gateway payment updates balance |
| US-007 | Admin | I want to freeze a membership so that membership dates are adjusted correctly | Must | Freeze period is recorded and expiry recalculated |
| US-008 | Member | I want to book a class so that I can reserve a place | Must | Booking succeeds only when capacity is available |
| US-009 | Trainer | I want to see today's PT sessions so that I can plan my day | Must | Calendar shows assigned sessions |
| US-010 | Trainer | I want to record a workout so that the member has a fitness history | Must | Workout is saved against member/date |
| US-011 | Member | I want to view my progress so that I can track improvement | Must | Measurements and historical values are displayed |
| US-012 | Owner | I want to compare branch revenue so that I can monitor locations | Should | Branch-level revenue comparison available |
| US-013 | Admin | I want to import existing members so that migration doesn't require manual entry | Must | CSV validation and import supported |
| US-014 | Member | I want to view my payment history so that I can verify transactions | Must | Paid invoices/receipts are displayed |
| US-015 | Owner | I want to see expired members so that staff can follow up | Must | Expired members can be filtered/exported |
| US-016 | Member | I want to cancel a class booking so that someone else can use the slot | Must | Cancellation updates capacity |
| US-017 | Trainer | I want to manage my client workout plans so that I can prescribe training | Must | Trainer can create/assign programs |
| US-018 | Admin | I want to collect cash payments so that offline payments are recorded | Must | Cash payment creates payment record |
| US-019 | Owner | I want to configure staff permissions | Could | Permission settings available if enabled in later phase |
| US-020 | Member | I want to freeze my membership | Should | Request follows configured approval policy |

---

## 8. Functional Requirements (by Module)

### 8.1 Member Management

#### Description

Central member database containing identity, contact, membership, payment, attendance and fitness information.

#### Member Profile

Store:

- Member ID
- Full name
- Profile photo
- Date of birth
- Gender
- Mobile number
- Email
- Address
- Emergency contact
- Joining date
- Branch
- Assigned trainer
- Membership status
- Medical/fitness notes
- Consent status

#### Membership

Each member can have:

- Current membership
- Historical memberships
- Membership plan
- Start date
- End date
- Price
- Discount
- Payment status
- Freeze history
- Renewal history

#### Freeze/Hold

Admin can:

- Start freeze
- Specify reason
- Specify start/end date
- Add notes
- View history

System must calculate revised expiry according to configured freeze policy.

#### Acceptance Criteria

- Member can be created without duplicate mobile numbers within the same gym.
- Member status automatically changes based on membership dates.
- Freeze history cannot be deleted by normal staff.
- Membership history remains accessible after renewal.
- Search returns results by name, mobile, member ID and QR ID.

**Priority: Must**

---

### 8.2 Attendance & Check-in

#### Check-in Methods

1. Staff search by name/mobile/member ID
2. QR code
3. Biometric/RFID integration

#### Biometric/RFID Adapter

Support:

- Device ID
- Member identifier
- Check-in timestamp
- Check-out timestamp
- Device status

#### Eligibility Rules

System validates:

- Membership active
- Branch permitted
- Account not blocked
- Check-in not already recorded within configured interval

#### Acceptance Criteria

- QR check-in completes in ≤10 seconds under normal conditions.
- Invalid/expired membership shows clear reason.
- Every check-in stores member, branch, timestamp and method.
- Duplicate check-ins are prevented according to configurable rules.
- Staff can manually override with audit logging.

**Priority: Must**

---

### 8.3 Billing & Payments

#### Membership Billing

Support:

- One-time payments
- Recurring memberships
- Installments
- Discounts
- Taxes
- Partial payments
- Cash
- UPI
- Card
- Online payment gateway

Razorpay is the initial provider. The payment layer must remain provider-agnostic.

#### Payment States

```text
Pending
Initiated
Successful
Failed
Refunded
Partially Refunded
Cancelled
```

#### Invoice

Invoice should contain:

- Invoice number
- Gym details
- GST details where applicable
- Member
- Items
- Discount
- Tax
- Total
- Payment method
- Payment status
- Date

#### Recurring Billing

Support:

- Billing frequency
- Start date
- Next billing date
- Mandate/subscription ID
- Payment retries
- Failed-payment status

#### Acceptance Criteria

- Successful payment automatically updates membership/payment status.
- Duplicate webhook events do not create duplicate payments.
- Failed payment is visible to staff.
- Member receives payment confirmation.
- Refund updates payment and invoice records.
- Payment records are immutable except through controlled refund/correction workflows.
- No raw card credentials are stored.

**Priority: Must**

---

### 8.4 Class & Session Scheduling

Support:

- Group classes
- Personal training
- Trainer calendars
- Recurring classes
- One-off sessions
- Capacity limits
- Waitlists
- Booking
- Cancellation
- No-show tracking

#### Class Configuration

```text
Class
 ├── Name
 ├── Branch
 ├── Trainer
 ├── Room
 ├── Capacity
 ├── Start time
 ├── End time
 └── Booking policy
```

#### Acceptance Criteria

- Class cannot exceed configured capacity.
- Member cannot book overlapping sessions.
- Cancellation releases the slot.
- Waitlist can promote members when a slot becomes available.
- Trainer cannot have conflicting sessions.
- Class attendance is linked to booking.

**Priority: Must**

---

### 8.5 Personal Training

#### PT Packages

Examples:

- 5 sessions
- 10 sessions
- 20 sessions
- Monthly unlimited PT

Track:

- Package price
- Sessions purchased
- Sessions consumed
- Sessions remaining
- Expiry
- Assigned trainer

#### PT Session

Each session stores:

- Member
- Trainer
- Date/time
- Duration
- Status
- Notes
- Workout
- Session number

#### Session States

```text
Scheduled
Completed
Cancelled
No-show
Rescheduled
```

#### Acceptance Criteria

- Completed session decrements available package balance.
- Cancelled session does not decrement balance unless gym policy says otherwise.
- Trainer can only modify their assigned sessions.
- Owner can view all PT sessions.
- Member can view remaining sessions.

**Priority: Must**

---

### 8.6 Staff & Trainer Management

#### Staff

Store:

- Name
- Mobile
- Email
- Role
- Branch
- Joining date
- Employment status

#### Trainer

Additional fields:

- Specializations
- Certifications
- Assigned members
- Classes
- PT sessions
- Compensation model

#### Compensation

V1 supports basic calculation:

- Fixed salary
- Per-session amount
- Per-class amount
- Revenue percentage

Payroll disbursement itself is not included.

#### Acceptance Criteria

- Owner can activate/deactivate staff.
- Trainer sees only assigned operational information.
- Staff cannot access owner-only financial settings.
- Compensation reports can be exported.

**Priority: Must**

---

### 8.7 Leads & CRM

A basic lead pipeline is recommended because acquisition and conversion are directly connected to membership growth.

#### Lead Fields

- Name
- Phone
- Source
- Interested plan
- Branch
- Assigned staff
- Trial date
- Status
- Next follow-up
- Notes

#### Pipeline

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

#### Acceptance Criteria

- Every lead has an owner.
- Follow-up date can be assigned.
- Conversion creates a member without duplicate data entry.
- Conversion source is retained.

**Priority: Should**

---

### 8.8 Reporting & Analytics Dashboard

#### Owner Dashboard

##### Revenue

- Today's collection
- Monthly collection
- Pending dues
- Refunds
- Revenue by branch
- Revenue by membership plan

##### Membership

- Active members
- Expired members
- Expiring within 7 days
- Expiring within 30 days
- New members
- Cancelled members
- Frozen members

##### Attendance

- Today's check-ins
- Daily trend
- Monthly trend
- Average visits/member
- Peak hours

##### PT

- PT sessions
- Completed sessions
- Remaining package sessions
- PT revenue

#### Reports

Export CSV/PDF where appropriate.

**Priority: Must**

---

### 8.9 Notifications

#### Channels

- WhatsApp
- SMS
- Email
- In-app notification

#### Mandatory Transactional Notifications

| Event | Notification |
|---|---|
| Membership created | Welcome |
| Payment successful | Receipt |
| Payment failed | Payment failure |
| Membership expiring | Reminder |
| Membership expired | Expiry |
| Class booking | Confirmation |
| Class reminder | Reminder |
| PT booking | Confirmation |
| PT reminder | Reminder |
| Birthday | Birthday message |
| Freeze approved | Confirmation |

WhatsApp should use an approved Business API provider.

**Priority: Must for core transactional events; Should for advanced campaigns.**

---

### 8.10 Multi-Branch Support

Each branch has:

- Name
- Address
- Contact
- Operating hours
- Staff
- Trainers
- Members
- Classes
- Revenue
- Attendance

#### Owner

Can:

- View all branches
- Switch branch
- Compare performance
- Consolidate reports

#### Staff

Default access: assigned branch only.

#### Member

Has:

- Home branch
- Allowed branches if membership permits multi-branch access

#### Acceptance Criteria

- Data from Branch A cannot appear in Branch B staff views without authorization.
- Owner can aggregate data across branches.
- Branch-level revenue and attendance are separately identifiable.

**Priority: Must**

---

### 8.11 Member Portal

The member experience is responsive and accessible from mobile browsers in V1.

#### Member Home

Display:

- Membership status
- Expiry date
- QR code
- Upcoming class
- Upcoming PT session
- Outstanding balance
- Recent attendance

#### Member Actions

**Membership**
- View plan
- View expiry
- Request freeze
- Renew
- View history

**Payments**
- Pay dues
- View invoices
- View payment history

**Classes**
- Browse
- Book
- Cancel
- Join waitlist
- View bookings

**Attendance**
- Attendance history
- Visit frequency

**PT**
- View trainer
- View sessions
- Book PT

**Workout**
- View assigned plan
- Log workout
- Record sets/reps/weight

**Progress**
- Weight
- Body measurements
- Progress photos
- Personal bests

**Priority: Must**

---

### 8.12 Workout & Progress Tracking

#### Workout Program

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

#### Exercise Library

Each exercise can include:

- Name
- Muscle group
- Equipment
- Instructions
- Video/image reference

#### Member Logging

Member can record:

- Sets
- Reps
- Weight
- Duration
- Notes

#### Progress

Track:

- Body weight
- BMI where applicable
- Body measurements
- Strength PRs
- Workout completion
- Progress photos

**Priority: Must**

---

## 9. Non-Functional Requirements

### 9.1 Performance

| Requirement | Target |
|---|---:|
| Standard API response | p95 <500ms |
| Dashboard API | p95 <1.5s |
| Check-in backend processing | <2s |
| Page initial load | <3s on standard broadband |
| Search response | <500ms |
| Large report generation | Asynchronous |

### 9.2 Scalability

Initial design:

- Multi-tenant SaaS
- Multiple gyms
- Multiple branches/gym
- 100–500 members/location

Architecture should support future growth to 10,000+ gyms and millions of member records without a fundamental rewrite.

### 9.3 Security

Required:

- HTTPS everywhere
- Password hashing
- Secure session/token management
- Role-based authorization
- Tenant isolation
- Branch-level authorization
- Audit logging
- Rate limiting
- CSRF protection
- XSS protection
- SQL injection prevention
- Secure file upload validation
- Secrets outside source code
- Encryption at rest where appropriate
- Encryption in transit

### 9.4 Payment Security

The application must not store raw card details. Payment processing is delegated to the payment gateway.

### 9.5 Personal Data

The system processes names, phone numbers, emails, addresses, fitness information, payment information and attendance history.

The implementation should support appropriate consent, purpose limitation, data access/deletion workflows and security controls applicable to India's Digital Personal Data Protection framework.

### 9.6 Availability

Target: **99.9% monthly availability**

AWS deployment should support:

- Health checks
- Automated backups
- Monitoring
- Error alerting
- Database recovery

### 9.7 Backup

Minimum:

- Daily full database backup
- Point-in-time recovery where supported
- Backup retention ≥30 days
- Monthly restore test

### 9.8 Localization

V1:

- INR
- Indian date/time formats
- IST timezone
- Indian mobile numbers
- GST-ready invoices
- English UI

Future:

- Hindi
- Telugu
- Tamil
- Kannada
- Marathi
- Other regional languages

---

## 10. Technical Considerations

### 10.1 High-Level Architecture

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

### 10.2 Suggested Django Applications

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

### 10.3 Multi-Tenant Model

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

Every business record should have an organization/tenant association.

Authorization must verify:

```text
User → Organization → Branch → Resource
```

### 10.4 Core Data Model

#### Organization

```text
id
name
status
created_at
```

#### Branch

```text
id
organization_id
name
address
phone
timezone
status
```

#### User

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

#### Member

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

#### MembershipPlan

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

#### Membership

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

#### Subscription

```text
id
member_id
membership_id
gateway
gateway_subscription_id
status
next_billing_date
```

#### Payment

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

#### Attendance

```text
id
member_id
branch_id
checkin_at
checkout_at
method
device_id
```

#### Class

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

#### Booking

```text
id
class_id
member_id
status
booked_at
cancelled_at
```

#### PTPackage

```text
id
member_id
trainer_id
sessions_purchased
sessions_used
expiry_date
```

#### PTSession

```text
id
package_id
member_id
trainer_id
scheduled_at
status
notes
```

#### WorkoutProgram

```text
id
member_id
trainer_id
name
start_date
end_date
status
```

#### WorkoutLog

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

---

## 11. UX/Design Principles

### 11.1 Primary Principle

**The front desk should complete common operations with minimal clicks.**

Optimize for:

1. Check-in
2. Member lookup
3. Payment collection
4. Renewal
5. Class booking
6. Member registration

### 11.2 Key Screens

#### Owner

- Dashboard
- Branch overview
- Revenue
- Members
- Reports
- Staff
- Settings

#### Front Desk

- Check-in
- Member search
- New member
- Payments
- Renewals
- Today's classes
- Today's PT sessions

#### Trainer

- Today's schedule
- Clients
- Workout programs
- PT sessions
- Progress

#### Member

- Home
- Membership
- QR
- Classes
- Payments
- Attendance
- PT
- Workout
- Progress
- Profile

### 11.3 Dashboard

The owner dashboard should immediately answer:

> **How is my gym doing today?**

Top cards:

```text
Today's Revenue
₹ XX,XXX

Active Members
XXX

Today's Check-ins
XXX

Pending Dues
₹ XX,XXX

Expiring Soon
XX

Today's PT Sessions
XX
```

### 11.4 Check-in UX

```text
Scan QR
   ↓
Identify member
   ↓
Validate membership
   ↓
Show member name/photo/status
   ↓
Record attendance
   ↓
"Welcome!"
```

No unnecessary navigation should be required.

---

## 12. Roadmap / Phasing

### Phase 0 — Foundation — Week 1

- AWS environment
- Django project
- Vue application
- Authentication
- Tenant architecture
- Branch architecture
- User roles
- Database foundation
- CI/CD
- Logging

### MVP — Weeks 2–8

#### Week 2 — Members & Memberships

- Member CRUD
- Search/filter
- Member profile
- Membership plans
- Membership lifecycle
- Freeze/hold
- Renewal

#### Week 3 — Attendance

- QR generation
- QR scanning
- Staff check-in
- Attendance history
- Eligibility validation
- Basic biometric/RFID adapter interface

#### Week 4 — Billing

- Invoices
- Payments
- Razorpay
- Webhooks
- Payment history
- Outstanding dues
- Renewal payment

#### Week 5 — Classes & PT

- Class management
- Trainer calendar
- Capacity
- Booking
- Cancellation
- PT packages
- PT sessions

#### Week 6 — Member Portal + Workout

- Member dashboard
- Membership
- Payments
- Booking
- Attendance
- Workout plans
- Workout logging
- Progress

#### Week 7 — Staff + Reporting

- Staff management
- Trainer management
- Owner dashboard
- Revenue reports
- Attendance reports
- Membership reports

#### Week 8 — Production Readiness

- Notifications
- Data migration
- Security testing
- Performance testing
- UAT
- Bug fixing
- Production deployment

### Phase 2 — Post-MVP

- Native mobile applications
- WhatsApp automation
- Advanced CRM
- Lead campaigns
- Advanced analytics
- Biometric vendor integrations
- RFID/access control
- Trainer compensation automation
- Advanced member progress
- Push notifications
- Member referral system

### Phase 3 — Advanced Platform

- AI workout recommendations
- AI retention/churn prediction
- Nutrition
- Advanced marketing automation
- Franchise management
- Accounting integrations
- Inventory/POS
- Advanced payroll
- Public gym website
- White-label mobile apps
- API marketplace

---

## 13. Risks & Open Questions

### 13.1 Technical Risks

#### Payment gateway dependency

Recurring payments depend on gateway capabilities, mandate rules and webhook reliability.

**Mitigation:** Create a provider-agnostic payment interface.

```text
PaymentService
      ↓
PaymentProvider Interface
      ↓
RazorpayProvider
StripeProvider
FutureProvider
```

#### Biometric compatibility

Different gyms may use different hardware vendors.

**Mitigation:** Use an integration adapter.

```text
Gym Portal
    ↓
Access Control Interface
    ↓
Vendor Adapter
    ├── Vendor A
    ├── Vendor B
    └── Vendor C
```

#### Migration quality

Legacy data may contain duplicates, missing phone numbers, invalid dates, duplicate payments and inconsistent membership status.

**Mitigation:**

```text
Upload
 ↓
Validate
 ↓
Preview errors
 ↓
Fix/download error file
 ↓
Confirm
 ↓
Import
 ↓
Import report
```

Never directly insert uploaded CSV data into production tables.

### 13.2 Adoption Risks

#### Staff resistance

Staff may continue using WhatsApp/Excel.

**Mitigation:** Optimize the most frequently used workflows.

#### Owner does not trust reports

If financial reports do not match bank/gateway data, adoption will suffer.

**Mitigation:** Maintain payment IDs, gateway IDs, audit logs, refund history and reconciliation reports.

### 13.3 Product Risks

The biggest MVP risk is attempting to build full CRM, accounting, native mobile, AI and hardware integrations within eight weeks.

The MVP should focus on:

**Member → Membership → Attendance → Payment → Booking → PT → Member self-service**

### Open Questions

| Question | Decision |
|---|---|
| Native mobile app in V1? | No; responsive web assumed |
| Payment provider | Razorpay V1 |
| WhatsApp provider | TBD |
| SMS provider | TBD |
| Biometric vendor | TBD |
| GST invoice rules | Confirm with finance/legal |
| Membership freeze policy | Gym-configurable |
| Cross-branch membership | Configuration required |
| Trial membership | Recommended |
| Lead CRM | Should |
| Accounting integration | Phase 2 |
| Native mobile apps | Phase 2 |

---

## 14. Appendix

### 14.1 Gym Industry Glossary

| Term | Meaning |
|---|---|
| **Active Member** | Member whose membership is currently valid |
| **Expired Member** | Member whose membership end date has passed |
| **Freeze/Hold** | Temporary suspension of membership validity |
| **Renewal** | Extension or creation of a new membership after expiry |
| **Walk-in** | Person visiting without an existing scheduled booking/membership |
| **PT** | Personal Training |
| **PT Package** | Pre-purchased number of personal training sessions |
| **No-show** | Member who booked but did not attend |
| **Check-in** | Recording a member's gym arrival |
| **Class Capacity** | Maximum members allowed in a class |
| **Waitlist** | Queue of members waiting for a full class |
| **Trial** | Temporary membership/access period used to acquire a new member |
| **Churn** | Members who stop/allow their memberships to lapse |
| **ARPU** | Average Revenue Per User |
| **UPI AutoPay** | Recurring payment authorization using UPI |
| **Branch** | Physical gym location belonging to an organization |

### Competitor/Market Feature Benchmark

| Capability | Gym Portal | Glofox | Indian Gym Platforms |
|---|:---:|:---:|:---:|
| Member Management | ✓ | ✓ | ✓ |
| Membership Billing | ✓ | ✓ | ✓ |
| Recurring Payments | ✓ | ✓ | ✓ |
| QR Check-in | ✓ | ✓ | ✓ |
| Biometric Adapter | Planned | Integration | Common |
| Classes | ✓ | ✓ | ✓ |
| PT | ✓ | ✓ | ✓ |
| Trainer Management | ✓ | ✓ | ✓ |
| Workout Tracking | ✓ | Partial/varies | ✓ |
| Member Self-Service | ✓ | ✓ | ✓ |
| Multi-Branch | ✓ | ✓ | ✓ |
| CRM | Should | ✓ | ✓ |
| WhatsApp | Planned | Messaging support | Common |
| UPI | ✓ | Market-dependent | ✓ |
| GST-oriented India billing | ✓ | Market-dependent | Common |
| Accounting Integration | Phase 2 | Available/varies | Varies |

### MVP MoSCoW Summary

| Module | Priority |
|---|---|
| Member Management | **Must** |
| Membership Plans/Renewals | **Must** |
| Freeze/Hold | **Must** |
| Attendance | **Must** |
| QR Check-in | **Must** |
| Biometric/RFID Adapter | **Should** |
| Billing | **Must** |
| Razorpay | **Must** |
| Recurring Billing | **Must** |
| Invoices | **Must** |
| Classes | **Must** |
| Class Booking | **Must** |
| PT | **Must** |
| Trainer Management | **Must** |
| Workout Tracking | **Must** |
| Progress Tracking | **Must** |
| Member Portal | **Must** |
| Multi-Branch | **Must** |
| Owner Dashboard | **Must** |
| Core Reports | **Must** |
| Notifications | **Must** |
| Lead CRM | **Should** |
| WhatsApp Automation | **Should** |
| Native Mobile App | **Later** |
| Accounting Integration | **Later** |
| AI Coaching | **Later** |
| Advanced Payroll | **Later** |
| POS/Inventory | **Later** |

## Product North Star

The product should make a gym owner's daily workflow possible from one system:

**Acquire → Register → Sell membership → Collect payment → Check in → Schedule → Train → Track progress → Renew → Retain**

The most important V1 workflows are:

**Membership renewal + payment collection + member retention.**
