# Architecture

```
 MERCHANT / CUSTOMER
        │
        ▼
 ┌─────────────────────────────┐
 │  Frontend                   │  React + TypeScript + Tailwind
 │  (Render static site)       │
 │  Login · Dashboard · POS ·  │
 │  Inventory · Reports ·      │
 │  AI Analyst · Market Intel  │
 └──────────────┬───────────────┘
                │ REST (JSON, JWT bearer auth)
                ▼
 ┌─────────────────────────────┐
 │  Backend                    │  FastAPI
 │  (Render web service)       │
 │  Auth · POS · Inventory ·   │
 │  Finance · AI · Market ·    │
 │  Payments APIs              │
 └──────────────┬───────────────┘
        │                 │                  │
        ▼                 ▼                  ▼
 ┌─────────────┐   ┌───────────────────┐  ┌─────────────────┐
 │ PostgreSQL  │   │ Payment Service    │  │ AI Engine        │
 │ (Render)    │   │  → MockMoMoAdapter │  │  facts (DB) →    │
 │             │   │  → ManualAdapter   │  │  Claude API, or  │
 │             │   │    (cash/bank/card)│  │  template        │
 └─────────────┘   └───────────────────┘  │  fallback         │
                                            └─────────────────┘
```

## Core loop (implemented)

A merchant makes a sale → `POST /sales` validates stock → creates the sale +
line items → reduces inventory (logged as an `inventory_movements` row) →
charges via the payment adapter → records the payment → financial totals
(`cost_of_goods_sold`, revenue) are available immediately to the dashboard
and reports endpoints.

## Inventory Intelligence

`app/analytics.py` holds the velocity/forecasting logic, kept deliberately
simple per the blueprint ("no complex ML needed at first"):

- **Average daily sales** — units sold in the last N days ÷ N
- **Estimated days of cover** — current stock ÷ average daily sales
- **Slow-moving detection** — compares a recent window's sales against a
  longer baseline window; flags a decline past a configurable threshold
- **Expiry alerts** — products whose `expiry_date` falls within N days
- **Low stock** — `quantity <= minimum_stock`

These are the "verified facts" layer the blueprint's AI Architecture
(section 18) describes — the next step is an LLM layer that explains them in
plain language rather than inventing numbers.

## Database

See `database/schema_reference.sql` (auto-generated from `app/models.py`).
Core tables: `users`, `businesses`, `suppliers`, `products`,
`inventory_movements`, `customers`, `sales`, `sale_items`, `payments`,
`expenses`.

## Payment abstraction

`app/payments.py` defines a `get_adapter(method)` factory. The POS route
never talks to a payment provider directly — it calls whatever adapter is
returned. Today that's `MockMoMoAdapter` (instant "confirmed" response, mimics
MTN MoMo's polling flow) and `ManualAdapter` (cash/bank/card). Swapping in the
real MTN MoMo API later is a matter of adding an `MTNMoMoAdapter` here and
updating the factory — no changes needed in the POS router.

## AI Business Analyst

`app/ai_engine.py` implements the same "verified facts, then explain" pipeline
the blueprint's AI Architecture describes:

1. `gather_facts()` pulls today's revenue/profit, this week's revenue change,
   low-stock/expiring/slow-moving products, top sellers, inventory value, and
   month-to-date expenses — all from the database, all through the same
   analytics functions the Inventory and Reports screens already use.
2. `explain_facts()` turns that dict into a plain-language answer. If
   `ANTHROPIC_API_KEY` is set, it asks Claude to phrase an answer to the
   merchant's specific question, constrained to only the facts provided. If
   not (or if the API call fails for any reason), a deterministic
   template-based explainer produces a solid answer instead — so the feature
   never breaks a demo for lack of an API key.

## Market Intelligence

`app/routers/market.py` serves `market_metrics` rows — aggregated
area/category/product demand-change percentages, plus a participating-business
count for transparency. No route or table anywhere stores or returns a figure
tied to one business; `seed_market_synthetic.py` demonstrates the intended
aggregation boundary by simulating transactions only in memory and persisting
just the final aggregates, matching blueprint section 22's privacy rule.

