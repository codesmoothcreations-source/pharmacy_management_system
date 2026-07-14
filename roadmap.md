# File 1 — Team Charter & Roadmap: Pharmacy Management System


## Table of Contents

1. [The Problem We're Solving](#1-the-problem-were-solving)
2. [Team Roles](#2-team-roles)
3. [Tech Stack](#3-tech-stack)
4. [Ground Rules](#4-ground-rules)
5. [The Weekly Ritual](#5-the-weekly-ritual)
6. [Git & GitHub Workflow for Beginners](#6-git--github-workflow-for-beginners)
7. [The Full Roadmap (Week by Week)](#7-the-full-roadmap-week-by-week)
8. [Definition of Done](#8-definition-of-done)
9. [How to Ask for Help (Without Killing Momentum)](#9-how-to-ask-for-help-without-killing-momentum)

---

## 1. The Problem We're Solving

Keep this at the top of your minds — it's what will make the project engaging instead of just "an exercise."

A small pharmacy (or chain of them) in Ghana currently tracks stock, sales, and expiry dates manually — on paper, or in someone's head. This causes real, expensive problems:

- Expired medicine gets sold because nobody was tracking expiry dates systematically.
- Stock runs out without warning because there's no low-stock alert.
- There's no record of who sold what, when, or to whom — so mistakes and losses can't be traced.
- Different batches of the same medicine (bought at different times, different prices) get mixed up.

**We are building software that solves this**, not just "a CRUD app with a database." Every feature you build should be traceable back to one of these real problems. When you're deciding what to build next and it's not obvious, ask: *"Which of these four problems does this solve?"*

---

## 2. Team Roles

| Team | Primary Focus | Also Contributes To |
|---|---|---|
| **Full** | Full-stack — glue between frontend and backend, database design, API contracts, code review for both sides | Everything — unblocking teammates, keeping the roadmap on track |
| **Backend** | FastAPI routes, SQLAlchemy models, PostgreSQL, business logic | Can suggest UI flows, test the frontend, give feedback on what data the frontend actually needs |
| **Frontend** | React UI, calling the API, forms, tables, basic styling | Can suggest what fields/data a screen needs, flag confusing API responses, test backend routes via `/docs` |

**Important team principle:** roles are a *primary focus*, not a wall. The backend person should be able to open the React project and understand roughly what's happening, and vice versa. Full separation early on, when everyone's a beginner, tends to create two people who can't talk to each other's code. Cross-review each other's pull requests even outside your specialty — you don't need to understand every line to ask "what does this do?"

---

## 3. Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Frontend:** React (with Vite)
- **API communication:** REST, JSON, via `fetch`/Axios from React to FastAPI
- **Version control:** Git + GitHub (shared repository)

We are deliberately **not** adding TypeScript, Docker, or deployment infrastructure in the first phase. Those are real, valuable skills — but adding them on day one, for a team where everyone is a learner, multiplies the number of new concepts you're all learning at once. Add them later, once the core app works, as their own dedicated phase (see the roadmap).

---

## 4. Ground Rules

These exist to keep three beginners from stepping on each other and burning out. Agree on them explicitly in your first meeting — don't assume they're obvious.

1. **Small tasks, shipped often.** A task that takes more than 2–3 days without anything committed is too big — break it down further.
2. **Commit early, commit often.** Nobody should be sitting on 4 days of uncommitted local changes. Small commits are easier to review and easier to undo if something breaks.
3. **Every feature branch, every pull request.** Even if you're the only one who'll ever look at it. This builds the habit before it matters on a bigger team.
4. **No silent blockers.** If you're stuck for more than ~30–45 minutes on something that isn't "I'm learning a new concept and reading is expected," say something in the group chat *that day*, not at the weekend call.
5. **Explain your code in the PR description**, even briefly. "Added medicine model + create/list routes" is enough. This is training for real jobs, where PR descriptions matter.
6. **It's fine to not know things.** Everyone here is a beginner. The team norm should be "ask early," never "figure it out alone in silence for 3 days."

---

## 5. The Weekly Norms

Every week, hold a sync — this is non-negotiable, it's the heartbeat of the project:

> Some thing like a conference call on the weekend,
> To know any challenges we will be facing or any thing u will like to share relating to the project

**How to run it (keep it under 30–40 minutes so it doesn't become a chore):**

1. **Round-robin update (5 min each):** each person answers three things —
   - What did I finish this week?
   - What am I working on next?
   - What's blocking me, or what am I unsure about?
2. **Demo (10–15 min):** show whatever runs, even if it's ugly. A form that submits, an endpoint that returns data in `/docs`, a table that renders with fake data — anything visible keeps morale up. Working software, however small, is the best motivator for a beginner team.
3. **Plan the coming week together:** agree on the next small milestone from the roadmap (Section 7) and who owns what.
4. **Open floor:** anything relating to the project — an idea, a concern, a "I saw this cool thing," a "I don't understand X, can someone explain."

Optional but recommended: keep a shared running doc (Google Doc, Notion, or even a `MEETING_NOTES.md` in the repo) where you jot 3–4 lines after every call — what was decided, what's next. Future-you, three weeks from now, will not remember what you agreed on this Saturday.

---

## 6. Git & GitHub Workflow for Beginners

Keep this simple — you don't need a complex branching strategy for a 3-person beginner team.

### 6.1 Repository setup

- One shared GitHub repository, e.g. `pharmacy-management-system`.
- Two folders at the root: `backend/` and `frontend/` — this is called a **monorepo** (one repository, multiple projects). Simple for a small team, no need to split into two repos yet.

```
pharmacy-management-system/
├── backend/        # the FastAPI project from the earlier guides
├── frontend/        # the React project
├── README.md        # what the project is, how to run both sides
└── MEETING_NOTES.md  # optional, running log of weekly syncs
```

### 6.2 Branching model

- `main` — always working, always deployable/demoable. Nobody commits directly to `main`.
- Feature branches, named clearly: `backend/add-medicine-model`, `frontend/medicine-list-page`, `backend/fix-auth-bug`.

### 6.3 The actual daily workflow

```bash
# start of any new task
git checkout main
git pull origin main
git checkout -b backend/add-medicine-model

# ...do your work, commit as you go...
git add .
git commit -m "Add Medicine model and category relationship"

# when ready
git push origin backend/add-medicine-model
# then open a Pull Request on GitHub into main
```

### 6.4 Pull Request rules for this team

- At least **one other team member reviews before merging** — even a quick "looks good" comment. This is the single habit that will teach all three of you the most, the fastest.
- Keep PRs small — one feature or fix per PR. A PR that touches 15 files is hard for a beginner reviewer to give useful feedback on.
- If you're stuck resolving a merge conflict, that's a **share-your-screen-on-a-call** moment, not a solo-struggle-for-2-hours moment, especially early on.

---

## 7. The Full Roadmap (Week by Week)

Paced deliberately slow — this assumes the team is part-time (studying/working alongside this) and everyone is genuinely new. Adjust pace up if the team is moving faster, but resist the urge to skip steps.

### Phase 0 — Setup (Week 1)
- Everyone gets their environment running: `uv` for backend, `npm`/Vite for frontend, PostgreSQL installed and reachable.
- Repository created, both folders scaffolded, everyone pushes a "hello world" commit successfully.
- **This week's demo:** backend shows `{"msg": "Pharmacy API is running"}` at `/`, frontend shows a default Vite React page.

### Phase 1 — Core Data, No Auth Yet (Weeks 2–4)
- Backend: `Category`, `Medicine`, `Supplier`, `Batch` models + basic CRUD routes (see `02_backend_track.md`).
- Frontend: a page that lists medicines from the API, and a form to add a new one (see `03_frontend_track.md`).
- **Team milestone:** frontend can display real data coming from the backend — this is the first moment the two sides of the project actually talk to each other, and usually the most exciting demo of the whole project so far.

### Phase 2 — Sales Flow (Weeks 5–7)
- Backend: `Staff`, `Customer`, `Sale`, `SaleItem` models + the `create_sale` logic (stock deduction, expiry check).
- Frontend: a simple "make a sale" screen — pick a medicine, pick quantity, see a running total, submit.
- **Team milestone:** a full, real business transaction works end to end — select medicine → deduct stock → record sale.

### Phase 3 — Authentication (Weeks 8–9)
- Backend: JWT login/signup (see the dedicated auth guide).
- Frontend: a login page, storing the token, sending it on protected requests, showing/hiding UI based on role.
- **Team milestone:** the app has real users now, not just an open system anyone can use.

### Phase 4 — Reporting & Polish (Weeks 10–11)
- Backend: "low stock" endpoint, "expiring soon" endpoint.
- Frontend: a simple dashboard page showing these two lists — this is genuinely useful, real functionality a pharmacy owner would want.
- Both: basic styling pass, fix rough edges, write a proper `README.md`.

### Phase 5 — Stretch Goals (Week 12+, pick based on energy/interest)
- Search/filter on the medicine list.
- Pagination.
- Simple charts (sales over time) on the dashboard.
- Deployment (this is a good moment to introduce Docker + a free hosting tier, as its own mini-project).

**Reminder:** these week numbers are a guide, not a contract. If week 3 takes two weeks, that's fine — the weekly sync is where you renegotiate the plan, not where you panic about being "behind."

---

## 8. Definition of Done

Before calling any task "done" (and closing its PR), it should meet all of these:

- [ ] It runs locally without errors.
- [ ] It was tested manually at least once (via `/docs` for backend, via clicking through the UI for frontend).
- [ ] At least one teammate reviewed the PR.
- [ ] If it's a new backend route, it's documented well enough that the frontend person could use it without asking you what it does (a clear function name + response model usually does this for free).

---

## 9. How to Ask for Help (Without Killing Momentum)

A useful habit for a beginner team, worth adopting from week 1:

1. **Try for 20–30 minutes on your own first**, and actually read the error message fully (not just the last line).
2. **Write down what you tried** before asking — even 2 sentences. This alone often makes you spot the bug yourself.
3. **Ask in the group chat with**: what you're trying to do, what you expected, what actually happened (paste the real error), what you've already tried.
4. If it's still unresolved after a teammate looks, **bring it to the weekend call** rather than letting it block you all week.

This format — "expected vs. actual, plus what I tried" — is exactly how professional developers ask for help. Building the habit now, on a low-stakes project, pays off everywhere later.