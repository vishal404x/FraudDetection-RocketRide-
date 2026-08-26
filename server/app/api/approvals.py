from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app import crud, models
from app.core.security import get_current_user

router = APIRouter(prefix="/api/approvals", tags=["approvals"])

@router.get('/')
def list_approvals(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = current_user.organization_id
    aprs = db.query(models.ApprovalRequest).filter(models.ApprovalRequest.organization_id == org_id).all()
    out = []
    for a in aprs:
        out.append({'id': a.id, 'payment_id': a.payment_id, 'status': a.status, 'required_roles': a.required_roles, 'created_at': a.created_at})
    return out

@router.get('/{approval_id}')
def get_approval(approval_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = current_user.organization_id
    apr = crud.get_approval_request(db, approval_id)
    if not apr or apr.organization_id != org_id:
        raise HTTPException(status_code=404, detail='Approval request not found')
    acts = db.query(models.ApprovalAction).filter(models.ApprovalAction.approval_request_id == approval_id).all()
    actions = [{'id': act.id, 'user_id': act.user_id, 'action': act.action, 'comment': act.comment, 'created_at': act.created_at} for act in acts]
    return {'id': apr.id, 'payment_id': apr.payment_id, 'status': apr.status, 'required_roles': apr.required_roles, 'actions': actions, 'created_at': apr.created_at}

@router.post('/{approval_id}/approve')
def approve(approval_id: int, payload: dict, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = current_user.organization_id
    apr = crud.get_approval_request(db, approval_id)
    if not apr or apr.organization_id != org_id:
        raise HTTPException(status_code=404, detail='Approval request not found')
    # check that current user role is allowed to approve
    allowed = False
    if current_user.role in (apr.required_roles or []):
        allowed = True
    if current_user.role in ('Owner', 'Admin'):
        allowed = True
    if not allowed:
        raise HTTPException(status_code=403, detail='User not authorized to approve this request')
    comment = payload.get('comment')
    act = crud.add_approval_action(db, apr.id, current_user.id, 'APPROVED', comment)
    # create audit log
    crud.create_audit_log(db, org_id, current_user.id, action='APPROVAL_GRANTED', object_type='approval_request', object_id=apr.id, previous_state=None, new_state=apr.status, reason=comment)
    # notify payment creator or organization admins
    try:
        payment = db.query(models.Payment).filter(models.Payment.id == apr.payment_id).first()
        # notify org admins/owner about approval result
        crud.create_notification(db, organization_id=org_id, user_id=None, target_roles=['Owner','Admin'], notif_type='APPROVAL_GRANTED', message=f'Approval {apr.id} granted by {current_user.email}', metadata={'approval_id': apr.id, 'payment_id': apr.payment_id})
    except Exception:
        db.rollback()
    return {'ok': True, 'approval_status': apr.status}

@router.post('/{approval_id}/reject')
def reject(approval_id: int, payload: dict, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = current_user.organization_id
    apr = crud.get_approval_request(db, approval_id)
    if not apr or apr.organization_id != org_id:
        raise HTTPException(status_code=404, detail='Approval request not found')
    # check that current user role is allowed to reject
    allowed = False
    if current_user.role in (apr.required_roles or []):
        allowed = True
    if current_user.role in ('Owner', 'Admin'):
        allowed = True
    if not allowed:
        raise HTTPException(status_code=403, detail='User not authorized to reject this request')
    comment = payload.get('comment')
    act = crud.add_approval_action(db, apr.id, current_user.id, 'REJECTED', comment)
    # create audit log
    crud.create_audit_log(db, org_id, current_user.id, action='APPROVAL_REJECTED', object_type='approval_request', object_id=apr.id, previous_state=None, new_state=apr.status, reason=comment)
    try:
        crud.create_notification(db, organization_id=org_id, user_id=None, target_roles=['Owner','Admin'], notif_type='APPROVAL_REJECTED', message=f'Approval {apr.id} rejected by {current_user.email}', metadata={'approval_id': apr.id, 'payment_id': apr.payment_id})
    except Exception:
        db.rollback()
    return {'ok': True, 'approval_status': apr.status}
