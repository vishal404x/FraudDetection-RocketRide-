from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.db.session import Base

class RiskScore(Base):
    __tablename__ = "risk_scores"
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True, index=True)
    score = Column(Integer, nullable=False)
    level = Column(String(50), nullable=False)
    rules_triggered = Column(JSON, nullable=True)
    evidence = Column(JSON, nullable=True)
    ai_findings = Column(JSON, nullable=True)
    provider = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
