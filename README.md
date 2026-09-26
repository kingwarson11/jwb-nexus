# JWB Nexus

AI-powered financial and commerce intelligence platform for African SMEs.
From *"what happened?"* to *"what should I do next?"*

This repo implements the full recommended build order from the project
blueprint: **Foundation (auth, business, products) → POS → Inventory
Intelligence → Financial OS → AI Business Analyst → Market Intelligence**.
Only the real MTN MoMo integration (currently mocked) and a push-notification
delivery layer remain as clearly-scoped next steps — see
[What's next](#whats-next).

## Stack

| Layer      | Technology                          |
|------------|--------------------------------------|
| Frontend   | React + TypeScript + Vite + Tailwind |
| Backend    | FastAPI (Python)                     |
| Database   | PostgreSQL                           |
| Payments   | Abstracted `PaymentService` — mock MoMo adapter now, real MTN MoMo later |
| AI layer   | Claude API (optional) with a built-in template fallback |
| Hosting    | **Render** — backend web service, managed Postgres, and the frontend as a Render static site, all from one Blueprint |

Everything runs on Render: the FastAPI backend as a web service, Postgres as
a managed database, and the React frontend as a Render **static site** — no
second hosting provider needed.

## What's implemented

- **Auth** — signup/login (JWT), password hashing
- **Businesses** — one owner can run multiple businesses
- **Products & Suppliers** — full CRUD
- **Inventory Intelligence** — stock levels, sales-velocity calculation,
  estimated days of cover, low-stock detection, expiry alerts, slow-moving
  product detection (recent vs. baseline velocity comparison)
- **POS** — cart → checkout → stock deduction → payment recording, in one
  atomic flow, with a swappable payment adapter (mock MoMo included)
- **Financial OS** — expenses, Income Statement, Cash Flow Statement, main
  dashboard summary
- **AI Business Analyst** — merchants ask plain-language questions; the
  backend pulls verified facts from the database (`app/analytics.py`,
  `app/ai_engine.py`) and explains them — via Claude if `ANTHROPIC_API_KEY`
  is set, or a template-based explainer if not (works either way, no API
  key required to demo it)
- **Market Intelligence** — anonymised, aggregated area/category demand
  trends, backed by a synthetic dataset matching the blueprint's exact MVP
  spec (1,000 simulated transactions, 50 products, 20 businesses, 5
  categories, 3 areas, 12 weeks). Nothing tied to an individual business is
  ever stored — only aggregated `market_metrics` rows
- **Demo data seed scripts** so the app isn't empty on first run

## What's next

- **Real MoMo integration** — swap `MockMoMoAdapter` in `app/payments.py`
  for MTN's sandbox/production API once you're onboarded; the POS route
  doesn't need to change
- **Notifications engine** — the underlying triggers (low stock, expiry,
  slow-moving, cash-flow risk, rising demand) all already exist as data;
  this phase is about delivering them as a feed / push notification rather
  than requiring the merchant to open each screen
- **Real aggregation job** — replace the synthetic Market Intelligence
  seed with a scheduled job that aggregates real participating-merchant
  sales data, keeping the same privacy boundary (only aggregates ever
  written to `market_metrics`)

---

## 1. Local development

### Prerequisites
- Python 3.12+, Node.js 18+, Docker (for local Postgres) — or your own Postgres instance

### Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit DATABASE_URL / JWT_SECRET if needed; ANTHROPIC_API_KEY is optional

# Start Postgres (or point DATABASE_URL at your own instance)
docker compose -f ../docker-compose.yml up -d db

# Tables are created automatically on first run
uvicorn app.main:app --reload --port 8000

# Optional demo data:
python seed_demo.py               # a working business with 14 days of sales/expenses
python seed_market_synthetic.py   # the synthetic Market Intelligence dataset
```

API docs at `http://localhost:8000/docs` (FastAPI's auto-generated Swagger UI).

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_URL=http://localhost:8000
npm run dev
```

App at `http://localhost:5173`. If you ran `seed_demo.py`, log in with
`demo@jwbnexus.com` / `demo1234`.

### Or run everything with Docker Compose

```bash
docker compose up --build
```

---

## 2. Push this to your GitHub

```bash
cd jwb-nexus
git init
git add .
git commit -m "Initial commit: JWB Nexus — POS, inventory, finance, AI analyst, market intelligence"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

Then create the working branches from the blueprint's suggested structure:

```bash
git checkout -b develop && git push -u origin develop
for b in feature/auth feature/pos feature/inventory feature/finance feature/ai feature/momo feature/market-intelligence; do
  git checkout develop && git checkout -b $b && git push -u origin $b
done
git checkout develop
```

---

## 3. Deploy — Render (backend + database + frontend, all in one)

1. Push this repo to GitHub (above) if you haven't.
2. In [Render](https://dashboard.render.com), click **New → Blueprint**, and
   point it at your GitHub repo. Render reads `render.yaml` automatically and
   provisions three things in one go:
   - A **PostgreSQL** database (free tier)
   - A **web service** (`jwb-nexus-api`) running the FastAPI backend, with
     `DATABASE_URL` and a generated `JWT_SECRET` wired in automatically
   - A **static site** (`jwb-nexus-frontend`) serving the built React app,
     with `VITE_API_URL` pointed at the backend service
3. Render assigns each service a URL based on its `name` in `render.yaml`
   (e.g. `https://jwb-nexus-api.onrender.com`), **if that subdomain is still
   available** — if it's taken, Render appends a suffix instead. After the
   first deploy, check the actual URLs Render gave you:
   - If the frontend's URL differs from `jwb-nexus-frontend.onrender.com`,
     update the backend's `CORS_ORIGINS` env var to match, then redeploy the
     backend.
   - If the backend's URL differs from `jwb-nexus-api.onrender.com`, update
     the frontend's `VITE_API_URL` env var to match, then redeploy the
     frontend (static sites need a rebuild to pick up a changed env var).
4. Optional: in the backend service's environment settings, add
   `ANTHROPIC_API_KEY` to get natural-language phrasing from Claude in the
   AI Business Analyst. Without it, the analyst still works — it uses a
   template-based explainer instead.
5. Optional: `python seed_demo.py` and `python seed_market_synthetic.py`
   can be run against your Render Postgres instance (set `DATABASE_URL` in
   your local shell to the value shown in the Render database's "Connect"
   tab) to populate demo data before a live pitch.

> Free-tier Render web services spin down after inactivity and take
> ~30–60s to wake up on the next request — fine for a demo/MVP, worth
> upgrading to a paid instance before a live pitch if that cold-start
> matters. Static sites don't have this issue.

---

## Project structure

```
jwb-nexus/
├── backend/            FastAPI app (Person 1: Backend + Financial Engine)
│   ├── app/
│   │   ├── main.py            App entrypoint, router registration
│   │   ├── models.py          SQLAlchemy models (incl. market_metrics)
│   │   ├── schemas.py         Pydantic request/response schemas
│   │   ├── auth.py, deps.py   JWT auth + FastAPI dependencies
│   │   ├── analytics.py       Velocity, slow-moving, expiry, low-stock logic
│   │   ├── ai_engine.py       AI Business Analyst: facts -> explanation
│   │   ├── payments.py        Payment adapter abstraction (mock MoMo)
│   │   └── routers/           One router per domain (auth, products, sales, ai, market, ...)
│   ├── seed_demo.py               Demo business + sales + expenses
│   ├── seed_market_synthetic.py   Synthetic Market Intelligence dataset
│   └── requirements.txt
├── frontend/            React app (Person 2: Frontend + UX)
│   └── src/
│       ├── pages/              Login, Dashboard, POS, Products, Inventory,
│       │                       Expenses, Reports, AIAnalyst, MarketIntelligence
│       ├── components/         Layout, ProtectedRoute
│       ├── context/AuthContext.tsx
│       └── api/client.ts       Typed fetch wrapper
├── database/
│   └── schema_reference.sql    Auto-generated Postgres DDL, for documentation
├── docs/
│   └── ARCHITECTURE.md
├── render.yaml                 Render Blueprint: backend + Postgres + static frontend
├── docker-compose.yml          Local dev environment
└── .github/workflows/ci.yml    Compiles the backend and builds the frontend on every push
```

Backend and frontend are cleanly split, matching the blueprint's 3-person
division. **Person 3 (AI + Data + DevOps)**'s scope — `app/ai_engine.py`,
`app/routers/market.py`, `seed_market_synthetic.py`, and this deployment
setup — is already scaffolded and working; the natural next step for that
role is swapping the synthetic dataset for a real aggregation job.

## Team workflow suggestion

- `main` — always deployable
- `develop` — integration branch
- `feature/*` — one branch per module; open a PR into `develop`; the other
  two teammates review before merging (per the blueprint: "Everyone should
  still review each other's work")

## API reference

Full interactive docs at `/docs` once the backend is running. Base URL
structure:

```
POST   /api/auth/signup | /api/auth/login | GET /api/auth/me
GET/POST   /api/businesses
GET/POST   /api/businesses/{id}/products
GET/POST   /api/businesses/{id}/suppliers
GET        /api/businesses/{id}/inventory | /inventory/expiring | /inventory/slow-moving
POST       /api/businesses/{id}/inventory/{product_id}/adjust
GET/POST   /api/businesses/{id}/sales | POST /sales/{id}/refund
GET/POST   /api/businesses/{id}/expenses
GET        /api/businesses/{id}/reports/dashboard | /income-statement | /cash-flow
POST       /api/businesses/{id}/ai/query
GET        /api/market/trends | /api/market/areas
```
