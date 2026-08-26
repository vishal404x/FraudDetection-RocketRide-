"""Seed demo organization, user, and vendors for Slice 1/2"""
from app.db.session import SessionLocal, engine
from app import crud
from app.db.session import Base


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        org = crud.create_organization(db, 'Demo Corp')
        user = crud.create_user(db, 'admin@demo.com', 'password', org.id, full_name='Demo Admin', role='Owner', is_superuser=True)
        # Demo vendors
        vendors = [
            ('ABC Manufacturing','ABC001'),
            ('XYZ Logistics','XYZ002'),
            ('Delta Supplies','DEL003'),
            ('Acme Services','ACM004'),
            ('Global Components','GLO005')
        ]
        for name, code in vendors:
            v = crud.create_vendor(db, org.id, name, vendor_code=code)
            # add a bank account
            crud.create_vendor_bank_account(db, v.id, 'HDFC Bank', '1234123412341234', ifsc_swift='HDFC0001234', account_holder=name)
            # add a trusted contact
            crud.create_vendor_contact(db, v.id, f'Contact {name}', f'contact@{name.replace(" ", "").lower()}.com', phone='+919999999999', is_trusted=True)
        print('Seeding complete. Org ID:', org.id)
    finally:
        db.close()

if __name__ == '__main__':
    seed()
