# File 2 — Backend Track: FastAPI + PostgreSQL, Paced for Beginners

> **Who this file is for:** whoever on the team is focusing on the backend (and Kelvin, moving between both). This is a **week-by-week curriculum**, not a code dump — each week has a small learning goal, a small building goal, and a checkpoint to demo at the weekend sync. For full code and deep explanations of *why* things are structured this way, this file points back to the two earlier deep-dive guides (`pharmacy_fastapi_guide.md` and `pharmacy_fastapi_auth_bugs.md`) — treat those as your reference manual, and this file as your pace-setter.

---

## Table of Contents

1. [Before Week 1 — Setup Checklist](#1-before-week-1--setup-checklist)
2. [Week 1 — Environment & "Hello World"](#week-1--environment--hello-world)
3. [Week 2 — Your First Real Model](#week-2--your-first-real-model)
4. [Week 3 — Relationships (Medicine ↔ Batch ↔ Supplier)](#week-3--relationships-medicine--batch--supplier)
5. [Week 4 — CRUD Routes for Everything So Far](#week-4--crud-routes-for-everything-so-far)
6. [Week 5 — Staff, Customer, and the Sale Skeleton](#week-5--staff-customer-and-the-sale-skeleton)
7. [Week 6 — The Real Sale Logic (Stock Deduction)](#week-6--the-real-sale-logic-stock-deduction)
8. [Week 7 — Talking to the Frontend Properly (CORS + API Contract)](#week-7--talking-to-the-frontend-properly-cors--api-contract)
9. [Weeks 8–9 — Authentication](#weeks-89--authentication)
10. [Weeks 10–11 — Reporting Endpoints](#weeks-1011--reporting-endpoints)
11. [How to Unblock Yourself](#how-to-unblock-yourself)

---

## 1. Before Week 1 — Setup Checklist

Do this once, carefully, before writing any application code:

- [ ] Install `uv` (see Section 2 of the main FastAPI guide).
- [ ] Install PostgreSQL locally, or via Docker if you're already comfortable with it (don't learn Docker *and* Postgres *and* FastAPI in the same week — pick local install first if this is new).
- [ ] Create the database: `CREATE DATABASE pharmacy_db;`
- [ ] `uv init backend` inside the shared repo, confirm `uv run uvicorn app.main:app --reload` gives you *something* (even a default page) before moving on.
- [ ] Push this to the shared repo on your own branch, open a PR, get it merged. This is your very first rep of the team's Git workflow (File 1, Section 6) — do it even though the code is trivial. The goal this week is the *workflow*, not the code.

---

## Week 1 — Environment & "Hello World"

**Learning goal:** understand what `uv`, `uvicorn`, and FastAPI's auto-generated `/docs` page actually are.

**Building goal:** a `main.py` with a single `GET /` route, running locally, visible at `http://localhost:8000/docs`.

**Do this, don't skip it:** open `/docs` and click "Try it out" on your root route. This page is going to be your single most-used tool for the rest of the project — it lets you test every route without needing the frontend to exist yet. Get comfortable with it now.

**Checkpoint for the weekend sync:** show `/docs` on a screen share, hit the root route live.

---

## Week 2 — Your First Real Model

**Learning goal:** what an ORM model actually is — a Python class that becomes a database table. Understand `Base`, `engine`, `SessionLocal`, and the `get_db` dependency (Section 6 of the main guide covers this in full — read it slowly this week, it's the foundation everything else sits on).

**Building goal:**
- Set up `app/core/database.py` and `app/core/config.py` exactly as shown in the main guide.
- Build **one** model: `Category` (just `id`, `name`, `description`).
- Confirm the table actually gets created in Postgres — open a DB client (pgAdmin, TablePlus, or even `psql` in the terminal) and look at the table with your own eyes. Don't just trust that it worked.

**Checkpoint:** show the `categories` table existing in the database, created from your Python code.

---

## Week 3 — Relationships (Medicine ↔ Batch ↔ Supplier)

**Learning goal:** one-to-many relationships in SQLAlchemy — foreign keys and the `relationship()` function. Read Section 3 of the main guide (the design *thinking process*) again this week — the "why is Batch a separate table from Medicine" reasoning is the single most important concept in this whole project.

**Building goal:** add `Medicine`, `Supplier`, and `Batch` models, fully connected via foreign keys, following the main guide's code exactly.

**Slow-down tip:** don't just copy-paste the three models in one sitting. Build `Medicine` alone first, confirm the table exists, *then* add `Supplier`, confirm it, *then* add `Batch` last (since it depends on both). Building one piece at a time and checking each one is how you catch mistakes early instead of debugging three new tables at once.

**Checkpoint:** show all four tables in Postgres, and show the foreign key columns (`medicine_id`, `supplier_id`) actually pointing to the right tables.

---

## Week 4 — CRUD Routes for Everything So Far

**Learning goal:** the four-layer pattern — `models/` → `schemas/` → `crud/` → `routers/` (Section 5 and 10 of the main guide). Understand *why* it's split this way, not just how.

**Building goal:** for `Medicine` specifically, build the full stack: `MedicineCreate`/`MedicineOut` schemas, `crud/medicine.py` with `create_medicine`/`get_medicines`/`get_medicine`, and `routers/medicines.py` wired into `main.py`.

**This week's real test:** use `/docs` to create 3–4 medicines, then list them, then fetch one by ID. If all three work, you've proven the entire pattern works — repeating it for `Category`, `Supplier`, and `Batch` next week is now just repetition of a pattern you understand, not new concepts.

**Checkpoint:** live demo creating and listing medicines through `/docs`.

---

## Week 5 — Staff, Customer, and the Sale Skeleton

**Learning goal:** many-to-many relationships and junction tables — this is genuinely the hardest new concept in the whole schema, so give it real time. Re-read Section 3, Step 4 of the main guide (the relationship table) until the `Sale` ↔ `SaleItem` ↔ `Medicine` structure actually makes sense, not just looks familiar.

**Building goal:** add `Staff`, `Customer`, `Sale`, and `SaleItem` models. Don't build the sale *logic* yet — just get the tables existing and connected correctly first.

**Checkpoint:** show the four new tables, and be ready to explain out loud (to a teammate, on the call) why `SaleItem` exists as its own table instead of `Sale` just having a list of medicine IDs.

---

## Week 6 — The Real Sale Logic (Stock Deduction)

**Learning goal:** business logic that spans multiple tables in one transaction — what happens if something fails halfway through.

**Building goal:** implement `crud/sale.py`'s `create_sale` function from Section 9 of the main guide. Type it out yourself rather than copy-pasting — this function is doing a lot (expiry check, stock check, deduction, price snapshot, total calculation) and typing it forces you to actually read each line.

**Test deliberately:** try to sell more than what's in stock (should fail cleanly). Try to sell an expired batch (should fail cleanly). Try a normal sale (should succeed and the batch's `quantity_in_stock` should visibly decrease).

**Checkpoint:** demo all three of those test cases live.

---

## Week 7 — Talking to the Frontend Properly (CORS + API Contract)

This is the week backend and frontend tracks meet. Coordinate directly with your frontend teammate this week — don't do it in isolation.

**Learning goal:** what CORS is and why browsers block frontend-to-backend requests by default across different ports (`localhost:5173` talking to `localhost:8000` looks like "different origins" to a browser, even on the same machine).

**Building goal:** add CORS middleware to `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # the Vite dev server's default address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Also this week — write the API contract.** Sit with your frontend teammate and, together, write down (in a shared doc, or a `API_CONTRACT.md` file in the repo root) exactly what each endpoint expects and returns:

```
GET  /medicines/           -> list of { id, name, generic_name, unit, requires_prescription, sell_price, category_id }
POST /medicines/           <- { name, generic_name, unit, requires_prescription, sell_price, category_id }
                            -> the created medicine object
```

This might feel like unnecessary paperwork, but for a beginner team it prevents an extremely common failure mode: backend changes a field name, frontend breaks, and nobody knows why for an hour. Real teams call this an "API contract" and it's worth the habit early.

**Checkpoint:** frontend successfully fetches real medicine data from the backend and it renders on screen, with no CORS errors in the browser console.

---

## Weeks 8–9 — Authentication

Follow the dedicated auth guide (`pharmacy_fastapi_auth_bugs.md`) directly — it's already structured as its own two-week-sized unit, including the intentional bug hunt. Do the bug hunt seriously; it teaches JWT debugging faster than reading working code ever would.

**Checkpoint (end of Week 9):** signup → login → authorized request to a protected route (`POST /sales/`) works end to end, live, on the call.

---

## Weeks 10–11 — Reporting Endpoints

**Learning goal:** writing slightly more complex queries — filtering by date ranges and thresholds.

**Building goal:** two new endpoints:

```python
@router.get("/reports/low-stock")
def low_stock(threshold: int = 10, db: Session = Depends(get_db)):
    return db.query(Batch).filter(Batch.quantity_in_stock < threshold).all()
```

```python
@router.get("/reports/expiring-soon")
def expiring_soon(days: int = 30, db: Session = Depends(get_db)):
    from datetime import date, timedelta
    cutoff = date.today() + timedelta(days=days)
    return db.query(Batch).filter(Batch.expiry_date <= cutoff).all()
```

These two routes are small, but they're the payoff moment of the whole project — this is genuinely useful software a real pharmacy owner would want. Point this out to the team at the sync; it's good for morale.

**Checkpoint:** both endpoints return sensible results against real test data your team entered over the past 10 weeks.

---

## How to Unblock Yourself

When something doesn't work (and it will, often), work through these in order before pinging the group chat:

1. **Read the actual error message, the whole thing**, especially the last few lines of a traceback — that's usually where the real cause is.
2. **Check `/docs`** — send the exact request there and see the raw response; it's often clearer than whatever error the frontend shows.
3. **Add a `print()`** right before the line that's failing, to check what a variable actually contains versus what you assumed it contains.
4. **Check the obvious first:** is the database running? Is the `.env` file correct? Did you forget to restart the server after a change to `.env`?
5. *Then* ask the team — with the "expected vs actual, what I tried" format from File 1, Section 9.
