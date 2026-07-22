# LearnSphere

A multi-tenant Learning Management System, built as a system-design
portfolio project: organizations onboard instructors and learners under
one invite-coded workspace, instructors build courses with quizzes and
assignments, learners enroll and earn certificates, and every
organization's data stays completely invisible to every other
organization - all on one shared platform.

Backend: **Django REST Framework, PostgreSQL (one database per service),
Redis, RabbitMQ.** Frontend: **React + TypeScript, Vite, TanStack Query,
Zustand, Tailwind CSS.**

## Architecture

```mermaid
flowchart TB
    Client["React + TypeScript<br/>TanStack Query · Zustand · Tailwind"]

    Client --> Gateway["Nginx API Gateway<br/><sub>routing · rate limiting · CORS</sub>"]

    subgraph Services["Microservices"]
        direction LR
        Auth["Auth Service<br/><sub>:4001</sub>"]
        Learning["Learning Service<br/><sub>:4002</sub>"]
        Assessment["Assessment Service<br/><sub>:4003</sub>"]
        Communication["Communication Service<br/><sub>:4004</sub>"]
        Media["Media Service<br/><sub>:4005</sub>"]
        Analytics["Analytics Service<br/><sub>:4006</sub>"]
        Admin["Admin Service<br/><sub>:4007</sub>"]
    end

    Gateway -->|/api/auth| Auth
    Gateway -->|/api/learning| Learning
    Gateway -->|/api/assessment| Assessment
    Gateway -->|/api/communication| Communication
    Gateway -->|/api/media| Media
    Gateway -->|/api/analytics| Analytics
    Gateway -->|/api/admin| Admin

    Auth -.->|"creates org / resolves invite code"| Admin
    Assessment -.->|"never - fully decoupled"| Learning
    Communication -.->|"resolves email, course title"| Auth
    Communication -.->|"resolves course title"| Learning

    Auth --> AuthDB[("Postgres · auth_db")]
    Learning --> LearningDB[("Postgres · learning_db")]
    Assessment --> AssessmentDB[("Postgres · assessment_db")]
    Communication --> CommDB[("Postgres · communication_db")]
    Media --> MediaDB[("Postgres · media_db")]
    Analytics --> AnalyticsDB[("Postgres · analytics_db")]
    Admin --> AdminDB[("Postgres · admin_db")]
    Media --> Store[("local disk / S3")]
    Learning -.->|"cache-aside: course details only"| Redis[("Redis")]

    classDef svc fill:#1E1B4B,stroke:#4C1D95,color:#fff
    classDef store fill:#FAF9FC,stroke:#F97362,color:#1E1B4B
    class Auth,Learning,Assessment,Communication,Media,Analytics,Admin svc
    class AuthDB,LearningDB,AssessmentDB,CommDB,MediaDB,AnalyticsDB,AdminDB,Store,Redis store
```

Three services make direct HTTP calls to another service (dotted lines
above) - Auth resolving an invite code through Admin at signup, and
Communication resolving an email or course title before sending a
notification. Everything else that changes state another service cares
about - a new enrollment, a graded quiz - goes through RabbitMQ instead:

```mermaid
sequenceDiagram
    participant L as Learning Service
    participant Q as RabbitMQ (topic exchange)
    participant C as Communication Service
    participant An as Analytics Service

    L->>Q: publish EnrollmentCreated (routing key)
    par each service has its own durable queue
        Q-->>C: EnrollmentCreated
        Q-->>An: EnrollmentCreated
    end
    C->>C: email the learner + notify the instructor
    An->>An: increment today's enrollment counter

    Note over Q: If Communication Service is briefly down, its queue<br/>holds the message until it reconnects - nothing is lost.
```

The same fan-out pattern handles `AssessmentCompleted` and
`CertificateIssued`. Full event catalog: `UserRegistered` ·
`OrganizationCreated` · `CoursePublished` · `EnrollmentCreated` ·
`AssessmentCompleted` · `CertificateIssued`.

The event bus is a genuine RabbitMQ topic exchange with **durable
per-service queues** - not a simplified pub/sub shortcut. Every service
that binds a queue to `domain_events` gets its own durable copy of a
matching event, so Communication Service and Analytics Service each
process the same `EnrollmentCreated` event independently, and an event
published while a service is mid-deploy is still waiting for it on
restart instead of being dropped.

Each service that consumes events (`admin`, `learning`, `communication`,
`analytics`) runs as **two containers** - a `web` process (Django/Gunicorn,
handles HTTP) and a `listener` process (a long-running `pika` consume
loop, handles events). Keeping them separate means either one can restart
independently without taking down the other.

## Multi-tenancy

