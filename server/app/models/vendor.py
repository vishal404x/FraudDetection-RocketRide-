from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    legal_name = Column(String(255), nullable=False)
    vendor_code = Column(String(100), nullable=True, index=True)
    tax_id = Column(String(100), nullable=True)
    registration_number = Column(String(100), nullable=True)
    address = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    contacts = relationship("VendorContact", back_populates="vendor", cascade="all, delete-orphan")
    bank_accounts = relationship("VendorBankAccount", back_populates="vendor", cascade="all, delete-orphan")
