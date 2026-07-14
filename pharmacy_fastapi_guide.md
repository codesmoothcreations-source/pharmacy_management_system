# Pharmacy Management System — A Complete FastAPI + SQLAlchemy Build Guide

> **Goal of this document:** teach you *how to think* about database design and FastAPI project structure, not just hand you code. Every section explains the "why" before the "how." Read it top to bottom once, then use it as a reference while you build.

---

## Table of Contents

1. [What We're Building](#1-what-were-building)
2. [Environment Setup with `uv`](#2-environment-setup-with-uv)
3. [The Database Design Thinking Process](#3-the-database-design-thinking-process)
4. [The Final Schema (ERD in text form)](#4-the-final-schema-erd-in-text-form)
5. [Folder Structure — Best Practices](#5-folder-structure--best-practices)
6. [Core Setup: config.py and database.py](#6-core-setup-configpy-and-databasepy)
7. [SQLAlchemy Models](#7-sqlalchemy-models)
8. [Pydantic Schemas](#8-pydantic-schemas)
9. [CRUD Layer](#9-crud-layer)
10. [Routers (comparing to your current style)](#10-routers-comparing-to-your-current-style)
11. [Wiring It All Together in main.py](#11-wiring-it-all-together-in-mainpy)
12. [Step-by-Step Integration Order](#12-step-by-step-integration-order)
13. [Exercises to Test Yourself](#13-exercises-to-test-yourself)
14. [Where to Go Next](#14-where-to-go-next)

---

## 1. What We're Building

A **Pharmacy Management System** backend. Not a toy — a real one, with the problems real pharmacies actually have:

- Medicines have **expiry dates**, and expired stock must never be sellable.
- Medicines arrive in **batches** (a batch of Paracetamol bought in June expires differently than one bought in August, even though it's "the same product").
- Some medicines need a **prescription**; some don't.
- Stock levels must be tracked accurately — you can't sell more than what's in stock.
- There are **suppliers** you buy from, and **customers** you sell to.
- Staff have different **roles** (admin, pharmacist, cashier) with different permissions.

This is intentionally more complex than a blog/posts API, because that complexity is exactly what teaches you real database thinking — one-to-many, many-to-many, and *why* you split things into separate tables instead of cramming everything into one.

---

## 2. Environment Setup with `uv`

`uv` is a fast Python package/project manager (written in Rust) that replaces `pip` + `venv` + `poetry` for most use cases. Here's the full setup from zero.

### 2.1 Install uv

**On Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**On macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify it installed:
```bash
uv --version
```

### 2.2 Create the project

```bash
uv init pharmacy-api
cd pharmacy-api
```

This creates a minimal project with a `pyproject.toml`, a `.python-version`, and a `main.py`. `pyproject.toml` is uv's equivalent of `package.json` if you're coming from Node — it tracks your project's dependencies and metadata.

### 2.3 Install your dependencies

With `uv`, you don't manually create a venv first — `uv add` creates one automatically the first time you add a package (in `.venv/`), and installs into it.

```bash
uv add fastapi
uv add "uvicorn[standard]"
uv add sqlalchemy
uv add psycopg2-binary
uv add pydantic
uv add pydantic-settings
uv add python-dotenv
uv add alembic
uv add passlib[bcrypt]
uv add python-jose[cryptography]
uv add python-multipart
```

**What each one is for:**

| Package | Purpose |
|---|---|
| `fastapi` | The web framework itself |
| `uvicorn[standard]` | ASGI server that actually runs your app |
| `sqlalchemy` | The ORM — maps Python classes to database tables |
| `psycopg2-binary` | PostgreSQL driver (the thing that actually talks to Postgres) |
| `pydantic` | Data validation — FastAPI uses this under the hood for request/response schemas |
| `pydantic-settings` | Lets you load config (DB URL, secrets) from a `.env` file cleanly |
| `python-dotenv` | Reads `.env` files |
| `alembic` | Database migrations — tracks schema changes over time (like a version control system for your DB structure) |
| `passlib[bcrypt]` | Password hashing for staff/user login |
| `python-jose[cryptography]` | JWT tokens for authentication |
| `python-multipart` | Needed for form data / file uploads later |

### 2.4 Running the dev server

```bash
uv run uvicorn app.main:app --reload
```

`uv run` executes a command inside the project's virtual environment without you needing to manually activate it — similar to `npm run dev` if you're coming from Node.

### 2.5 PostgreSQL

Install Postgres locally (or use Docker). Then create a database:

```sql
CREATE DATABASE pharmacy_db;
```

You'll connect to it with a URL that looks like:
```
postgresql://username:password@localhost:5432/pharmacy_db
```

We'll put this in a `.env` file in Section 6.

---

## 3. The Database Design Thinking Process

This is the part most tutorials skip — they just show you the finished schema. But the *process* of getting there is the actual skill. Here's how a database designer actually thinks.

### Step 1 — List the "nouns" (entities)

Read the problem statement and underline every "thing" that needs to be stored:

> A pharmacy sells **medicines**. Medicines come from **suppliers** in **batches**, each with its own **expiry date**. **Staff** (admin/pharmacist/cashier) manage stock and process **sales** to **customers**. Some medicines require a **prescription**.

Nouns found: Medicine, Supplier, Batch, Staff, Sale, Customer, Prescription.

These become candidate **tables**.

### Step 2 — For each entity, ask "what do I need to know about it?"

Example for **Medicine**:
- name (Paracetamol 500mg)
- category (Painkiller, Antibiotic, etc.)
- generic name
- unit of measure (tablet, syrup, injection)
- whether it requires a prescription
- selling price

Notice: **price and quantity are NOT medicine properties** — they belong to *batches*, because different batches of the same medicine can have different cost prices (bought at different times) and different quantities. This is the first real design decision.

### Step 3 — Ask "is this really one entity, or is it secretly two?"

This is the most important skill in schema design. Beginners often make one big table. Ask yourself:

> "If I stored 'Medicine' and 'Stock Quantity' in the same row, what happens when the same medicine arrives in two different batches with two different expiry dates?"

You'd have to either:
- duplicate the medicine row (bad — now "Paracetamol" exists twice with different info, which is inconsistent), or
- have one row track only *one* expiry date (bad — you lose the ability to track multiple batches)

**This tells you Medicine and Batch must be separate tables**, linked by a relationship. This reasoning — "can this thing have more than one of this attribute over time?" — is how you catch these splits every time.

### Step 4 — Define relationships between entities

For every pair of related entities, ask: **"For one X, how many Y's? And for one Y, how many X's?"**

| Relationship | Question & Answer | Type |
|---|---|---|
| Medicine ↔ Batch | One medicine can have many batches. One batch belongs to one medicine. | **One-to-Many** |
| Supplier ↔ Batch | One supplier supplies many batches. One batch comes from one supplier. | **One-to-Many** |
| Medicine ↔ Category | One category has many medicines. One medicine belongs to one category. | **One-to-Many** |
| Sale ↔ Medicine | One sale can include many medicines, and one medicine can appear in many sales. | **Many-to-Many** (needs a join table: `sale_items`) |
| Staff ↔ Sale | One staff member processes many sales. One sale is processed by one staff member. | **One-to-Many** |
| Customer ↔ Sale | One customer can have many sales. One sale belongs to one customer (or none, for walk-ins). | **One-to-Many** |
| Prescription ↔ Sale | One prescription is linked to one sale (if the sale required one). | **One-to-One (optional)** |

**Key insight for you (coming from JS/Node thinking):** a Many-to-Many relationship *always* needs a third table in between (a "join table" or "association table"). There's no way to represent Many-to-Many with a single foreign key column — this is different from how you might casually store arrays in Mongo. In relational databases, you always resolve M:N into two 1:N relationships via a junction table.

### Step 5 — Normalize (remove duplication)

The rule of thumb: **a piece of data should live in exactly one place.** If "Supplier Name" appears in both the `batches` table and a `suppliers` table, that's duplication — if the supplier's name changes, you'd have to update it everywhere. Instead, `batches` stores a `supplier_id` (a foreign key) and *looks up* the name from `suppliers` when needed.

This is called **normalization**, and it's the same discipline as not repeating yourself in code (DRY) — just applied to data.

### Step 6 — Identify what needs timestamps, soft state, and constraints

- `expiry_date` on batches — critical, drives business logic (don't sell expired stock).
- `quantity_in_stock` on batches — must never go negative (this becomes a `CHECK` constraint or app-level validation).
- `is_active` on staff — for disabling accounts without deleting history.
- `created_at` / `updated_at` — nearly every table should have these, for auditing.

### Step 7 — Draw it out (mentally or on paper) before writing code

Before touching SQLAlchemy, sketch boxes-and-arrows. This is the ERD (Entity Relationship Diagram). Section 4 below is that diagram in text form — this is the actual deliverable of the thinking process above.

---

## 4. The Final Schema (ERD in text form)

```
┌─────────────┐        ┌──────────────┐        ┌─────────────┐
│  Category   │1      *│   Medicine   │1      *│    Batch    │
├─────────────┤────────├──────────────┤────────├─────────────┤
│ id          │        │ id           │        │ id          │
│ name        │        │ name         │        │ medicine_id │
│ description │        │ generic_name │        │ supplier_id │
└─────────────┘        │ category_id  │        │ batch_no    │
                        │ requires_rx  │        │ quantity    │
                        │ unit         │        │ cost_price  │
                        │ sell_price   │        │ expiry_date │
                        └──────────────┘        │ received_at │
                                                 └─────────────┘
                                                        *
                                                        │
                                                        1
                                                ┌───────────────┐
                                                │   Supplier    │
                                                ├───────────────┤
                                                │ id            │
                                                │ name          │
                                                │ phone         │
                                                │ email         │
                                                │ address       │
                                                └───────────────┘

┌─────────────┐        ┌──────────────┐        ┌─────────────┐
│    Staff    │1      *│     Sale     │1      *│  SaleItem   │
├─────────────┤────────├──────────────┤────────├─────────────┤
│ id          │        │ id           │        │ id          │
│ full_name   │        │ staff_id     │        │ sale_id     │
│ username    │        │ customer_id  │        │ medicine_id │
│ password    │        │ total_amount │        │ batch_id    │
│ role        │        │ created_at   │        │ quantity    │
│ is_active   │        └──────────────┘        │ unit_price  │
└─────────────┘               1                └─────────────┘
                               │                       *
                               *                       │
                        ┌──────────────┐               │
                        │   Customer   │       (links to Medicine
                        ├──────────────┤        AND Batch — so we
                        │ id           │        know exactly which
                        │ full_name    │        batch was sold from)
                        │ phone        │
                        └──────────────┘
```

**Reading this diagram:** `1` and `*` on each end of a line tell you the relationship type. `Medicine 1 ── * Batch` reads as "one Medicine has many Batches." `SaleItem` is the junction table that resolves the Sale ↔ Medicine many-to-many relationship — and it *also* links to `Batch`, which is a deliberate design choice: **when you sell a medicine, you must record which specific batch it came from**, so stock deduction and expiry tracking stay accurate.

---

## 5. Folder Structure — Best Practices

Your current code is all in one `main.py` — fine for 5 routes, unmanageable for a real system. The industry-standard approach for FastAPI is a **layered, domain-organized structure**. Here's the one we'll use, and *why* each piece exists.

```
pharmacy-api/
├── .env                        # secrets (DB url, JWT secret) — never committed to git
├── .gitignore
├── pyproject.toml              # created by uv, tracks dependencies
├── alembic.ini                 # alembic config (migrations)
├── alembic/                    # migration scripts live here
│   └── versions/
│
└── app/
    ├── __init__.py
    ├── main.py                 # creates the FastAPI() app, includes routers — the entrypoint
    │
    ├── core/                   # cross-cutting concerns, used everywhere
    │   ├── __init__.py
    │   ├── config.py           # reads .env into a typed Settings object
    │   ├── database.py         # SQLAlchemy engine, SessionLocal, Base, get_db dependency
    │   └── security.py         # password hashing + JWT creation/verification
    │
    ├── models/                 # SQLAlchemy ORM models (= your DB tables, one class per table)
    │   ├── __init__.py
    │   ├── category.py
    │   ├── medicine.py
    │   ├── supplier.py
    │   ├── batch.py
    │   ├── staff.py
    │   ├── customer.py
    │   ├── sale.py
    │   └── sale_item.py
    │
    ├── schemas/                # Pydantic models (= shape of request/response JSON)
    │   ├── __init__.py
    │   ├── medicine.py
    │   ├── batch.py
    │   ├── sale.py
    │   └── staff.py
    │
    ├── crud/                   # pure DB operations — "talk to the database" logic, no HTTP stuff
    │   ├── __init__.py
    │   ├── medicine.py
    │   ├── batch.py
    │   └── sale.py
    │
    ├── routers/                # FastAPI route handlers — the "controller" layer, thin
    │   ├── __init__.py
    │   ├── medicines.py
    │   ├── batches.py
    │   ├── sales.py
    │   ├── staff.py
    │   └── auth.py
    │
    └── dependencies.py         # shared FastAPI dependencies (e.g. get_current_user)
```

### Why split it this way? (the reasoning, not just the rule)

Think of it as **four layers, each with one job**, request flowing top to bottom:

1. **`routers/`** — receives the HTTP request, validates input shape (via `schemas/`), calls the CRUD layer, returns a response. It should contain almost **no business logic**.
2. **`schemas/`** — defines what valid input/output JSON looks like. This is *not* the database structure — it's the "contract" with whoever calls your API. E.g., you'll accept a `password` on signup but never return it in a response — schemas enforce that.
3. **`crud/`** — the actual "talk to the database" functions: `get_medicine_by_id()`, `create_batch()`, etc. This is where SQLAlchemy queries live. Keeping this separate from routers means you can reuse these functions from multiple routes, background jobs, or tests without duplicating query logic.
4. **`models/`** — the SQLAlchemy classes that map directly to tables. This is your actual database structure.

**The analogy for you, coming from Express/Node:** this is basically the same as splitting `routes/`, `controllers/`, and `models/` in an Express app — routers = your route files, crud = your controllers/services, models = your Mongoose/Prisma models, schemas = your request validation (like `zod` or `joi` schemas).

**Why not put everything in one `main.py` like your sample?** It works until it doesn't — the moment you have 8 tables and 30 endpoints, a single file becomes unreadable and merge conflicts become constant if you're now onboarding a frontend dev too (which you mentioned you're doing). Splitting by concern means two people can work in different files without stepping on each other, and you can test the `crud/` layer without spinning up the whole HTTP app.

---

## 6. Core Setup: config.py and database.py

### `.env` (project root)

```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/pharmacy_db
SECRET_KEY=change_this_to_a_long_random_string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### `app/core/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
```

**Why this exists:** instead of scattering `os.getenv("DATABASE_URL")` calls everywhere (easy to typo, no type safety), you get one typed `settings` object you import anywhere: `from app.core.config import settings`.

### `app/core/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# FastAPI dependency — gives each request its own DB session, and closes it after
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**What's happening here, piece by piece:**
- `engine` — the actual connection pool to Postgres.
- `SessionLocal` — a factory that creates new "conversations" with the DB (a Session). You get a fresh one per request — never share sessions across requests.
- `Base` — the parent class every model inherits from. SQLAlchemy uses this to know "these classes are tables."
- `get_db()` — a **generator function** used as a FastAPI dependency. The `yield` hands the session to your route function; once the route finishes (success or error), the code after `yield` runs and closes the session. You'll see `db: Session = Depends(get_db)` in every route that touches the database.

---

## 7. SQLAlchemy Models

Models are Python classes that map 1:1 to database tables. Each class attribute = a column.

### `app/models/category.py`

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

    medicines = relationship("Medicine", back_populates="category")
```

### `app/models/medicine.py`

```python
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    generic_name = Column(String, nullable=True)
    unit = Column(String, nullable=False)          # e.g. "tablet", "bottle"
    requires_prescription = Column(Boolean, default=False)
    sell_price = Column(Float, nullable=False)

    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="medicines")

    batches = relationship("Batch", back_populates="medicine")
```

### `app/models/supplier.py`

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)

    batches = relationship("Batch", back_populates="supplier")
```

### `app/models/batch.py`

```python
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_number = Column(String, nullable=False)
    quantity_in_stock = Column(Integer, nullable=False, default=0)
    cost_price = Column(Float, nullable=False)
    expiry_date = Column(Date, nullable=False)
    received_at = Column(DateTime(timezone=True), server_default=func.now())

    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    medicine = relationship("Medicine", back_populates="batches")

    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    supplier = relationship("Supplier", back_populates="batches")
```

### `app/models/staff.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="cashier")  # admin | pharmacist | cashier
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sales = relationship("Sale", back_populates="staff")
```

### `app/models/customer.py`

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)

    sales = relationship("Sale", back_populates="customer")
```

### `app/models/sale.py`

```python
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    total_amount = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    staff = relationship("Staff", back_populates="sales")

    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    customer = relationship("Customer", back_populates="sales")

    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
```

### `app/models/sale_item.py`

```python
from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)   # price AT time of sale — don't rely on medicine.sell_price later

    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    sale = relationship("Sale", back_populates="items")

    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    medicine = relationship("Medicine")

    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    batch = relationship("Batch")
```

> **Learning note:** `unit_price` is duplicated onto `SaleItem` even though `Medicine.sell_price` already exists. This is **intentional, not a normalization mistake** — if you later change a medicine's price, old sales records must still reflect the price *at the time of that sale*. This is a common real-world exception to strict normalization called capturing a "point-in-time snapshot."

### `app/models/__init__.py`

```python
from app.core.database import Base
from app.models.category import Category
from app.models.medicine import Medicine
from app.models.supplier import Supplier
from app.models.batch import Batch
from app.models.staff import Staff
from app.models.customer import Customer
from app.models.sale import Sale
from app.models.sale_item import SaleItem
```

This file matters more than it looks — importing every model here means when `Base.metadata.create_all()` runs (or Alembic autogenerates a migration), SQLAlchemy actually knows all your tables exist.

---

## 8. Pydantic Schemas

Schemas define the **shape of data going in and out of your API** — separate from the DB models. This separation is deliberate: you never want to accidentally expose a `hashed_password` field just because it exists on the model.

### `app/schemas/medicine.py`

```python
from pydantic import BaseModel

class MedicineBase(BaseModel):
    name: str
    generic_name: str | None = None
    unit: str
    requires_prescription: bool = False
    sell_price: float
    category_id: int

class MedicineCreate(MedicineBase):
    pass

class MedicineOut(MedicineBase):
    id: int

    class Config:
        from_attributes = True   # allows Pydantic to read directly from SQLAlchemy objects
```

**Pattern to notice:** `Base` holds shared fields, `Create` is what the client sends in (POST body), `Out` is what you return (adds `id`, and would exclude anything sensitive). You'll repeat this `Base / Create / Out` pattern for every resource.

### `app/schemas/batch.py`

```python
from pydantic import BaseModel
from datetime import date, datetime

class BatchBase(BaseModel):
    batch_number: str
    quantity_in_stock: int
    cost_price: float
    expiry_date: date
    medicine_id: int
    supplier_id: int

class BatchCreate(BatchBase):
    pass

class BatchOut(BatchBase):
    id: int
    received_at: datetime

    class Config:
        from_attributes = True
```

### `app/schemas/sale.py`

```python
from pydantic import BaseModel
from datetime import datetime

class SaleItemCreate(BaseModel):
    medicine_id: int
    batch_id: int
    quantity: int

class SaleCreate(BaseModel):
    customer_id: int | None = None
    items: list[SaleItemCreate]

class SaleItemOut(BaseModel):
    id: int
    medicine_id: int
    batch_id: int
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True

class SaleOut(BaseModel):
    id: int
    staff_id: int
    customer_id: int | None
    total_amount: float
    created_at: datetime
    items: list[SaleItemOut]

    class Config:
        from_attributes = True
```

Notice `SaleCreate` only asks the client for `medicine_id`, `batch_id`, and `quantity` per item — **never** `unit_price`. The server calculates price and total. Never trust the client to tell you how much something costs.

---

## 9. CRUD Layer

This layer is pure database logic — no `Request`, no HTTP status codes, just functions that take a `Session` and return data.

### `app/crud/medicine.py`

```python
from sqlalchemy.orm import Session
from app.models.medicine import Medicine
from app.schemas.medicine import MedicineCreate

def get_medicine(db: Session, medicine_id: int):
    return db.query(Medicine).filter(Medicine.id == medicine_id).first()

def get_medicines(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Medicine).offset(skip).limit(limit).all()

def create_medicine(db: Session, medicine: MedicineCreate):
    db_medicine = Medicine(**medicine.model_dump())
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine
```

### `app/crud/sale.py` (the interesting one — handles stock deduction)

```python
from sqlalchemy.orm import Session
from datetime import date
from fastapi import HTTPException, status
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.batch import Batch
from app.models.medicine import Medicine
from app.schemas.sale import SaleCreate

def create_sale(db: Session, sale_data: SaleCreate, staff_id: int):
    total_amount = 0.0
    sale_items_to_add = []

    for item in sale_data.items:
        batch = db.query(Batch).filter(Batch.id == item.batch_id).first()
        medicine = db.query(Medicine).filter(Medicine.id == item.medicine_id).first()

        if not batch or not medicine:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Medicine or batch not found")

        if batch.expiry_date < date.today():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Batch {batch.batch_number} is expired")

        if batch.quantity_in_stock < item.quantity:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Not enough stock for {medicine.name}")

        # deduct stock
        batch.quantity_in_stock -= item.quantity

        line_total = medicine.sell_price * item.quantity
        total_amount += line_total

        sale_items_to_add.append(
            SaleItem(
                medicine_id=medicine.id,
                batch_id=batch.id,
                quantity=item.quantity,
                unit_price=medicine.sell_price,
            )
        )

    new_sale = Sale(
        staff_id=staff_id,
        customer_id=sale_data.customer_id,
        total_amount=total_amount,
        items=sale_items_to_add,
    )

    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)
    return new_sale
```

**This function is the heart of the whole system.** Walk through it slowly — it's checking expiry, checking stock, deducting stock, snapshotting price, and building the sale, all in one atomic database transaction (if anything raises before `db.commit()`, nothing is saved — SQLAlchemy rolls it back). This is the kind of business logic that belongs in `crud/` (or a `services/` layer if it grows further), *not* directly inside a router.

---

## 10. Routers (comparing to your current style)

Here's your original `create_post` pattern next to the equivalent "done properly" pattern, so you can see exactly what changes and why.

**What you have now:**
```python
@app.post('/createpost')
def create_post(payload: dict = Body(...)):
    print(payload)
    return { "msg" : "Successfully created post" }
```

Problems: `dict` means **no validation** — any garbage JSON is accepted; nothing is saved to a database; no typed response.

**The pharmacy equivalent, done properly:**

### `app/routers/medicines.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.medicine import MedicineCreate, MedicineOut
from app.crud import medicine as medicine_crud

router = APIRouter(prefix="/medicines", tags=["Medicines"])

@router.post("/", response_model=MedicineOut)
def create_medicine(medicine: MedicineCreate, db: Session = Depends(get_db)):
    return medicine_crud.create_medicine(db, medicine)

@router.get("/", response_model=list[MedicineOut])
def list_medicines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return medicine_crud.get_medicines(db, skip, limit)

@router.get("/{medicine_id}", response_model=MedicineOut)
def get_medicine(medicine_id: int, db: Session = Depends(get_db)):
    return medicine_crud.get_medicine(db, medicine_id)
```

**What changed and why:**
- `medicine: MedicineCreate` instead of `payload: dict` — FastAPI now validates the incoming JSON automatically. Send a string where a float should be? You get a clean 422 error for free, no code needed.
- `response_model=MedicineOut` — guarantees the response shape, and filters out any fields not defined on `MedicineOut` (defense against accidentally leaking data).
- `db: Session = Depends(get_db)` — this is FastAPI's **dependency injection**. Every request gets its own database session automatically, and it's closed automatically after. You just declare you need it.
- The router doesn't touch SQLAlchemy directly — it delegates to `medicine_crud`. The router's job is *only* to handle HTTP concerns.
- `APIRouter(prefix="/medicines", tags=["Medicines"])` — this is how you split `main.py`'s single `app` into per-resource files; `tags` groups them nicely in the auto-generated `/docs` page.

### `app/routers/sales.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.sale import SaleCreate, SaleOut
from app.crud import sale as sale_crud
# from app.dependencies import get_current_staff  # add once auth is wired up

router = APIRouter(prefix="/sales", tags=["Sales"])

@router.post("/", response_model=SaleOut)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    staff_id = 1  # placeholder until auth is added — see Section 12
    return sale_crud.create_sale(db, sale, staff_id)
```

---

## 11. Wiring It All Together in main.py

### `app/main.py`

```python
from fastapi import FastAPI
from app.core.database import Base, engine
from app.routers import medicines, batches, sales, staff, auth

# creates all tables that don't exist yet (fine for dev; use Alembic for real migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pharmacy Management System")

app.include_router(medicines.router)
app.include_router(batches.router)
app.include_router(sales.router)
app.include_router(staff.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"msg": "Pharmacy API is running"}
```

`app.include_router(...)` is the key line — it plugs each domain's routes into the single FastAPI app, each keeping its own `prefix` (so `medicines.router` handles everything under `/medicines/...`). This is directly equivalent to `app.use('/medicines', medicinesRouter)` in Express.

---

## 12. Step-by-Step Integration Order

Build in this order — each step is testable on its own before moving to the next, which keeps debugging manageable:

1. **Environment** — `uv init`, install packages, create `.env`, confirm Postgres is running and reachable.
2. **`core/database.py` + `core/config.py`** — confirm you can connect (write a tiny throwaway script that does `engine.connect()` and prints success).
3. **Models, one at a time, simplest first** — `Category` → `Supplier` → `Medicine` → `Batch` → `Staff` → `Customer` → `Sale` → `SaleItem`. After each one, run the app and check `Base.metadata.create_all()` creates the table correctly (inspect with `psql` or a GUI like TablePlus/pgAdmin).
4. **Schemas** — write `Base/Create/Out` for each model, matching what you just built.
5. **CRUD functions** — start with simple ones (`create_medicine`, `get_medicines`) before the complex `create_sale`.
6. **Routers** — wire up one resource fully (model → schema → crud → router) before starting the next. Test each with `/docs` (FastAPI's built-in Swagger UI) as you go — don't wait until everything is built to test.
7. **Auth (`core/security.py` + `routers/auth.py`)** — hash passwords with `passlib`, issue JWTs on login, add a `get_current_staff` dependency, then protect `create_sale` with it (replacing the `staff_id = 1` placeholder from Section 10).
8. **Alembic migrations** — once your schema stabilizes, switch from `Base.metadata.create_all()` to proper Alembic migrations, so schema changes are tracked and reversible (important once you're not the only dev — remember your friend joining as frontend dev will eventually want a stable API contract, and *you'll* want to evolve the DB without breaking things).
9. **Business rules** — expand `create_sale`'s validation (e.g., block sales of prescription-only items without a linked prescription record), add a low-stock alert query, add a "medicines expiring in the next 30 days" report endpoint.

---

## 13. Exercises to Test Yourself

Do these *before* looking anything up — this matches how you said you like to learn (struggle first, then get help):

1. Add a `Prescription` model (fields: `id`, `patient_name`, `doctor_name`, `issued_date`, `sale_id` as a one-to-one link to `Sale`). Which side of the relationship should hold the foreign key?
2. Write the `crud` function `get_low_stock_batches(db, threshold=10)` that returns all batches where `quantity_in_stock < threshold`.
3. Write the `crud` function `get_expiring_soon(db, days=30)` that returns batches expiring within the next N days. (Hint: `datetime.date.today() + timedelta(days=days)`)
4. Add a `role`-based check: write a FastAPI dependency `require_role("admin")` that raises a 403 if the logged-in staff member isn't an admin. Where should this live — `dependencies.py` or `core/security.py`? Justify your answer.
5. Your `create_sale` function currently fetches each batch one-by-one in a loop. What happens if two cashiers submit a sale for the *same last unit* of a medicine at the exact same time? (This is a real concurrency problem — research `SELECT ... FOR UPDATE` row locking once you hit it.)

---

## 14. Where to Go Next

Once this is working end-to-end:
- **Alembic migrations** properly (you'll need this the moment you deploy — you can't just re-run `create_all` against a production DB with real data in it).
- **Pytest + a test database** — write tests for your `crud/` layer since it's decoupled from HTTP, it's very testable in isolation.
- **Async SQLAlchemy** (`asyncpg` + `AsyncSession`) once you're comfortable with the sync version — FastAPI performs best when your DB calls are async too, but learning sync SQLAlchemy first is the right order.
- **Docker Compose** — containerize the API + Postgres together, so your friend (frontend dev) can spin up the whole backend with one command without installing Postgres locally.

---

*This guide is meant to be read alongside actually typing the code yourself — don't copy-paste wholesale. Type each model, run the server, break it on purpose, and read the error. That's where the actual learning happens.*
