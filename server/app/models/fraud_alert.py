from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.db.session import Base

class FraudAlert(Base):
    __tablename__ = "fraud_alerts"
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)
    alert_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    risk_score = Column(Integer, nullable=True)
    reason = Column(String(1000), nullable=True)
    evidence = Column(JSON, nullable=True)
    status = Column(String(50), nullable=False, default="OPEN")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
