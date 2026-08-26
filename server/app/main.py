from fastapi import FastAPI
from app.api import auth, orgs, dashboard, vendors, invoices, payments, verifications
from app.db import session as db_session

app = FastAPI(title="AP Payment Fraud Sentinel - Backend")

app.include_router(auth.router)
app.include_router(orgs.router)
app.include_router(dashboard.router)
app.include_router(vendors.router)
app.include_router(invoices.router)
app.include_router(payments.router)

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
