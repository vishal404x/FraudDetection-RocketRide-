from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app import crud, models
from app.core.security import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@router.get('/')
def list_notifications(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = current_user.organization_id
    notifs = crud.list_notifications_for_user(db, org_id, current_user.id, current_user.role)
    out = []
    for n in notifs:
        out.append({'id': n.id, 'notif_type': n.notif_type, 'message': n.message, 'metadata': n.metadata, 'seen': n.seen, 'created_at': n.created_at})
    return out

@router.post('/{notification_id}/mark-seen')
def mark_seen(notification_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    n = crud.mark_notification_seen(db, notification_id, current_user.id)
    if not n:
        raise HTTPException(status_code=404, detail='Notification not found')
    return {'ok': True}
