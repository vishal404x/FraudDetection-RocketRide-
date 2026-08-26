from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app import crud, models
from app.core.security import get_current_user, require_role

router = APIRouter(prefix="/api/approval-policies", tags=["approval_policies"])

@router.get('/')
def get_policy(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = current_user.organization_id
    pol = crud.get_approval_policy(db, org_id)
    if not pol:
        raise HTTPException(status_code=404, detail='Approval policy not found')
    return {'id': pol.id, 'organization_id': pol.organization_id, 'threshold_amount': pol.threshold_amount, 'required_roles': pol.required_roles}

@router.patch('/')
def update_policy(payload: dict, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Only Admin/Owner may update org policy
    require_role(current_user, ['Owner', 'Admin'])
    org_id = current_user.organization_id
    threshold = payload.get('threshold_amount')
    req_roles = payload.get('required_roles')
    if threshold is None and req_roles is None:
        raise HTTPException(status_code=400, detail='No changes provided')
    pol = crud.update_approval_policy(db, org_id, threshold_amount=threshold, required_roles=req_roles)
    return {'id': pol.id, 'organization_id': pol.organization_id, 'threshold_amount': pol.threshold_amount, 'required_roles': pol.required_roles}
