from datetime import datetime, date as date_type
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# ---------- Auth ----------

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------- Business ----------

class BusinessCreate(BaseModel):
    name: str
    category: Optional[str] = None
    area: Optional[str] = None
    currency: str = "GHS"


class BusinessOut(BusinessCreate):
    id: str
    owner_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Supplier ----------

class SupplierCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    notes: Optional[str] = None


class SupplierOut(SupplierCreate):
    id: str
    business_id: str

    class Config:
        from_attributes = True


# ---------- Product ----------

class ProductCreate(BaseModel):
    name: str
    category: Optional[str] = None
    selling_price: float
    cost_price: float
    quantity: int = 0
    minimum_stock: int = 5
    expiry_date: Optional[date_type] = None
    supplier_id: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    selling_price: Optional[float] = None
    cost_price: Optional[float] = None
    minimum_stock: Optional[int] = None
    expiry_date: Optional[date_type] = None
    supplier_id: Optional[str] = None


class ProductOut(BaseModel):
    id: str
    business_id: str
    supplier_id: Optional[str]
    name: str
    category: Optional[str]
    selling_price: float
    cost_price: float
    quantity: int
    minimum_stock: int
    expiry_date: Optional[date_type]

    class Config:
        from_attributes = True


class StockAdjustment(BaseModel):
    quantity_change: int   # positive to add stock, negative to remove
    note: Optional[str] = None


# ---------- Sales / POS ----------

class SaleItemIn(BaseModel):
    product_id: str
    quantity: int


class PaymentIn(BaseModel):
    method: str   # MOMO | CASH | BANK | CARD
    amount: float
    provider_reference: Optional[str] = None


class SaleCreate(BaseModel):
    items: List[SaleItemIn]
    discount: float = 0
    payment: PaymentIn
    customer_id: Optional[str] = None


class SaleItemOut(BaseModel):
    product_id: str
    quantity: int
    unit_price: float
    line_total: float

    class Config:
        from_attributes = True


class SaleOut(BaseModel):
    id: str
    business_id: str
    subtotal: float
    discount: float
    total: float
    status: str
    created_at: datetime
    items: List[SaleItemOut] = []

    class Config:
        from_attributes = True


# ---------- Expenses ----------

class ExpenseCreate(BaseModel):
    category: str
    description: Optional[str] = None
    amount: float
    date: Optional[date_type] = None


class ExpenseOut(ExpenseCreate):
    id: str
    business_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Reports ----------

class DashboardSummary(BaseModel):
    today_revenue: float
    today_sales_count: int
    gross_profit_today: float
    inventory_value: float
    low_stock_count: int
    expiring_soon_count: int
    slow_moving_count: int


class IncomeStatement(BaseModel):
    period_start: date_type
    period_end: date_type
    revenue: float
    cost_of_goods_sold: float
    gross_profit: float
    operating_expenses: float
    net_profit: float


class CashFlowStatement(BaseModel):
    period_start: date_type
    period_end: date_type
    opening_balance: float
    cash_in: float
    cash_out: float
    closing_balance: float
    net_cash_flow: float


# ---------- AI Business Analyst ----------

class AIQuery(BaseModel):
    question: str


class AIResponse(BaseModel):
    answer: str
    facts: dict   # the verified data the answer was grounded in — shown so the merchant can trust it


# ---------- Market Intelligence ----------

class MarketTrendOut(BaseModel):
    area: str
    category: str
    product_name: Optional[str]
    period_start: date_type
    period_end: date_type
    demand_change_pct: float
    participating_businesses: int

    class Config:
        from_attributes = True
