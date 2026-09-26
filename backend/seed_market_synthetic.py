"""
Synthetic Market Intelligence dataset (blueprint section 21):
  1,000 simulated transactions | 50 products | 20 businesses
  5 business categories | 3 areas | 12 weeks

This script simulates transactions in memory ONLY to compute aggregated,
anonymised demand-change metrics — no per-business or per-transaction data
is ever written to the database. Only the final market_metrics rows are
persisted, which is the same privacy boundary production aggregation would
need to respect (blueprint section 22, Data Privacy).

Usage:
    python seed_market_synthetic.py
"""
import random
from datetime import date, timedelta
from collections import defaultdict

from app.database import Base, engine, SessionLocal
from app import models

random.seed(42)

Base.metadata.create_all(bind=engine)
db = SessionLocal()

AREAS = ["East Legon", "Osu", "Madina"]
CATEGORIES = {
    "Beverages": ["Bottled Water", "Malt Drink", "Soft Drink", "Fruit Juice"],
    "Groceries": ["Indomie", "Rice (5kg)", "Cooking Oil", "Milo", "Sugar"],
    "Dairy": ["Yoghurt", "FanYogo", "Milk Powder"],
    "Bakery": ["Bread", "Meat Pie", "Doughnuts"],
    "Household": ["Detergent", "Toilet Roll", "Dish Soap"],
}
PRODUCT_NAMES = [f"{name} #{i+1}" if i > 0 else name
                 for cat, names in CATEGORIES.items() for i, name in enumerate(names * 3)][:50]
PRODUCT_CATEGORY = {}
i = 0
flat_products = []
for cat, names in CATEGORIES.items():
    for n in range(10):  # 5 categories x 10 = 50 products
        pname = f"{names[n % len(names)]} {n // len(names) + 1}"
        flat_products.append(pname)
        PRODUCT_CATEGORY[pname] = cat

BUSINESSES = [{"id": f"biz_{i}", "area": random.choice(AREAS)} for i in range(20)]

WEEKS = 12
TOTAL_TRANSACTIONS = 1000

# Each "transaction" = one business selling one product in one week, with a quantity.
# We deliberately trend bottled-water-type (Beverages) demand upward across the weeks,
# and a couple of products downward, so the resulting metrics tell a believable story
# — matching the blueprint's Figure 8.1 / 9.1 worked examples.
weekly_qty = defaultdict(lambda: defaultdict(int))   # week -> product -> total qty
weekly_participants = defaultdict(lambda: defaultdict(set))  # week -> product -> business ids

for _ in range(TOTAL_TRANSACTIONS):
    week = random.randint(0, WEEKS - 1)
    product = random.choice(flat_products)
    business = random.choice(BUSINESSES)

    base_qty = random.randint(5, 40)
    category = PRODUCT_CATEGORY[product]
    trend_factor = 1.0
    if category == "Beverages":
        trend_factor = 1.0 + (week / WEEKS) * 0.6       # rising demand
    elif category == "Household":
        trend_factor = 1.0 - (week / WEEKS) * 0.4        # declining demand
    qty = max(1, int(base_qty * trend_factor))

    weekly_qty[week][product] += qty
    weekly_participants[week][product].add(business["id"])

# Aggregate: compare the last 4 weeks against the previous 4 weeks, per product and per category.
recent_weeks = range(WEEKS - 4, WEEKS)
baseline_weeks = range(WEEKS - 8, WEEKS - 4)

today = date.today()
period_end = today
period_start = today - timedelta(weeks=4)

existing = db.query(models.MarketMetric).count()
if existing > 0:
    print(f"{existing} market_metrics rows already exist — skipping (delete them first to reseed).")
else:
    created = 0
    for product in flat_products:
        recent_total = sum(weekly_qty[w].get(product, 0) for w in recent_weeks)
        baseline_total = sum(weekly_qty[w].get(product, 0) for w in baseline_weeks)
        participants = set()
        for w in recent_weeks:
            participants |= weekly_participants[w].get(product, set())

        if baseline_total == 0 or len(participants) < 2:
            continue  # not enough signal to report — protects anonymity too (min sample size)

        change_pct = round(((recent_total - baseline_total) / baseline_total) * 100, 1)
        area = random.choice(AREAS)  # in the synthetic set we assign an area per metric for demo variety

        db.add(models.MarketMetric(
            area=area,
            category=PRODUCT_CATEGORY[product],
            product_name=product,
            period_start=period_start,
            period_end=period_end,
            demand_change_pct=change_pct,
            participating_businesses=len(participants),
        ))
        created += 1

    # Category-level roll-ups too (product_name = None), one per area
    for area in AREAS:
        for category in CATEGORIES:
            cat_products = [p for p, c in PRODUCT_CATEGORY.items() if c == category]
            recent_total = sum(weekly_qty[w].get(p, 0) for w in recent_weeks for p in cat_products)
            baseline_total = sum(weekly_qty[w].get(p, 0) for w in baseline_weeks for p in cat_products)
            if baseline_total == 0:
                continue
            change_pct = round(((recent_total - baseline_total) / baseline_total) * 100, 1)
            db.add(models.MarketMetric(
                area=area, category=category, product_name=None,
                period_start=period_start, period_end=period_end,
                demand_change_pct=change_pct, participating_businesses=len(BUSINESSES),
            ))
            created += 1

    db.commit()
    print(f"Created {created} anonymised market_metrics rows from a synthetic dataset "
          f"({TOTAL_TRANSACTIONS} simulated transactions, {len(flat_products)} products, "
          f"{len(BUSINESSES)} businesses, {len(CATEGORIES)} categories, {len(AREAS)} areas, {WEEKS} weeks).")

db.close()
