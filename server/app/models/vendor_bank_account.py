from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class VendorBankAccount(Base):
    __tablename__ = "vendor_bank_accounts"
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    bank_name = Column(String(255), nullable=False)
    # store encrypted account number; do not store plaintext
    account_number_encrypted = Column(String(2000), nullable=True)
    masked_account = Column(String(255), nullable=False)
    ifsc_swift = Column(String(100), nullable=True)
    account_holder = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_verified_at = Column(DateTime(timezone=True), nullable=True)

    vendor = relationship("Vendor", back_populates="bank_accounts")
