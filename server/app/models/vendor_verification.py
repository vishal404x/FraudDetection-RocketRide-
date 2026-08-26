from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.session import Base

class VendorVerification(Base):
    __tablename__ = "vendor_verifications"
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    bank_account_id = Column(Integer, ForeignKey("vendor_bank_accounts.id"), nullable=True)
    verification_type = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="PENDING")
    notes = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