`organizationId` lives in the JWT claims (set once at signup, verified
locally by every service the same way as the user's `role`), and a
shared `IsTenantScoped` permission class enforces it on org-membership,
course listing, and course search. Platform admins are the one exception
and can cross tenant boundaries, which is how the platform analytics
dashboard aggregates every organization's KPIs at once.

Enforcement is not yet consistent everywhere: course detail
(`GET /courses/:id`) is intentionally public with no auth, and neither
enrollment nor a few other course-scoped reads (instructor's enrollment
list, discussion/announcement reads) currently check that the requested
`course_id` belongs to the requester's organization - only that the
requester is authenticated with the right role. In practice this means
a course ID from another organization, if known, isn't fully walled off
yet. Worth tightening before treating tenant isolation as complete.

## Search stays inside Learning Service

Per the design doc's explicit guidance, there's no separate Search
Service. `learning-service` maintains a Postgres `SearchVectorField` +
`GinIndex` on courses (Django's `django.contrib.postgres.search` -
`SearchVector`/`SearchQuery`/`SearchRank`) and exposes
`/courses/search?q=`, updated whenever a course is created or edited.

## Service boundaries

| Service | Owns | Port |
|---|---|---|
| `auth-service` | credentials, JWT, refresh tokens | 4001 |
| `learning-service` | courses, modules, lessons, enrollment, progress, certificates, course search | 4002 |
| `assessment-service` | quizzes, questions, assignments, submissions, grades | 4003 |
| `communication-service` | discussions, announcements, in-app notifications, email | 4004 |
| `media-service` | video/PDF/image uploads (local disk by default, S3 when configured) | 4005 |
| `analytics-service` | KPIs, growth, per-course metrics | 4006 |
| `admin-service` | organizations, invite codes, subscriptions, audit logs, support tickets, platform settings | 4007 |
| `gateway` (Nginx) | routing, rate limiting, CORS | 8080 |

## Running it locally

Requirements: Docker + Docker Compose.

```bash
cp .env.example .env
docker compose up --build
```

Then open:

- **App:** http://localhost:3000
- **API gateway:** http://localhost:8080/api
- **RabbitMQ management UI:** http://localhost:15672 (learnsphere / learnsphere)

### Try the flow end to end

1. **Register** at `/register` choosing "I'm starting a new organization"
   - this creates both your account and the organization in one step and
     hands you back an invite code, visible on the `/organization` page.
2. Open an incognito window, **register again** as "I'm an instructor
   joining one" using that invite code.
3. As the instructor, go to **Instructor → New course**, add a module and
   a lesson, build a short quiz, then **Publish**.
4. Open a third window, **register as a learner** with the same invite
   code, find the course in the **Catalog**, enroll, complete the lesson,
   and take the quiz.
   - Completing every lesson auto-issues a certificate
     (`CertificateIssued` → Communication Service emails you, Analytics
     Service logs it).
5. Back in the org admin's window, check **Organization** for the
   30-day KPI counters ticking up as the learner interacts with the
   course.

### Creating a platform admin

There's no public platform-admin signup (by design). Register normally,
then flip the role directly in Postgres:

```bash
docker compose exec postgres psql -U learnsphere -d auth_db \
  -c "UPDATE accounts_user SET role = 'platform_admin', organization_id = NULL WHERE email = 'you@example.com';"
```

## Running a single service without Docker

```bash
cd services/auth-service
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgres://learnsphere:learnsphere@localhost:5432/auth_db
export JWT_ACCESS_SECRET=dev-only-jwt-secret-change-me
export RABBITMQ_URL=amqp://learnsphere:learnsphere@localhost:5672/
python manage.py migrate
python manage.py runserver 0.0.0.0:4001
```

Services that consume events (`admin`, `learning`, `communication`,
`analytics`) also need `python manage.py listen_events` running
alongside the web server, matching the extra container each gets in
`docker-compose.yml`.

## Repo layout

```
learnsphere/
├── docker-compose.yml
├── .env.example
├── infra/
│   ├── nginx/                  # API Gateway config
│   └── postgres-init/          # creates one DB per service, once, when the data volume is first created
├── services/
│   ├── auth-service/
│   ├── learning-service/
│   ├── assessment-service/
│   ├── communication-service/
│   ├── media-service/
│   ├── analytics-service/
│   └── admin-service/
└── frontend/
```

Each service follows the same shape: `config/` (Django settings, WSGI
entrypoint), one domain app (e.g. `learning/`) with `models.py`,
`serializers.py` (where used), `views.py`, `urls.py`, and - where
relevant - `rabbitmq_bus.py` (publish), `events_handlers.py` +
`management/commands/listen_events.py` (subscribe).
