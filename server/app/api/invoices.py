from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app import crud, models
from app.core.ai_provider import get_ai_provider
from app.core.security import get_current_user

router = APIRouter(prefix="/api/invoices", tags=["invoices"])

@router.post('/', status_code=201)
def upload_invoice(payload: dict, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    vendor_id = payload.get('vendor_id')
    total_amount = payload.get('total_amount')
    invoice_number = payload.get('invoice_number')
    if not vendor_id or total_amount is None or not invoice_number:
        raise HTTPException(status_code=400, detail='vendor_id, invoice_number and total_amount required')
    invoice = crud.create_invoice(db, current_user.organization_id, vendor_id, invoice_number, total_amount, currency=payload.get('currency'))
    return { 'id': invoice.id, 'status': invoice.status }

@router.get('/')
def list_invoices(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    invs = crud.list_invoices(db, current_user.organization_id)
    out = []
    for i in invs:
        out.append({'id': i.id, 'invoice_number': i.invoice_number, 'total_amount': float(i.total_amount), 'status': i.status})
    return out

@router.get('/{invoice_id}')
def get_invoice(invoice_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    inv = crud.get_invoice(db, invoice_id, current_user.organization_id)
    if not inv:
        raise HTTPException(status_code=404, detail='Invoice not found')
    return {
        'id': inv.id,
        'invoice_number': inv.invoice_number,
        'total_amount': float(inv.total_amount),
        'status': inv.status
    }

@router.post('/{invoice_id}/analyze')
def analyze_invoice(invoice_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    inv = crud.get_invoice(db, invoice_id, current_user.organization_id)
    if not inv:
        raise HTTPException(status_code=404, detail='Invoice not found')
    result = crud.analyze_invoice_rules(db, inv)

    # Call AI provider for explainability and additional signals
    ai = get_ai_provider()
    ai_findings = ai.analyze_invoice({'invoice_number': inv.invoice_number, 'total_amount': float(inv.total_amount)})
    explanation = ai.explain_risk({'deterministic_rules': result.get('rules', []), 'invoice': {'total_amount': float(inv.total_amount), 'invoice_number': inv.invoice_number}})
    # merge ai explanation into evidence
    result['evidence']['ai_explanation'] = explanation

    rs = crud.save_risk_score(db, current_user.organization_id, inv.id, result, ai_findings=ai_findings, provider='mock')
    if result['score'] >= 30:
        severity = result['level']
        reason = 'Deterministic rules triggered: ' + ','.join(result['rules'])
        crud.create_fraud_alert(db, current_user.organization_id, inv.id, alert_type='INVOICE_ANOMALY', severity=severity, risk_score=result['score'], reason=reason, evidence=result.get('evidence'))
        if result['score'] >= 60:
            inv.status = 'HELD'
            db.add(inv)
            db.commit()
    return {'risk_score_id': rs.id, 'score': rs.score, 'level': rs.level, 'rules': rs.rules_triggered, 'evidence': rs.evidence, 'ai_findings': rs.ai_findings}
