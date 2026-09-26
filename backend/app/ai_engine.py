"""
AI Business Analyst (blueprint section 7 / AI Architecture section 18).

The pipeline is deliberately staged so the LLM never invents numbers:
  1. DATA        -> pulled from Postgres via SQLAlchemy
  2. ANALYTICS    -> app/analytics.py (velocity, coverage, decline %, etc.)
  3. RULES        -> gather_facts() below turns analytics into a flat, labelled
                     dict of verified facts
  4. LLM          -> explain_facts() turns those facts into plain language.
                     If ANTHROPIC_API_KEY isn't set, a template-based fallback
                     is used instead — the app works fully without an API key,
                     the LLM step only improves the phrasing.
"""
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import models, analytics

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


def gather_facts(db: Session, business: models.Business) -> dict:
    """Stage 1-3: verified, structured facts about the business right now."""
    now = datetime.utcnow()
    start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    today_sales = db.query(models.Sale).filter(
        models.Sale.business_id == business.id,
        models.Sale.created_at >= start_today,
        models.Sale.status == "COMPLETED",
    ).all()
    today_revenue = sum(s.total for s in today_sales)
    today_cogs = sum(s.cost_of_goods_sold for s in today_sales)

    week_ago = now - timedelta(days=7)
    prior_week = now - timedelta(days=14)
    this_week_revenue = (
        db.query(func.coalesce(func.sum(models.Sale.total), 0))
        .filter(models.Sale.business_id == business.id, models.Sale.created_at >= week_ago,
                models.Sale.status == "COMPLETED").scalar()
    ) or 0
    prior_week_revenue = (
        db.query(func.coalesce(func.sum(models.Sale.total), 0))
        .filter(models.Sale.business_id == business.id, models.Sale.created_at >= prior_week,
                models.Sale.created_at < week_ago, models.Sale.status == "COMPLETED").scalar()
    ) or 0
    revenue_change_pct = (
        round(((this_week_revenue - prior_week_revenue) / prior_week_revenue) * 100, 1)
        if prior_week_revenue else None
    )

    low_stock = analytics.low_stock_products(db, business.id)
    expiring = analytics.expiring_products(db, business.id, within_days=7)
    slow_moving = analytics.slow_moving_products(db, business.id)

    inventory_value = (
        db.query(func.coalesce(func.sum(models.Product.quantity * models.Product.cost_price), 0))
        .filter(models.Product.business_id == business.id).scalar()
    ) or 0

    expenses_this_month = (
        db.query(func.coalesce(func.sum(models.Expense.amount), 0))
        .filter(models.Expense.business_id == business.id,
                models.Expense.date >= now.date().replace(day=1)).scalar()
    ) or 0

    top_products = (
        db.query(models.Product.name, func.sum(models.SaleItem.quantity).label("qty"))
        .join(models.SaleItem, models.SaleItem.product_id == models.Product.id)
        .join(models.Sale, models.Sale.id == models.SaleItem.sale_id)
        .filter(models.Product.business_id == business.id, models.Sale.created_at >= week_ago)
        .group_by(models.Product.name).order_by(func.sum(models.SaleItem.quantity).desc()).limit(5).all()
    )

    return {
        "business_name": business.name,
        "today_revenue": round(today_revenue, 2),
        "today_gross_profit": round(today_revenue - today_cogs, 2),
        "this_week_revenue": round(this_week_revenue, 2),
        "revenue_change_pct_vs_prior_week": revenue_change_pct,
        "inventory_value": round(inventory_value, 2),
        "expenses_this_month": round(expenses_this_month, 2),
        "low_stock_products": [{"name": p.name, "quantity": p.quantity, "minimum_stock": p.minimum_stock} for p in low_stock],
        "expiring_soon_products": [{"name": p.name, "quantity": p.quantity, "expiry_date": str(p.expiry_date)} for p in expiring],
        "slow_moving_products": slow_moving,
        "top_selling_products_this_week": [{"name": n, "units_sold": int(q)} for n, q in top_products],
        "currency": business.currency,
    }


def _template_explain(question: str, facts: dict) -> str:
    """Fallback explainer — no external API required. Plain, grounded sentences from the facts dict."""
    lines = [f"Here's what the data shows for {facts['business_name']} right now:"]
    lines.append(f"- Today's revenue: {facts['currency']} {facts['today_revenue']} "
                 f"(gross profit {facts['currency']} {facts['today_gross_profit']}).")
    if facts["revenue_change_pct_vs_prior_week"] is not None:
        direction = "up" if facts["revenue_change_pct_vs_prior_week"] >= 0 else "down"
        lines.append(f"- This week's revenue is {direction} {abs(facts['revenue_change_pct_vs_prior_week'])}% "
                     f"vs. the previous week.")
    if facts["low_stock_products"]:
        names = ", ".join(p["name"] for p in facts["low_stock_products"][:5])
        lines.append(f"- Low stock: {names}. Consider restocking soon.")
    if facts["expiring_soon_products"]:
        names = ", ".join(f"{p['name']} ({p['quantity']} units, expires {p['expiry_date']})"
                          for p in facts["expiring_soon_products"][:5])
        lines.append(f"- Expiring within 7 days: {names}.")
    if facts["slow_moving_products"]:
        names = ", ".join(f"{p['product_name']} (down {p['decline_pct']}%)" for p in facts["slow_moving_products"][:5])
        lines.append(f"- Slow-moving: {names}. Consider reducing your next order for these.")
    if facts["top_selling_products_this_week"]:
        names = ", ".join(f"{p['name']} ({p['units_sold']} units)" for p in facts["top_selling_products_this_week"])
        lines.append(f"- Top sellers this week: {names}.")
    if not any([facts["low_stock_products"], facts["expiring_soon_products"], facts["slow_moving_products"]]):
        lines.append("- No urgent inventory issues detected.")
    return "\n".join(lines)


def _llm_explain(question: str, facts: dict) -> str:
    """Calls Claude to phrase the verified facts as a direct answer to the merchant's question."""
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    system = (
        "You are a business analyst for an African SME's point-of-sale and inventory system. "
        "You are given VERIFIED FACTS as JSON, already pulled from the business's database. "
        "Answer the merchant's question using ONLY these facts — never invent a number that "
        "isn't present in the JSON. Be direct, concise (3-5 sentences), and end with one concrete "
        "recommendation if the facts support one."
    )
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        system=system,
        messages=[{"role": "user", "content": f"VERIFIED FACTS:\n{facts}\n\nMERCHANT'S QUESTION:\n{question}"}],
    )
    return "".join(block.text for block in message.content if block.type == "text")


def explain_facts(question: str, facts: dict) -> str:
    """Stage 5 (LLM), with a graceful fallback so the feature works with zero external config."""
    if ANTHROPIC_API_KEY:
        try:
            return _llm_explain(question, facts)
        except Exception:
            pass  # fall through to the template explainer if the API call fails for any reason
    return _template_explain(question, facts)
