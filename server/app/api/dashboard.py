from fastapi import APIRouter, Depends
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app import models
from sqlalchemy import or_

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get('/')
def dashboard_overview(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return organization-scoped dashboard metrics for the authenticated user."""
    org_id = current_user.organization_id

    invoices_screened = db.query(models.Invoice).filter(models.Invoice.organization_id == org_id).count()
    payments_processed = db.query(models.Payment).filter(models.Payment.organization_id == org_id, models.Payment.status == 'PAID').count()
    payments_held = db.query(models.Payment).filter(models.Payment.organization_id == org_id).filter(or_(models.Payment.status == 'HELD', models.Payment.held == 'YES')).count()
    high_risk_transactions = db.query(models.RiskScore).filter(models.RiskScore.organization_id == org_id, models.RiskScore.score >= 60).count()
    fraud_attempts = db.query(models.FraudAlert).filter(models.FraudAlert.organization_id == org_id).count()
    fraud_prevented = db.query(models.FraudAlert).filter(models.FraudAlert.organization_id == org_id, models.FraudAlert.status.in_(['RESOLVED','CLOSED'])).count()

    recent_alerts_q = db.query(models.FraudAlert).filter(models.FraudAlert.organization_id == org_id).order_by(models.FraudAlert.created_at.desc()).limit(5)
    recent_alerts = []
    for a in recent_alerts_q:
        recent_alerts.append({
            'id': a.id,
            'alert_type': a.alert_type,
            'severity': a.severity,
            'risk_score': a.risk_score,
            'reason': a.reason,
            'status': a.status,
            'created_at': a.created_at.isoformat() if a.created_at else None
        })

    return {
        "invoices_screened": invoices_screened,
        "payments_processed": payments_processed,
        "payments_held": payments_held,
        "high_risk_transactions": high_risk_transactions,
        "fraud_attempts": fraud_attempts,
        "fraud_prevented": fraud_prevented,
        "recent_alerts": recent_alerts,
    }
