from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app import crud, models
from app.core.security import get_current_user, require_role

router = APIRouter(prefix="/api/payments", tags=["payments"])

@router.get('/')
def list_payments(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = current_user.organization_id
    payments = db.query(models.Payment).filter(models.Payment.organization_id == org_id).all()
    out = []
    for p in payments:
        out.append({'id': p.id, 'invoice_id': p.invoice_id, 'amount': float(p.amount), 'currency': p.currency, 'status': p.status, 'held': p.held, 'reason': p.reason})
    return out

@router.get('/{payment_id}')
def get_payment(payment_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = current_user.organization_id
    p = db.query(models.Payment).filter(models.Payment.id == payment_id, models.Payment.organization_id == org_id).first()
    if not p:
        raise HTTPException(status_code=404, detail='Payment not found')
    return {'id': p.id, 'invoice_id': p.invoice_id, 'amount': float(p.amount), 'currency': p.currency, 'status': p.status, 'held': p.held, 'reason': p.reason}

@router.post('/')
def create_payment_endpoint(payload: dict, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # who can create payments? Allow AP Specialist and above
    require_role(current_user, ['Owner', 'Admin', 'Finance Manager', 'AP Specialist'])
    invoice_id = payload.get('invoice_id')
    amount = payload.get('amount')
    currency = payload.get('currency', 'INR')
    if not amount:
        raise HTTPException(status_code=400, detail='amount required')
    payment = crud.create_payment(db, current_user.organization_id, invoice_id, amount, currency)
    # create audit log for creation
    crud.create_audit_log(db, current_user.organization_id, current_user.id, action='PAYMENT_CREATED', object_type='payment', object_id=payment.id, previous_state=None, new_state=payment.status, reason=payload.get('reason'))
    return {'id': payment.id, 'status': payment.status}

@router.post('/{payment_id}/hold')
def hold_payment(payment_id: int, reason: dict, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = current_user.organization_id
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id, models.Payment.organization_id == org_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail='Payment not found')
    prev_state = payment.status
    payment.status = 'HELD'
    payment.held = 'YES'
    payment.reason = reason.get('reason') if isinstance(reason, dict) else str(reason)
    db.add(payment)
    db.commit()
    # create audit log
    crud.create_audit_log(db, org_id, current_user.id, action='PAYMENT_HELD', object_type='payment', object_id=payment.id, previous_state=prev_state, new_state=payment.status, reason=payment.reason)
    return {'id': payment.id, 'status': payment.status}

@router.post('/{payment_id}/release')
def release_payment(payment_id: int, payload: dict, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # only authorized human roles may release
    require_role(current_user, ['Owner', 'Admin', 'Finance Manager'])
    org_id = current_user.organization_id
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id, models.Payment.organization_id == org_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail='Payment not found')
    # check for approval requests
    apr = crud.get_approval_for_payment(db, payment.id)
    if apr and not crud.is_approval_satisfied(db, apr.id):
        raise HTTPException(status_code=403, detail='Payment requires approval before it can be released')

    prev_state = payment.status
    payment.status = 'RELEASED'
    payment.held = 'NO'
    reason = payload.get('reason')
    payment.reason = reason
    db.add(payment)
    db.commit()
    crud.create_audit_log(db, org_id, current_user.id, action='PAYMENT_RELEASED', object_type='payment', object_id=payment.id, previous_state=prev_state, new_state=payment.status, reason=reason)
    return {'id': payment.id, 'status': payment.status}

@router.post('/{payment_id}/reject')
def reject_payment(payment_id: int, payload: dict, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # only authorized human roles may reject
    require_role(current_user, ['Owner', 'Admin', 'Finance Manager'])
    org_id = current_user.organization_id
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id, models.Payment.organization_id == org_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail='Payment not found')
    prev_state = payment.status
    payment.status = 'REJECTED'
    payment.held = 'NO'
    reason = payload.get('reason')
    payment.reason = reason
    db.add(payment)
    db.commit()
    crud.create_audit_log(db, org_id, current_user.id, action='PAYMENT_REJECTED', object_type='payment', object_id=payment.id, previous_state=prev_state, new_state=payment.status, reason=reason)
    return {'id': payment.id, 'status': payment.status}