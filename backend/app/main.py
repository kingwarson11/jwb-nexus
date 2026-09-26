from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.config import settings
from app.routers import auth, businesses, suppliers, products, inventory, sales, expenses, reports, ai, market

# For the MVP we use create_all for simplicity. Move to Alembic migrations
# once the schema stabilizes (see database/ for a plain SQL reference schema).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="JWB Nexus API",
    description="AI-powered financial and commerce intelligence platform for African SMEs",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(businesses.router)
app.include_router(suppliers.router)
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(sales.router)
app.include_router(expenses.router)
app.include_router(reports.router)
app.include_router(ai.router)
app.include_router(market.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "JWB Nexus API"}


@app.get("/health")
def health():
    return {"status": "healthy"}
