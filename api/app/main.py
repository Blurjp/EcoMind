from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import health, ingest, query, orgs, users, audits, alerts, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Ecomind API starting...")
    yield
    # Shutdown
    print("🛑 Ecomind API shutting down...")


app = FastAPI(
    title="Ecomind API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router)
app.include_router(ingest.router, prefix="/v1")
app.include_router(query.router, prefix="/v1")
app.include_router(orgs.router, prefix="/v1")
app.include_router(users.router, prefix="/v1")
app.include_router(audits.router, prefix="/v1")
app.include_router(alerts.router, prefix="/v1")
app.include_router(reports.router, prefix="/v1")


@app.get("/")
async def root():
    return {
        "service": "ecomind-api",
        "version": "0.1.0",
        "ts": datetime.utcnow().isoformat() + "Z",
    }