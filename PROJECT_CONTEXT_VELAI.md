# Velai (Campus Gigs): Project Context

> Read this file before every task. It is the source of truth for scope, stack, data model and rules. If a request conflicts with this file, ask before proceeding.

## 1. What Velai is

A campus-only marketplace for ONE college. Clubs, departments and approved local businesses post small paid jobs (posters, reels, websites, data entry, photography, tutoring). Students with the right skills take them. AI turns a rough request into a clear brief and a fair price range. Every completed gig builds the student's verified portfolio.

**One-line pitch:** Velai is the campus job board where AI turns a rough request into a clear brief and fair price, and every finished job builds the student's verified portfolio.

**Four jobs:** Post (brief builder) · Match (skill fit) · Deliver (agree, chat, hand over, approve, pay) · Prove (verified portfolio).

## 2. Roles

| Role | Can do |
|---|---|
| student | Browse gigs, apply, deliver, post gigs for their own club, build portfolio |
| staff | Post gigs for their department, approve work |
| admin | Approve organisations, moderate, resolve disputes, view analytics |

Organisations: `club`, `department`, `business`. Businesses must be admin-approved before posting.

## 3. Tech stack (fixed, do not swap without asking)

- **Mobile app:** Expo (React Native) + TypeScript + Expo Router
- **Admin and public portfolio web:** Next.js + TypeScript
- **API:** FastAPI (Python), Pydantic, SQLAlchemy, Alembic
- **Database:** PostgreSQL (+ pgvector for matching in Phase 2)
- **Realtime chat:** WebSockets via FastAPI
- **Queue and workers:** Redis + RQ (or Celery)
- **Push:** Firebase Cloud Messaging
- **Storage:** S3-compatible bucket, malware scan on uploads
- **Auth:** JWT, role-based access, college email (email OTP first, Google Workspace OAuth later)
- **Payments:** Razorpay or Cashfree, TEST MODE ONLY
- Add a `college_id` column to the main tables from day one.

## 4. Build phases

Build ONLY the current phase. Do not start later phases unless told.

**Phase 1: MVP**
1. College-email login and onboarding (name, department, year, skills with level, up to 3 sample links, availability)
2. Organisations (club, department) with verified owner
3. Post a gig: category, description, budget range, deadline, deliverables, number of revisions (structured form)
4. Gig feed with filters (category, budget, deadline, matches my skills)
5. Apply with pitch, optional sample, proposed price and time
6. Poster accepts an applicant. Both confirm the agreement (scope, price, deadline, revisions)
7. In-app chat per gig with file sharing
8. Deliver, approve, or request a revision (limited to the agreed number)
9. Ratings both ways
10. Notifications (new matching gig, applicant, accepted, delivered, deadline near)
11. Payment RECORDING only: pay directly by UPI outside the app, both sides tap "paid" and "received"
12. Admin web: approve organisations, moderation list

**Phase 2: Wow layer**
- AI brief builder: text or voice request to structured brief, price range, timeline, clarifying questions. Poster edits before publishing
- Fair price guidance from category bands, then completed-gig data
- Smart matching: embeddings plus rating, on-time rate, availability. Return a plain-language reason. Invite top-fit students
- Auto-built verified portfolio: AI drafts an entry from a completed gig, poster approves, shareable public page (student controls visibility)

**Phase 3: Stretch**
- Payment gateway in test mode with release on approval
- Dispute flow with admin decision
- Team gigs with roles and split pay
- Fest mode (bulk posting, volunteer slots)
- Reputation score and levels
- Admin analytics dashboard
- Deadline risk nudges

## 5. Gig lifecycle (state machine)

`Draft → Open → InProgress → Delivered → Completed`

Other transitions:
- Open → Expired (deadline passes), Open → Cancelled (poster cancels)
- Delivered → InProgress (revision requested)
- InProgress or Delivered → Disputed → Completed or Cancelled (admin decides)

Rules:
- Revisions limited to the agreed number. More revisions need a new agreement.
- If a poster ignores a delivery, remind them, then escalate to admin.
- Only Completed gigs create portfolio entries and count toward reputation.
- Enforce transitions in one place in the backend. Reject invalid transitions with a clear error.

## 6. Database tables

`users`, `skills`, `user_skills`, `organizations`, `org_members`, `gigs`, `gig_skills`, `applications`, `contracts`, `messages`, `deliverables`, `payments`, `reviews`, `portfolio_items`, `disputes`, `notifications`, `embeddings`, `reports`, `audit_logs`

Key fields:

- **users:** id, college_id, college_email, name, department, year, role, reputation, created_at
- **user_skills:** user_id, skill_id, level, sample_links
- **organizations:** id, name, type, verified_status, owner_id
- **gigs:** id, org_id, poster_id, title, category, description, deliverables (json), budget_min, budget_max, deadline, revisions, status, ai_brief (json), created_at
- **applications:** id, gig_id, user_id, pitch, sample_url, proposed_price, proposed_days, fit_score, fit_reason, status
- **contracts:** id, gig_id, doer_id, price, deadline, revisions, confirmed_by_poster_at, confirmed_by_doer_at
- **messages:** id, gig_id, sender_id, body, attachment_url, created_at
- **deliverables:** id, contract_id, file_url, note, version, status (submitted, accepted, revision)
- **payments:** id, contract_id, amount, method, gateway_ref, status, paid_at
- **reviews:** id, contract_id, reviewer_id, reviewee_id, rating, text, tags
- **portfolio_items:** id, user_id, contract_id, title, summary, skills, preview_url, poster_approved, visibility (private, college, public)
- **disputes:** id, contract_id, raised_by, reason, evidence, status, decision, decided_by

