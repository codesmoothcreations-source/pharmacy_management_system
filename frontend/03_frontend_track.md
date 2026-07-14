# File 3 — Frontend Track: React, Paced for Beginners

> **Who this file is for:** whoever on the team is focusing on the frontend (and Kelvin, moving between both). Same format as the backend track — a week-by-week curriculum synced to the same roadmap in File 1, so both sides of the team hit their "meets in the middle" moments at the same time.

---

## Table of Contents

1. [Before Week 1 — Setup Checklist](#1-before-week-1--setup-checklist)
2. [Folder Structure — What We're Aiming For](#folder-structure--what-were-aiming-for)
3. [Week 1 — Environment & "Hello World"](#week-1--environment--hello-world)
4. [Week 2 — Your First Component & Static Data](#week-2--your-first-component--static-data)
5. [Week 3 — State: Making Things Change on the Screen](#week-3--state-making-things-change-on-the-screen)
6. [Week 4 — Talking to a Real API (Before the Backend Is Ready)](#week-4--talking-to-a-real-api-before-the-backend-is-ready)
7. [Week 5 — Forms: Adding a New Medicine](#week-5--forms-adding-a-new-medicine)
8. [Week 6 — The Sale Screen](#week-6--the-sale-screen)
9. [Week 7 — Connecting to the Real Backend (CORS Day)](#week-7--connecting-to-the-real-backend-cors-day)
10. [Weeks 8–9 — Login & Protected Pages](#weeks-89--login--protected-pages)
11. [Weeks 10–11 — Dashboard](#weeks-1011--dashboard)
12. [Core React Concepts Glossary](#core-react-concepts-glossary)

---

## 1. Before Week 1 — Setup Checklist

- [ ] Install Node.js (LTS version) — check with `node --version`.
- [ ] Inside the shared repo: `npm create vite@latest frontend -- --template react`
- [ ] `cd frontend && npm install && npm run dev` — confirm the default Vite+React page loads at `http://localhost:5173`.
- [ ] Push this to the shared repo on your own branch, open a PR, get it merged, same as the backend's Week 1. This is your first rep of the team Git workflow.

We're using **plain JavaScript React**, not TypeScript, deliberately — for a first team project where React itself is new, adding a type system on top multiplies what you're learning at once. Once the app works, upgrading to TypeScript is a great Phase 5 stretch goal (File 1, Section 7).

---

## Folder Structure — What We're Aiming For

Keep it simple and grow it only as you need to — don't over-engineer a folder structure for an app that doesn't exist yet.

```
frontend/
├── src/
│   ├── main.jsx              # entry point, renders <App />
│   ├── App.jsx                 # top-level layout + routing
│   ├── api/
│   │   └── client.js           # one place that knows the backend's base URL
│   ├── pages/
│   │   ├── MedicineListPage.jsx
│   │   ├── AddMedicinePage.jsx
│   │   ├── SalePage.jsx
│   │   ├── LoginPage.jsx
│   │   └── DashboardPage.jsx
│   └── components/
│       ├── MedicineCard.jsx
│       └── Navbar.jsx
├── index.html
└── package.json
```

**Why `pages/` vs `components/`?** A "page" is something a whole URL route points to (the medicine list screen). A "component" is a smaller reusable piece used *inside* pages (a single medicine card, a navbar shown on every page). This distinction becomes genuinely useful once you have more than 3–4 screens — it stops you from having one giant folder with 20 files in it and no sense of what's a screen versus what's a building block.

---

## Week 1 — Environment & "Hello World"

**Learning goal:** what Vite actually is (a fast dev server + build tool), and what "JSX" is — HTML-looking syntax inside JavaScript.

**Building goal:** edit `App.jsx` to show something of your own, e.g.:

```jsx
function App() {
  return (
    <div>
      <h1>Pharmacy Management System</h1>
      <p>Frontend is running.</p>
    </div>
  );
}

export default App;
```

**Checkpoint:** show this rendering live in the browser at `localhost:5173`.

---

## Week 2 — Your First Component & Static Data

**Learning goal:** components, props, and the `.map()` pattern for rendering lists — this single pattern is used constantly in React and is worth really understanding this week, not skimming past.

**Building goal:** create `components/MedicineCard.jsx`, which takes a medicine object as a **prop** and displays it:

```jsx
function MedicineCard({ medicine }) {
  return (
    <div style={{ border: "1px solid #ccc", padding: "10px", marginBottom: "8px" }}>
      <h3>{medicine.name}</h3>
      <p>Price: GHS {medicine.sell_price}</p>
      <p>{medicine.requires_prescription ? "Requires prescription" : "Over the counter"}</p>
    </div>
  );
}

export default MedicineCard;
```

Then in `pages/MedicineListPage.jsx`, use it with **fake, hardcoded data** (no backend involved yet):

```jsx
import MedicineCard from "../components/MedicineCard";

const fakeMedicines = [
  { id: 1, name: "Paracetamol 500mg", sell_price: 5.5, requires_prescription: false },
  { id: 2, name: "Amoxicillin 250mg", sell_price: 12.0, requires_prescription: true },
];

function MedicineListPage() {
  return (
    <div>
      <h2>Medicines</h2>
      {fakeMedicines.map((med) => (
        <MedicineCard key={med.id} medicine={med} />
      ))}
    </div>
  );
}

export default MedicineListPage;
```

**Why fake data first?** This week is purely about learning components and rendering lists — a real skill on its own. Bringing in the real API in the same week as learning `.map()` and props for the first time is two new things at once. Separate them.

**Checkpoint:** the medicine list renders on screen using the fake data, styled at least minimally.

---

## Week 3 — State: Making Things Change on the Screen

**Learning goal:** `useState` — the core idea that a component "remembers" a value and re-renders itself when that value changes. This is the single most important React concept — everything else builds on it.

**Building goal:** add a search box above the medicine list that filters the (still fake) list as you type:

```jsx
import { useState } from "react";

function MedicineListPage() {
  const [searchTerm, setSearchTerm] = useState("");

  const filtered = fakeMedicines.filter((med) =>
    med.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div>
      <h2>Medicines</h2>
      <input
        type="text"
        placeholder="Search medicines..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      {filtered.map((med) => (
        <MedicineCard key={med.id} medicine={med} />
      ))}
    </div>
  );
}
```

**Slow down and notice:** you never manually touched the DOM to make the list update — you just changed the `searchTerm` state, and React re-ran the component and re-rendered the filtered list automatically. This is the core mental model shift from plain JavaScript DOM manipulation, and it's worth sitting with this example until it clicks.

**Checkpoint:** typing in the search box visibly filters the list live.

---

## Week 4 — Talking to a Real API (Before the Backend Is Ready)

Backend may not have all routes ready by this week — that's fine, this is intentional pacing. Use a free placeholder API to learn the *pattern* of fetching data, so when the real backend is ready in Week 7 it's just swapping a URL.

**Learning goal:** `useEffect` + `fetch`, and the "loading / data / error" pattern that every real app needs.

**Building goal:**

```jsx
import { useState, useEffect } from "react";

function MedicineListPage() {
  const [medicines, setMedicines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("https://jsonplaceholder.typicode.com/users") // placeholder, swapped later
      .then((res) => res.json())
      .then((data) => {
        setMedicines(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []); // empty array = run once, when the component first appears

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Something went wrong: {error}</p>;

  return (
    <div>
      <h2>Medicines</h2>
      {medicines.map((med) => (
        <p key={med.id}>{med.name}</p>
      ))}
    </div>
  );
}
```

**Why the placeholder API this week?** It removes a dependency on the backend being finished, which keeps the frontend track moving at its own pace without blocking on your teammate. It also isolates the *new concept* (fetching + loading state) from a second new thing (a backend that might have its own bugs) — same principle as Week 2's fake data.

**Checkpoint:** the loading state briefly shows, then real (placeholder) data appears, and you can explain out loud what `useEffect`'s empty `[]` does.

---

## Week 5 — Forms: Adding a New Medicine

**Learning goal:** controlled form inputs — every input's value lives in state, and typing updates that state.

**Building goal:** `pages/AddMedicinePage.jsx` — a form with fields matching the `MedicineCreate` schema from the backend (coordinate the exact field names with your backend teammate this week):

```jsx
import { useState } from "react";

function AddMedicinePage() {
  const [form, setForm] = useState({
    name: "",
    generic_name: "",
    unit: "",
    requires_prescription: false,
    sell_price: "",
    category_id: "",
  });

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    setForm({ ...form, [name]: type === "checkbox" ? checked : value });
  }

  function handleSubmit(e) {
    e.preventDefault();
    console.log("Would submit:", form); // real API call added in Week 7
  }

  return (
    <form onSubmit={handleSubmit}>
      <input name="name" placeholder="Medicine name" value={form.name} onChange={handleChange} />
      <input name="generic_name" placeholder="Generic name" value={form.generic_name} onChange={handleChange} />
      <input name="unit" placeholder="Unit (tablet, bottle...)" value={form.unit} onChange={handleChange} />
      <label>
        <input type="checkbox" name="requires_prescription" checked={form.requires_prescription} onChange={handleChange} />
        Requires prescription
      </label>
      <input name="sell_price" type="number" placeholder="Price" value={form.sell_price} onChange={handleChange} />
      <button type="submit">Add Medicine</button>
    </form>
  );
}

export default AddMedicinePage;
```

**Checkpoint:** filling the form and submitting logs the correct object shape to the browser console — verify every field name matches exactly what the backend's `MedicineCreate` schema expects.

---

## Week 6 — The Sale Screen

**Learning goal:** managing a small list of items in state (the "cart" of a sale) — adding items, removing items, calculating a running total.

**Building goal:** a page where you can pick a medicine from a (still fake, or placeholder) list, choose a quantity, add it to a running sale list, and see a live total:

```jsx
const [saleItems, setSaleItems] = useState([]);

function addItem(medicine, quantity) {
  setSaleItems([...saleItems, { medicine, quantity }]);
}

const total = saleItems.reduce((sum, item) => sum + item.medicine.sell_price * item.quantity, 0);
```

**Checkpoint:** adding two or three items updates a visible running total correctly.

---

## Week 7 — Connecting to the Real Backend (CORS Day)

Coordinate directly with your backend teammate this week — this is the meeting-in-the-middle moment from File 1's roadmap and File 2's Week 7.

**Building goal:** create `src/api/client.js` — one central place that knows the backend's address:

```js
const BASE_URL = "http://localhost:8000";

export async function getMedicines() {
  const res = await fetch(`${BASE_URL}/medicines/`);
  if (!res.ok) throw new Error("Failed to fetch medicines");
  return res.json();
}

export async function createMedicine(medicine) {
  const res = await fetch(`${BASE_URL}/medicines/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(medicine),
  });
  if (!res.ok) throw new Error("Failed to create medicine");
  return res.json();
}
```

**Why one central file instead of `fetch` calls scattered across every page?** If the backend URL ever changes (e.g. when you deploy), you change it in exactly one place. It also means every page uses the same error-handling pattern instead of each page inventing its own.

Now swap the placeholder URL from Week 4 and the `console.log` from Week 5 for real calls to `getMedicines()` and `createMedicine()`.

**If you hit a CORS error in the browser console** ("blocked by CORS policy") — that's expected on the *first* attempt, and it's the backend's job to fix (File 2, Week 7 covers the exact middleware). This is a good real example of a bug that requires both sides of the team talking to each other to resolve — not something the frontend can fix alone.

**Checkpoint:** the medicine list page shows real data from the real database, and the "Add Medicine" form actually creates a new row you can then see appear in the list.

---

## Weeks 8–9 — Login & Protected Pages

**Learning goal:** storing a token after login and attaching it to future requests.

**Building goal:**
- A `LoginPage.jsx` with username/password fields, calling a `login()` function in `api/client.js` that hits `POST /auth/login`.
- Store the returned token in React state at the top level of the app (`App.jsx`) — for this phase, plain state is fine; don't reach for anything fancier yet.
- Attach it on protected requests:

```js
export async function createSale(saleData, token) {
  const res = await fetch(`${BASE_URL}/sales/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify(saleData),
  });
  if (!res.ok) throw new Error("Failed to create sale");
  return res.json();
}
```

- Simple route protection: if there's no token in state, redirect to `/login` instead of showing the sale page. (If you haven't set up `react-router-dom` yet, this is the week to add it — `npm install react-router-dom` — for real multi-page navigation instead of manually swapping components.)

**Checkpoint:** logging in with valid credentials lets you reach the sale page and complete a real sale; logging out (or never logging in) blocks it.

---

## Weeks 10–11 — Dashboard

**Learning goal:** fetching from two endpoints and rendering two lists on one page — nothing conceptually new, this is a chance to consolidate everything so far.

**Building goal:** `DashboardPage.jsx` showing two sections, calling the backend's `/reports/low-stock` and `/reports/expiring-soon` endpoints from File 2's Weeks 10–11.

**Checkpoint:** the dashboard shows real, correct low-stock and expiring-soon data pulled from the actual database your team has been testing with for 10 weeks — a genuinely satisfying moment to demo at the sync.

---

## Core React Concepts Glossary

Keep this open in a tab for the first several weeks:

| Term | What it means |
|---|---|
| **Component** | A JavaScript function that returns UI (JSX). The building block of every React app. |
| **JSX** | HTML-looking syntax inside JavaScript — gets compiled into real DOM elements. |
| **Props** | Data passed *into* a component from its parent, e.g. `<MedicineCard medicine={med} />`. Read-only inside the component receiving them. |
| **State (`useState`)** | Data a component "remembers" between renders. Changing it causes the component to re-render. |
| **Effect (`useEffect`)** | Code that runs in response to a component appearing or a value changing — most commonly used for fetching data. |
| **Controlled input** | A form input whose value is driven entirely by React state, not by the browser's own internal input memory. |
| **Conditional rendering** | Showing different UI depending on a value, e.g. `{loading ? <p>Loading...</p> : <RealContent />}`. |
