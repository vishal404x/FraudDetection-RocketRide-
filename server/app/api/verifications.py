from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app import crud, models
from app.core.security import get_current_user, require_role

router = APIRouter(prefix="/api/verifications", tags=["verifications"])

@router.post('/')
def start_verification(payload: dict, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # payload should include vendor_id and optionally bank_account_id and type
    vendor_id = payload.get('vendor_id')
    bank_account_id = payload.get('bank_account_id')
    vtype = payload.get('verification_type', 'BANK_ACCOUNT')
    if not vendor_id:
        raise HTTPException(status_code=400, detail='vendor_id required')
    ver = models.VendorVerification(vendor_id=vendor_id, bank_account_id=bank_account_id, verification_type=vtype, status='PENDING', notes=payload.get('notes'))
    db.add(ver)
    db.commit()
    db.refresh(ver)
    crud.create_audit_log(db, current_user.organization_id, current_user.id, action='VERIFICATION_STARTED', object_type='verification', object_id=ver.id, previous_state=None, new_state='PENDING', reason=payload.get('notes'))
    return {'id': ver.id, 'status': ver.status}

@router.post('/{verification_id}/complete')
def complete_verification(verification_id: int, payload: dict, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Only trusted roles should complete verification
    require_role(current_user, ['Owner', 'Admin', 'Finance Manager', 'AP Specialist'])
    ver = db.query(models.VendorVerification).filter(models.VendorVerification.id == verification_id).first()
    if not ver:
        raise HTTPException(status_code=404, detail='Verification not found')
    result = payload.get('result')  # 'CONFIRMED', 'DENIED', 'UNABLE_TO_REACH'
    notes = payload.get('notes')
    from datetime import datetime
    ver.status = 'COMPLETED'
    ver.completed_at = datetime.utcnow()
    ver.notes = notes
    db.add(ver)
    db.commit()
    db.refresh(ver)
    # If confirmed and bank account present, mark bank account as verified
    if result == 'CONFIRMED' and ver.bank_account_id:
        acc = db.query(models.VendorBankAccount).filter(models.VendorBankAccount.id == ver.bank_account_id).first()
        if acc:
            acc.is_verified = True
            from datetime import datetime
            acc.last_verified_at = datetime.utcnow()
            db.add(acc)
            db.commit()
    crud.create_audit_log(db, current_user.organization_id, current_user.id, action='VERIFICATION_COMPLETED', object_type='verification', object_id=ver.id, previous_state='PENDING', new_state=ver.status, reason=notes)
    return {'id': ver.id, 'status': ver.status}
