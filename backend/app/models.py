import enum
import uuid
from datetime import datetime, date

from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, Date,
    ForeignKey, Enum, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class PaymentMethod(str, enum.Enum):
    MOMO = "MOMO"
    CASH = "CASH"
    BANK = "BANK"
    CARD = "CARD"


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"


class MovementType(str, enum.Enum):
    PURCHASE = "PURCHASE"
    SALE = "SALE"
    ADJUSTMENT = "ADJUSTMENT"
    EXPIRY_WRITE_OFF = "EXPIRY_WRITE_OFF"


# ---------- Users & Businesses ----------

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    businesses = relationship("Business", back_populates="owner")


class Business(Base):
    __tablename__ = "businesses"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    owner_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)        # e.g. "Retail / Mini Mart"
    area = Column(String, nullable=True)             # e.g. "East Legon"
    currency = Column(String, default="GHS")
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="businesses")
    products = relationship("Product", back_populates="business")
    suppliers = relationship("Supplier", back_populates="business")
    sales = relationship("Sale", back_populates="business")
    expenses = relationship("Expense", back_populates="business")


# ---------- Products & Inventory ----------

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    business_id = Column(UUID(as_uuid=False), ForeignKey("businesses.id"), nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    business = relationship("Business", back_populates="suppliers")
    products = relationship("Product", back_populates="supplier")


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    business_id = Column(UUID(as_uuid=False), ForeignKey("businesses.id"), nullable=False)
    supplier_id = Column(UUID(as_uuid=False), ForeignKey("suppliers.id"), nullable=True)

    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    selling_price = Column(Float, nullable=False, default=0)
    cost_price = Column(Float, nullable=False, default=0)
    quantity = Column(Integer, nullable=False, default=0)
    minimum_stock = Column(Integer, nullable=False, default=5)
    expiry_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    business = relationship("Business", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    movements = relationship("InventoryMovement", back_populates="product")


class InventoryMovement(Base):
    """Every stock change (purchase, sale, adjustment, expiry write-off) is logged here."""
    __tablename__ = "inventory_movements"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    product_id = Column(UUID(as_uuid=False), ForeignKey("products.id"), nullable=False)
    movement_type = Column(Enum(MovementType), nullable=False)
    quantity_change = Column(Integer, nullable=False)   # positive = stock in, negative = stock out
    reference = Column(String, nullable=True)            # e.g. sale id or purchase id
    note = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="movements")


# ---------- Sales / POS ----------

class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    business_id = Column(UUID(as_uuid=False), ForeignKey("businesses.id"), nullable=False)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)


class Sale(Base):
    __tablename__ = "sales"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    business_id = Column(UUID(as_uuid=False), ForeignKey("businesses.id"), nullable=False)
    customer_id = Column(UUID(as_uuid=False), ForeignKey("customers.id"), nullable=True)

    subtotal = Column(Float, nullable=False, default=0)
    discount = Column(Float, nullable=False, default=0)
    total = Column(Float, nullable=False, default=0)
    cost_of_goods_sold = Column(Float, nullable=False, default=0)

    status = Column(String, default="COMPLETED")   # COMPLETED | REFUNDED
    created_at = Column(DateTime, default=datetime.utcnow)

    business = relationship("Business", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale")
    payment = relationship("Payment", back_populates="sale", uselist=False)


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    sale_id = Column(UUID(as_uuid=False), ForeignKey("sales.id"), nullable=False)
    product_id = Column(UUID(as_uuid=False), ForeignKey("products.id"), nullable=False)

    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    unit_cost = Column(Float, nullable=False, default=0)
    line_total = Column(Float, nullable=False)

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    sale_id = Column(UUID(as_uuid=False), ForeignKey("sales.id"), nullable=False)
    method = Column(Enum(PaymentMethod), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.CONFIRMED)
    provider_reference = Column(String, nullable=True)  # e.g. mock MoMo transaction id
    created_at = Column(DateTime, default=datetime.utcnow)

    sale = relationship("Sale", back_populates="payment")


# ---------- Finance ----------

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    business_id = Column(UUID(as_uuid=False), ForeignKey("businesses.id"), nullable=False)
    category = Column(String, nullable=False)   # rent, electricity, transport, salaries, internet, other
    description = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

    business = relationship("Business", back_populates="expenses")


# ---------- Market Intelligence ----------

class MarketMetric(Base):
    """
    Anonymised, aggregated demand signal — NEVER tied to an individual business.
    Populated by an aggregation job (see database/seed_market_synthetic.py for the
    MVP's synthetic dataset) or, eventually, a scheduled job that aggregates real
    participating-merchant sales data with no merchant-identifying fields retained.
    """
    __tablename__ = "market_metrics"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    area = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    product_name = Column(String, nullable=True)   # null = category-level metric

    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    demand_change_pct = Column(Float, nullable=False)   # e.g. +22.0 = demand up 22%
    participating_businesses = Column(Integer, nullable=False)  # transparency, never identities

    created_at = Column(DateTime, default=datetime.utcnow)
