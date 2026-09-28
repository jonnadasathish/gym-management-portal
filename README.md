# Gym Management Portal

Multi-location gym operations SaaS for India: members, memberships, attendance, billing, classes, personal training, and a member portal.

Product baseline: [`PRD.md`](PRD.md) (v1.0, 24 Sep 2026).  
Engineering rules: [`AGENTS.md`](AGENTS.md).  
Living implementation state: [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md).

This repository is a **V1 development snapshot**. It is not production-ready and is not a complete PRD delivery.

## Stack

| Layer | Choice |
|---|---|
| Frontend | Vue 3, Vite, Pinia, Vue Router |
| Backend | Django 5, Django REST Framework |
| API | `/api/v1/` |
| Auth | JWT access token (memory) + rotating httpOnly refresh cookie |
| Database | MySQL 8 |
| Jobs | Redis + Celery |
| Payments | Provider interface; Razorpay is the V1 gateway (live HTTPS not verified) |
| Currency / timezone | INR / IST |

Roles: `OWNER`, `STAFF_ADMIN`, `TRAINER`, `MEMBER`.

## Local development

Docker Compose is the supported path. Host ports `3306` and `6379` are **not** published (they stay on the compose network). The UI and API are published.

```bash
cp .env.example .env
docker compose up --build
```

| Service | URL |
|---|---|
| Vue app | http://localhost:5173 |
| Django API | http://localhost:8000/api/v1/ |
| Liveness | http://localhost:8000/healthz/ |
| Readiness (DB + Redis) | http://localhost:8000/readyz/ |

Apply migrations once the backend container is up:

```bash
docker compose exec backend python manage.py migrate
```

Create the first owner in Django (there is no committed demo seed):

```bash
docker compose exec backend python manage.py shell
```

```python
from organizations.models import Organization
from branches.models import Branch
from accounts.models import User

org = Organization.objects.create(name="Demo Gym")
branch = Branch.objects.create(organization=org, name="Main")
User.objects.create_user(
    email="owner@example.com",
    password="ChangeMe123!",
    full_name="Demo Owner",
    role="OWNER",
    organization=org,
    home_branch=branch,
)
```

Sign in at http://localhost:5173/login.

## Tests

```bash
docker compose run --rm backend pytest -q
docker compose run --rm frontend sh -c "npm test -- --run && npm run build"
```

Last recorded backend run after GYM-018: **245 passed**. Frontend: Vitest + `vite build`.

## Repository layout

```text
PRD.md                 Product requirements
AGENTS.md              Agent / engineering contract
PROJECT_CONTEXT.md     Current state, decisions, iterations
.env.example           Non-secret environment template
docker-compose.yml     db, redis, backend, celery, frontend
backend/               Django project (`gymportal`) and domain apps
frontend/              Vue app
```

## What is in V1 (implemented locally)

Staff and member flows for register → sell membership → cash collect → check-in (search + QR) → class booking → PT → workouts/progress → renew → portal. Owner dashboard (JSON + CSV), freeze request + staff approve, login throttle, tenant-scoped APIs.

## What is not done

Do not expect these to work in this snapshot:

- Live Razorpay checkout (keys empty; `FakePaymentProvider` is used when keys are unset)
- Recurring subscription charge / retry
- Waitlist auto-promotion (intentionally off)
- GST legal invoice columns
- WhatsApp / SMS vendors (console / in-app only)
- AWS, backups, production hardening
- PDF receipts / reports

See `PROJECT_CONTEXT.md` §1 and the requirement table for status.

## Secrets

Never commit `.env`. Copy `.env.example` and replace `DJANGO_SECRET_KEY` before any real environment. Razorpay keys stay empty until a test-mode account is configured.

## License

Unspecified. Internal project unless a license file is added.