## 7. API surface (REST)

- **Auth/profile:** `POST /auth/login`, `GET/PATCH /me`, `PUT /me/skills`
- **Orgs:** `POST /orgs`, `GET /orgs/{id}`, `POST /admin/orgs/{id}/approve`
- **Gigs:** `POST /gigs/brief` (AI draft), `POST /gigs`, `GET /gigs`, `GET /gigs/{id}`, `PATCH /gigs/{id}`, `POST /gigs/{id}/cancel`
- **Applications:** `POST /gigs/{id}/applications`, `GET /gigs/{id}/applications`, `POST /applications/{id}/accept`
- **Contracts:** `POST /contracts/{id}/confirm`, `GET /contracts/{id}`
- **Chat:** `GET/POST /gigs/{id}/messages`, WebSocket `/ws/gigs/{id}`
- **Delivery:** `POST /contracts/{id}/deliver`, `POST /deliverables/{id}/approve`, `POST /deliverables/{id}/revise`
- **Payments:** `POST /contracts/{id}/pay`, `POST /webhooks/payments`
- **Reviews and portfolio:** `POST /contracts/{id}/review`, `GET /users/{id}/portfolio`, `POST /portfolio/{id}/approve`
- **Disputes:** `POST /contracts/{id}/dispute`, `PATCH /admin/disputes/{id}`
- **Notifications:** `GET /notifications`, `PUT /me/notification-prefs`, `POST /devices`
- **Admin:** `GET /admin/analytics`, `GET /admin/moderation`

## 8. Key logic

**Brief builder:** LLM returns strict JSON: title, tasks, deliverables, skills, price_min, price_max, timeline_days, clarifying_questions (max 2). Validate with Pydantic. If the model fails, return an empty form. Never publish without poster review.

**Price guidance:** category-based bands first. Once enough completed gigs exist, adjust using similar completed gigs. Always show the range and the reason.

**Matching:** embed gig text and student skills and past work. Rank by skill fit, then rating, on-time rate, availability, relevant samples. Return a plain-language reason. Fallback: skill tag match.

**Reputation:** Bayesian-smoothed average rating combined with on-time rate and completion rate. Formula must be visible to users.

**Notifications:** relevance threshold, max 3 pushes per user per day, per-topic mute, quiet hours.

## 9. Trust, safety and policy rules

- Sign-in limited to verified college emails. Organisations need a verified owner. Businesses need admin approval.
- New users have a small cap on open gigs and applications until they build history.
- **Academic dishonesty is not allowed:** no assignment writing, exam help or impersonation. Flag with AI plus keyword rules, surface to admin, allow reports.
- Budget must be shown on every gig. No unpaid "exposure" gigs.
- Chat stays in the app. Do not expose phone numbers or emails.
- Report and block on every gig, message and profile.
- Dispute flow decided by a named admin or faculty owner. Keep an audit log.

## 10. Payments rules

- Phase 1: record-only. Do NOT hold any money. Do NOT build real escrow.
- Phase 3: payment gateway in TEST MODE only. Label it clearly as test mode in the UI.
- Never store card or UPI credentials. The gateway handles them.
- Do not enable live payments without explicit approval and a compliance check.

## 11. Security and privacy rules

- TLS everywhere, encryption at rest, no secrets in code, `.env.example` provided.
- Role-based access on every endpoint. Validate all inputs.
- Rate limit posting, applying, chat and uploads.
- Limit file types and sizes. Scan uploads. Use signed, expiring links for private files.
- Portfolio visibility chosen by the student. Entries need poster approval, and posters can request removal of anything about their organisation.
- Provide data export and account deletion. Design consent and retention around India's DPDP Act, 2023.

## 12. UI and design rules

- Bottom tabs: Gigs, My work, Post, Chats, Me. The Post button is large and central. Posting a gig should take under a minute.
- Colours: deep navy text, green for actions and money, amber only for verified and highlight moments.
- Rounded sans-serif headings, readable body, large tap targets, dark mode, large-text support.
- Empty states say what to do next, e.g. "No gigs yet. Post the first one."
- Sentence-case buttons that say what they do. Confirmation toasts reuse the same verb ("Posted", "Accepted").
- Errors say what went wrong and how to fix it. They don't apologize.
- Voice input is a first-class path for posting a gig.
- Explain AI output in plain words and always allow editing.

## 13. Working rules for the agent

1. For each task, first write a short plan and the files you will touch. Wait for approval.
2. Build backend first, with seed data (15 sample gigs, 5 organisations, 30 sample users) and auto-generated API docs.
3. Then the mobile app, then the admin web.
4. Clean, typed, commented code. Add a README and `.env.example`.
5. Add tests for auth, the gig state machine (including invalid transitions), apply and accept, and revision limits.
6. After every milestone, say exactly how to run and test it.
7. Every AI output must be editable, explained or approved by a human, with a non-AI fallback.
8. Do not add features outside the current phase. Flag ideas instead of building them.

## 14. Definition of done (Phase 1)

- Two phones can complete one full gig: post, apply, accept, chat, deliver, approve, record payment, rate.
- Invalid state transitions are rejected and tested.
- Notification cap and mute work.
- Seed data loads with one command.
- README explains setup in under 10 steps.
