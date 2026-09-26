"""
Seeds a demo business with products, a few days of sales, and expenses,
so the dashboard/inventory/reports screens aren't empty on first run.

Usage:
    python seed_demo.py
Uses whatever DATABASE_URL is set in your environment / .env file.
"""
import random
from datetime import date, timedelta

from app.database import Base, engine, SessionLocal
from app import models
from app.auth import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

DEMO_EMAIL = "demo@jwbnexus.com"
DEMO_PASSWORD = "demo1234"

user = db.query(models.User).filter(models.User.email == DEMO_EMAIL).first()
if not user:
    user = models.User(email=DEMO_EMAIL, hashed_password=hash_password(DEMO_PASSWORD), full_name="Benjamin Owusu")
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Created demo user: {DEMO_EMAIL} / {DEMO_PASSWORD}")
else:
    print("Demo user already exists, reusing it.")

business = db.query(models.Business).filter(models.Business.owner_id == user.id).first()
if not business:
    business = models.Business(owner_id=user.id, name="Benjamin's Mini Mart", category="Retail / Mini Mart",
                                area="East Legon", currency="GHS")
    db.add(business)
    db.commit()
    db.refresh(business)
    print(f"Created business: {business.name}")

PRODUCTS = [
    dict(name="Bottled Water (500ml)", category="Beverages", selling_price=5, cost_price=3, quantity=320, minimum_stock=30),
    dict(name="Malt Drink", category="Beverages", selling_price=8, cost_price=5.5, quantity=160, minimum_stock=15),
    dict(name="Indomie Chicken", category="Groceries", selling_price=6, cost_price=4, quantity=420, minimum_stock=40),
    dict(name="Bread", category="Bakery", selling_price=12, cost_price=8, quantity=90, minimum_stock=10),
    dict(name="FanYogo", category="Dairy", selling_price=4, cost_price=2.5, quantity=110, minimum_stock=20,
         expiry_date=date.today() + timedelta(days=6)),
    dict(name="Yoghurt (Sachet)", category="Dairy", selling_price=3, cost_price=1.8, quantity=90, minimum_stock=15,
         expiry_date=date.today() + timedelta(days=4)),
    dict(name="Milo (Tin)", category="Groceries", selling_price=45, cost_price=35, quantity=25, minimum_stock=10),
]

existing = {p.name for p in db.query(models.Product).filter(models.Product.business_id == business.id)}
products = []
for p in PRODUCTS:
    if p["name"] in existing:
        products.append(db.query(models.Product).filter(models.Product.business_id == business.id,
                                                          models.Product.name == p["name"]).first())
        continue
    product = models.Product(business_id=business.id, **p)
    db.add(product)
    db.flush()
    db.add(models.InventoryMovement(product_id=product.id, movement_type=models.MovementType.PURCHASE,
                                     quantity_change=product.quantity, note="Seed stock"))
    products.append(product)
db.commit()
print(f"Seeded {len(products)} products.")

# 14 days of realistic random sales, biased toward beverages (for the "demand rising" story)
existing_sales = db.query(models.Sale).filter(models.Sale.business_id == business.id).count()
if existing_sales == 0:
    for day_offset in range(14, -1, -1):  # includes today (offset 0) so the dashboard shows live activity
        sale_date = date.today() - timedelta(days=day_offset)
        num_sales = random.randint(3, 9)
        for _ in range(num_sales):
            chosen = random.sample(products, k=random.randint(1, 3))
            subtotal, cogs = 0.0, 0.0
            sale = models.Sale(business_id=business.id, subtotal=0, discount=0, total=0, cost_of_goods_sold=0)
            sale.created_at = __import__("datetime").datetime.combine(sale_date, __import__("datetime").time(hour=random.randint(8, 19)))
            db.add(sale)
            db.flush()
            for product in chosen:
                qty = random.randint(1, 5)
                if product.quantity < qty:
                    continue
                line_total = product.selling_price * qty
                subtotal += line_total
                cogs += product.cost_price * qty
                db.add(models.SaleItem(sale_id=sale.id, product_id=product.id, quantity=qty,
                                        unit_price=product.selling_price, unit_cost=product.cost_price, line_total=line_total))
                product.quantity -= qty
                db.add(models.InventoryMovement(product_id=product.id, movement_type=models.MovementType.SALE,
                                                 quantity_change=-qty, reference=sale.id))
            sale.subtotal = subtotal
            sale.total = subtotal
            sale.cost_of_goods_sold = cogs
            method = random.choice(["MOMO", "MOMO", "CASH", "BANK"])
            db.add(models.Payment(sale_id=sale.id, method=method, amount=subtotal,
                                   status=models.PaymentStatus.CONFIRMED,
                                   provider_reference=f"SEED-{sale.id[:8]}" if method == "MOMO" else None))
    db.commit()
    print("Seeded 14 days of demo sales.")
else:
    print("Sales already exist, skipping sales seed.")

existing_expenses = db.query(models.Expense).filter(models.Expense.business_id == business.id).count()
if existing_expenses == 0:
    EXPENSES = [
        ("rent", "Monthly shop rent", 1200, 25),
        ("electricity", "ECG bill", 180, 20),
        ("transport", "Restock transport", 90, 15),
        ("salaries", "Shop assistant wages", 600, 10),
        ("internet", "Data bundle", 60, 5),
    ]
    for category, desc, amount, days_ago in EXPENSES:
        db.add(models.Expense(business_id=business.id, category=category, description=desc, amount=amount,
                               date=date.today() - timedelta(days=days_ago)))
    db.commit()
    print("Seeded demo expenses.")
else:
    print("Expenses already exist, skipping.")

print("\nDemo data ready.")
print(f"Login with: {DEMO_EMAIL} / {DEMO_PASSWORD}")
db.close()
