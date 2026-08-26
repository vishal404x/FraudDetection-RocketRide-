from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    invoice_number = Column(String(200), nullable=False, index=True)
    invoice_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    subtotal = Column(Numeric(12,2), nullable=True)
    tax = Column(Numeric(12,2), nullable=True)
    total_amount = Column(Numeric(12,2), nullable=False)
    currency = Column(String(10), nullable=True)
    status = Column(String(50), nullable=False, default="UPLOADED")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    documents = relationship("InvoiceDocument", back_populates="invoice", cascade="all, delete-orphan")
