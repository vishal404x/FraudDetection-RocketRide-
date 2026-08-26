from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from app.db.session import Base

class ApprovalPolicy(Base):
    __tablename__ = "approval_policies"
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False, default='default')
    # threshold amount which triggers creation of approval requests
    threshold_amount = Column(Float, nullable=False, default=500000.0)
    # default required roles for approvals above threshold
    required_roles = Column(JSON, nullable=True)  # e.g. ['Finance Manager', 'CFO']
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
