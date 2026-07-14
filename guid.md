# 🏥 Pharmacy Management System – Full‑Stack Project with FastAPI & SQLAlchemy

This guide will take you from zero to a well‑structured, production‑ready **pharmacy database system** using **FastAPI**, **SQLAlchemy** (ORM), **Pydantic** for validation, and **uv** for environment management.  
We’ll go through the **thinking process** behind designing the database, then build a clean folder structure, write models, schemas, routes, and finally test everything.

By the end, you will have a **complete working project** that you can extend, and you’ll understand *why* each piece is organised the way it is.

---

## 📦 Table of Contents

1. [Project Overview](#-project-overview)
2. [Environment Setup with `uv`](#-environment-setup-with-uv)
3. [Database Design – The Thinking Process](#-database-design--the-thinking-process)
   - Identifying Entities & Relationships
   - ER Diagram (Conceptual)
   - Attributes & Constraints
4. [Folder Structure – Best Practices](#-folder-structure--best-practices)
5. [Building the Project Step‑by‑Step](#-building-the-project-stepbyStep)
   - Configuration & Database Connection
   - SQLAlchemy Models
   - Pydantic Schemas
   - CRUD Operations (Repository Layer)
   - API Routes (Routers)
   - Main Application Factory
6. [Testing the API](#-testing-the-api)
7. [Next Steps & Best Practices](#-next-steps--best-practices)
8. [Full Code Snippets](#-full-code-snippets)

---

## 🎯 Project Overview

We are building a **Pharmacy Management System** that handles:

- **Medicines** (products) – each has a name, barcode, category, price, stock, expiry date, etc.
- **Categories** – to group medicines (e.g., Antibiotics, Painkillers, Vitamins).
- **Suppliers** – companies that supply the medicines.
- **Customers** – people who buy medicines.
- **Sales** (orders) – records of purchases, including date, customer, total amount.
- **Sale Items** – line items of each sale (medicine, quantity, price at sale time).
- **Inventory** – automatic update of stock on each sale.

We will use **PostgreSQL** as the database (you can easily switch to SQLite for development).

---

## 🛠 Environment Setup with `uv`

`uv` is an extremely fast Python package installer and resolver. Let’s set everything up.

### 1. Install `uv` (if not already)

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip (fallback)
pip install uv
```

### 2. Create a new project directory

```bash
mkdir pharmacy-api
cd pharmacy-api
```

### 3. Initialise a Python virtual environment with `uv`

```bash
uv venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

### 4. Install dependencies

Create a `pyproject.toml` (or just install directly) – we’ll use `uv add`:

```bash
uv add fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-dotenv
```

If you want to use `async` with PostgreSQL, you might replace `psycopg2-binary` with `asyncpg` and use `databases` or `sqlalchemy.ext.asyncio`. For simplicity, we’ll stick with **sync** SQLAlchemy (easier for beginners).

Optionally, add `httpx` for testing later.

---

## 🧠 Database Design – The Thinking Process

Before writing any code, we must **understand the business domain** and **model it correctly**.

### 🔍 Identifying Entities & Relationships

We ask:

- What are the **main objects**? → Medicine, Category, Supplier, Customer, Sale, SaleItem.
- How do they relate?
  - A `Category` has many `Medicine`s (one‑to‑many).
  - A `Supplier` supplies many `Medicine`s (one‑to‑many).
  - A `Sale` belongs to one `Customer` (many‑to‑one).
  - A `Sale` has many `SaleItem`s (one‑to‑many).
  - Each `SaleItem` refers to one `Medicine` (many‑to‑one).
  - `Inventory` is essentially the `stock` column inside `Medicine` – we can keep it there and update it on each sale.

We might also add `Employee` if needed, but let’s keep it minimal.

### 📊 Conceptual ER Diagram

```
+-------------+       +-------------+       +-------------+
|  Category   |       |  Supplier   |       |  Customer   |
+-------------+       +-------------+       +-------------+
| id (PK)     |       | id (PK)     |       | id (PK)     |
| name        |       | name        |       | name        |
| description |       | contact     |       | email       |
+-------------+       | phone       |       | phone       |
      |               +-------------+       | address     |
      | (1)                | (1)            +-------------+
      |                    |                     |
      |                    |                     |
      | (many)             | (many)              | (many)
      |                    |                     |
+-------------+       +-------------+       +-------------+
|  Medicine   |       |   Sale      |       |             |
+-------------+       +-------------+       |             |
| id (PK)     |<------| id (PK)     |------>|             |
| name        |       | date        |       |             |
| barcode     |       | total_amount|       +-------------+
| category_id |       | customer_id |       +-------------+
| supplier_id |       +-------------+       |  SaleItem   |
| price       |             | (1)           +-------------+
| stock       |             |               | id (PK)     |
| expiry_date |             | (many)        | sale_id (FK)|
| description |             +-------------->| medicine_id |
+-------------+                              | quantity    |
                                             | price       |
                                             +-------------+
```

### 🔑 Attributes & Constraints

- **Medicine**: `barcode` should be unique. `price` and `stock` are numeric. `expiry_date` – future check.
- **Sale**: `total_amount` could be computed from items, but we store it for quick access.
- **SaleItem**: stores the `price` at the time of sale (historical snapshot).
- **Foreign keys**: cascade delete? For safety, we may set `ondelete="RESTRICT"` to avoid deleting a medicine that has sales.

### 📌 Additional thoughts

- We might add **audit fields** (`created_at`, `updated_at`) to every table.
- For **soft delete**, add an `is_active` boolean.

Now we have a solid design. Let’s implement it!

---

## 🗂 Folder Structure – Best Practices

A modular, scalable structure:

```
pharmacy-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app creation, include routers
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Load environment variables, settings
│   │   └── database.py         # Database engine and session
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── category.py
│   │   ├── supplier.py
│   │   ├── customer.py
│   │   ├── medicine.py
│   │   ├── sale.py
│   │   └── sale_item.py
│   ├── schemas/                # Pydantic models (request/response validation)
│   │   ├── __init__.py
│   │   ├── category.py
│   │   ├── supplier.py
│   │   ├── customer.py
│   │   ├── medicine.py
│   │   ├── sale.py
│   │   └── sale_item.py
│   ├── crud/                   # Database operations (logic)
│   │   ├── __init__.py
│   │   ├── base.py             # Generic CRUD class (optional)
│   │   ├── category.py
│   │   ├── medicine.py
│   │   └── ...
│   ├── api/                    # Route handlers (routers)
│   │   ├── __init__.py
│   │   ├── v1/                 # versioned API
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── categories.py
│   │   │   │   ├── medicines.py
│   │   │   │   ├── sales.py
│   │   │   │   └── ...
│   │   │   └── router.py       # register all endpoints
│   ├── dependencies.py         # Dependency injection (e.g., get_db)
│   └── utils/                  # Helpers (e.g., pagination, error handlers)
├── .env                        # Environment variables (not in VCS)
├── .gitignore
├── pyproject.toml
└── README.md
```

**Why this structure?**

- **Separation of Concerns**: Models (DB), Schemas (validation), CRUD (business logic), Routes (HTTP layer) are clearly separated.
- **Scalability**: Adding new tables or versions is straightforward.
- **Testability**: Each component can be unit‑tested independently.
- **Maintainability**: Clear naming and grouping.

We’ll implement this step by step.

---

## 🔨 Building the Project Step‑by‑Step

Let’s write the actual code.

### 1. Configuration & Database Connection

**`.env`** (create in project root)

```env
DATABASE_URL=postgresql://user:password@localhost/pharmacy_db
```

**`app/core/config.py`**

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./pharmacy.db")

    class Config:
        env_file = ".env"

settings = Settings()
```

**`app/core/database.py`**

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 2. SQLAlchemy Models

We’ll define each model in its own file under `app/models/`. Let’s write one complete example: `Medicine`.

**`app/models/category.py`**

```python
from sqlalchemy import Column, Integer, String, DateTime, func
from app.core.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

**`app/models/medicine.py`**

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    barcode = Column(String, unique=True, index=True, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    expiry_date = Column(DateTime, nullable=True)
    description = Column(String, nullable=True)

    # Foreign Keys
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False)

    # Relationships
    category = relationship("Category", back_populates="medicines")
    supplier = relationship("Supplier", back_populates="medicines")
    sale_items = relationship("SaleItem", back_populates="medicine")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

Similarly, we define `Supplier`, `Customer`, `Sale`, `SaleItem` with appropriate relationships.

**Important**: In `Category`, add `medicines = relationship("Medicine", back_populates="category")`. Same for `Supplier`.

**`app/models/sale.py`**

```python
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, server_default=func.now())
    total_amount = Column(Float, nullable=False, default=0.0)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False)

    customer = relationship("Customer", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale")
```

**`app/models/sale_item.py`**

```python
from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)  # price at sale time

    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="RESTRICT"), nullable=False)

    sale = relationship("Sale", back_populates="items")
    medicine = relationship("Medicine", back_populates="sale_items")
```

Don’t forget to add `back_populates` in each model to make relationships bidirectional.

Now we create all tables by running (we’ll add a startup script later).

### 3. Pydantic Schemas

We need schemas for **request** (creation/update) and **response** (returning data). Usually we have `Base`, `Create`, `Update`, and `Out` schemas.

**`app/schemas/medicine.py`** – example:

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Shared properties
class MedicineBase(BaseModel):
    name: str
    barcode: str
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    expiry_date: Optional[datetime] = None
    description: Optional[str] = None
    category_id: int
    supplier_id: int

# Creation request
class MedicineCreate(MedicineBase):
    pass

# Update request (all optional)
class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    barcode: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    expiry_date: Optional[datetime] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None

# Response (includes created_at, updated_at, and maybe nested category/supplier)
class MedicineOut(MedicineBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # for ORM compatibility (formerly orm_mode)
```

Similarly for `Category`, `Supplier`, `Customer`, `Sale`, `SaleItem`. You can nest some of them if needed (e.g., `SaleOut` includes list of `SaleItemOut`).

### 4. CRUD Operations (Repository Layer)

We’ll create reusable base CRUD and then specific ones.

**`app/crud/base.py`**

```python
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
```

**`app/crud/medicine.py`** – specific CRUD with extra methods (e.g., search by barcode or name).

```python
from typing import Optional, List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.medicine import Medicine
from app.schemas.medicine import MedicineCreate, MedicineUpdate

class CRUDMedicine(CRUDBase[Medicine, MedicineCreate, MedicineUpdate]):
    def get_by_barcode(self, db: Session, barcode: str) -> Optional[Medicine]:
        return db.query(Medicine).filter(Medicine.barcode == barcode).first()

    def search_by_name(self, db: Session, name: str, skip: int = 0, limit: int = 100) -> List[Medicine]:
        return db.query(Medicine).filter(Medicine.name.ilike(f"%{name}%")).offset(skip).limit(limit).all()

medicine = CRUDMedicine(Medicine)
```

Repeat for other models.

### 5. API Routes (Routers)

We’ll put each resource endpoints in its own file under `app/api/v1/endpoints/`.

**`app/api/v1/endpoints/medicines.py`**

```python
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.medicine import medicine as crud_medicine
from app.schemas.medicine import MedicineOut, MedicineCreate, MedicineUpdate

router = APIRouter()

@router.get("/", response_model=List[MedicineOut])
def read_medicines(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    if name:
        items = crud_medicine.search_by_name(db, name=name, skip=skip, limit=limit)
    else:
        items = crud_medicine.get_multi(db, skip=skip, limit=limit)
    return items

@router.post("/", response_model=MedicineOut, status_code=status.HTTP_201_CREATED)
def create_medicine(
    *,
    db: Session = Depends(get_db),
    medicine_in: MedicineCreate,
):
    # Check if barcode already exists
    existing = crud_medicine.get_by_barcode(db, barcode=medicine_in.barcode)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medicine with this barcode already exists.",
        )
    # Optionally check category and supplier exist (we’ll add dependency)
    return crud_medicine.create(db, obj_in=medicine_in)

@router.get("/{medicine_id}", response_model=MedicineOut)
def read_medicine(
    medicine_id: int,
    db: Session = Depends(get_db),
):
    db_medicine = crud_medicine.get(db, id=medicine_id)
    if not db_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return db_medicine

@router.put("/{medicine_id}", response_model=MedicineOut)
def update_medicine(
    *,
    db: Session = Depends(get_db),
    medicine_id: int,
    medicine_in: MedicineUpdate,
):
    db_medicine = crud_medicine.get(db, id=medicine_id)
    if not db_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    # Check barcode uniqueness if changed
    if medicine_in.barcode and medicine_in.barcode != db_medicine.barcode:
        existing = crud_medicine.get_by_barcode(db, barcode=medicine_in.barcode)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Barcode already registered to another medicine.",
            )
    return crud_medicine.update(db, db_obj=db_medicine, obj_in=medicine_in)

@router.delete("/{medicine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medicine(
    *,
    db: Session = Depends(get_db),
    medicine_id: int,
):
    db_medicine = crud_medicine.get(db, id=medicine_id)
    if not db_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    crud_medicine.remove(db, id=medicine_id)
    return None
```

Similarly, create endpoints for categories, suppliers, customers, sales. For sales, we’ll need a special endpoint that accepts a list of items and updates stock.

### 6. Main Application Factory

**`app/main.py`**

```python
from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.database import engine, Base

# Create tables (in production use Alembic migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pharmacy API", version="1.0.0")

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Pharmacy API is running"}
```

**`app/api/v1/router.py`**

```python
from fastapi import APIRouter
from app.api.v1.endpoints import medicines, categories, suppliers, customers, sales

api_router = APIRouter()

api_router.include_router(medicines.router, prefix="/medicines", tags=["medicines"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(suppliers.router, prefix="/suppliers", tags=["suppliers"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(sales.router, prefix="/sales", tags=["sales"])
```

### 7. Running the Application

```bash
uvicorn app.main:app --reload
```

Now you can visit `http://localhost:8000/docs` to see the interactive API docs.

---

## 🧪 Testing the API (with `httpx` or Swagger)

You can test endpoints manually via Swagger UI or use `httpx` in a test script.

Example test for creating a medicine:

```bash
curl -X POST "http://localhost:8000/api/v1/medicines/" \
  -H "Content-Type: application/json" \
  -d '{"name":"Paracetamol","barcode":"123456","price":5.99,"stock":100,"category_id":1,"supplier_id":1}'
```

Make sure you first create a category and a supplier (via their endpoints) to get their IDs.

---

## 📈 Next Steps & Best Practices

1. **Alembic Migrations**: Instead of `Base.metadata.create_all`, use Alembic for schema versioning.
2. **Environment Variables**: Use `.env` for different environments (development, testing, production).
3. **Error Handling**: Add global exception handlers for 404, 422, etc.
4. **Dependency Injection**: Create dependencies to check existence of category/supplier before inserting medicine.
5. **Pagination**: Implement pagination with `limit`/`offset` or cursor-based.
6. **Authentication/Authorization**: Add JWT or OAuth2 for secure endpoints.
7. **Logging & Monitoring**: Integrate with logging and maybe Prometheus.
8. **Testing**: Write unit tests with `pytest` and `httpx`.
9. **Docker**: Containerize the app with Docker and docker-compose.

---

## 📝 Full Code Snippets (Summary)

I’ve provided all the essential pieces. For the complete code, you would create the missing files:

- `app/models/supplier.py`, `customer.py`, `sale.py`, `sale_item.py`
- `app/schemas/` for each entity
- `app/crud/` for each entity
- `app/api/v1/endpoints/` for each entity

But the pattern is the same as for `Medicine`. You can copy and adapt.

---

## 🧠 Final Thoughts on the Thinking Process

**Why we did what we did:**

- **Separation**: Keeps business logic away from HTTP layer.
- **Reusability**: Generic CRUD base reduces boilerplate.
- **Validation**: Pydantic ensures data integrity at API boundary.
- **ORM**: SQLAlchemy handles SQL generation, making switching DB easy.
- **Modularity**: Each component can be replaced or extended without affecting others.

This structure is suitable for small to medium projects and is used by many professional FastAPI applications.

---

## 🚀 Ready to Code!

You now have all the knowledge to build your pharmacy API. Clone this guide, open your editor, and start writing the models, schemas, and routes.

If you get stuck, refer back to the examples. Remember, learning by doing is the best way – so go ahead and build the entire system!

Happy coding! 😊