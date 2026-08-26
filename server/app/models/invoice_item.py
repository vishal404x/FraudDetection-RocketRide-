from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    description = Column(String(1000), nullable=True)
    quantity = Column(Numeric(12,2), nullable=True)
    unit_price = Column(Numeric(12,2), nullable=True)
    total = Column(Numeric(12,2), nullable=True)

    invoice = relationship("Invoice", back_populates="items")
