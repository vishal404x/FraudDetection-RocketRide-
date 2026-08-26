from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app import crud, models
from app.core.security import get_current_user

router = APIRouter(prefix="/api/vendors", tags=["vendors"])

@router.post('/', status_code=201)
def create_vendor(payload: dict, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = current_user.organization_id
    vendor = crud.create_vendor(db, org_id, payload.get('legal_name'), payload.get('vendor_code'), payload.get('tax_id'), payload.get('registration_number'), payload.get('address'))
    return {'id': vendor.id, 'legal_name': vendor.legal_name}

@router.get('/')
def list_vendors(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = current_user.organization_id
    vendors = crud.list_vendors(db, org_id)
    out = []
    for v in vendors:
        out.append({
            'id': v.id,
            'legal_name': v.legal_name,
            'vendor_code': v.vendor_code,
            'tax_id': v.tax_id,
            'registration_number': v.registration_number,
            'address': v.address,
            'created_at': v.created_at.isoformat()
        })
    return out

@router.get('/{vendor_id}')
def get_vendor(vendor_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = current_user.organization_id
    v = crud.get_vendor(db, vendor_id, org_id)
    if not v:
        raise HTTPException(status_code=404, detail='Vendor not found')
    return {
        'id': v.id,
        'legal_name': v.legal_name,
        'vendor_code': v.vendor_code,
        'tax_id': v.tax_id,
        'registration_number': v.registration_number,
        'address': v.address,
        'contacts': [{'id': c.id, 'name': c.name, 'email': c.email, 'phone': c.phone, 'is_trusted': c.is_trusted} for c in v.contacts],
        'bank_accounts': [{'id': b.id, 'bank_name': b.bank_name, 'masked_account': b.masked_account, 'ifsc_swift': b.ifsc_swift, 'account_holder': b.account_holder, 'is_verified': b.is_verified, 'created_at': b.created_at.isoformat()} for b in v.bank_accounts]
    }

@router.post('/{vendor_id}/bank_accounts', status_code=201)
def add_bank_account(vendor_id: int, payload: dict, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    bank_name = payload.get('bank_name')
    account_number = payload.get('account_number')
    if not bank_name or not account_number:
        raise HTTPException(status_code=400, detail='bank_name and account_number required')
    vendor = crud.get_vendor(db, vendor_id, current_user.organization_id)
    if not vendor:
        raise HTTPException(status_code=404, detail='Vendor not found')
    account = crud.create_vendor_bank_account(db, vendor_id, bank_name, account_number, payload.get('ifsc_swift'), payload.get('account_holder'))
    return { 'id': account.id, 'masked_account': account.masked_account, 'bank_name': account.bank_name }

@router.post('/{vendor_id}/contacts', status_code=201)
def add_contact(vendor_id: int, payload: dict, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    name = payload.get('name')
    email = payload.get('email')
    phone = payload.get('phone')
    is_trusted = bool(payload.get('is_trusted', False))
    if not name or not email:
        raise HTTPException(status_code=400, detail='name and email required')
    vendor = crud.get_vendor(db, vendor_id, current_user.organization_id)
    if not vendor:
        raise HTTPException(status_code=404, detail='Vendor not found')
    contact = crud.create_vendor_contact(db, vendor_id, name, email, phone, is_trusted)
    return { 'id': contact.id, 'name': contact.name, 'email': contact.email }
