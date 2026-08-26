from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, orgs, dashboard, vendors, invoices, payments, verifications, approvals, approval_policies
from app.db import session as db_session

app = FastAPI(title="AP Payment Fraud Sentinel - Backend")

# CORS for local frontend dev (Vite)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(orgs.router)
app.include_router(dashboard.router)
app.include_router(vendors.router)
app.include_router(invoices.router)
app.include_router(payments.router)
app.include_router(verifications.router)
app.include_router(approvals.router)
app.include_router(approval_policies.router)
app.include_router(__import__('app.api.notifications', fromlist=['router']).router)

@app.on_event("startup")
def startup_event():
    # create tables if not exist (simple development convenience)
    db = db_session.engine.connect()
    import app.models  # ensure models are imported so metadata exists
    from app.db.session import Base
    Base.metadata.create_all(bind=db_session.engine)
    db.close()

@app.get("/health")
def health():
    return {"status": "ok"}
