"""Seed demo payments for existing invoices (after seeding vendors and invoices)"""
from app.db.session import SessionLocal, engine
from app import crud
from app.db.session import Base
from app import models


def seed_payments():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        org = db.query(models.Organization).first()
        if not org:
            print('No organization found; run seed_demo first')
            return
        # create a demo invoice if none
        invoice = db.query(models.Invoice).first()
        if not invoice:
            # pick first vendor
            v = db.query(models.Vendor).first()
            if not v:
                print('No vendor found; run seed_demo first')
                return
            invoice = crud.create_invoice(db, org.id, v.id, 'INV-1000', 150000.00, currency='INR')
        # create payments linked to invoice
        from decimal import Decimal
        p = models.Payment(organization_id=org.id, invoice_id=invoice.id, amount=Decimal(invoice.total_amount), currency=invoice.currency or 'INR', status='PENDING', held='NO')
        db.add(p)
        db.commit()
        db.refresh(p)
        print('Seeded payment id', p.id)
    finally:
        db.close()

if __name__ == '__main__':
    seed_payments()
