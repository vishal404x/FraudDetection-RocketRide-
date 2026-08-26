from sqlalchemy.orm import Session
from app import models
from passlib.context import CryptContext
from typing import List

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_organization(db: Session, name: str):
    org = models.Organization(name=name)
    db.add(org)
    db.commit()
    db.refresh(org)
    # create default approval policy for organization
    try:
        default_policy = models.ApprovalPolicy(organization_id=org.id, name='default', threshold_amount=500000.0, required_roles=['Finance Manager', 'CFO'])
        db.add(default_policy)
        db.commit()
        db.refresh(default_policy)
    except Exception:
        db.rollback()
    return org


def get_approval_policy(db: Session, organization_id: int):
    return db.query(models.ApprovalPolicy).filter(models.ApprovalPolicy.organization_id == organization_id).first()


def update_approval_policy(db: Session, organization_id: int, threshold_amount: float | None = None, required_roles: list | None = None):
    pol = get_approval_policy(db, organization_id)
    if not pol:
        pol = models.ApprovalPolicy(organization_id=organization_id, name='default', threshold_amount=(threshold_amount or 500000.0), required_roles=(required_roles or ['Finance Manager', 'CFO']))
        db.add(pol)
        db.commit()
        db.refresh(pol)
        return pol
    if threshold_amount is not None:
        pol.threshold_amount = float(threshold_amount)
    if required_roles is not None:
        pol.required_roles = required_roles
    db.add(pol)
    db.commit()
    db.refresh(pol)
    return pol

def create_user(db: Session, email: str, password: str, organization_id: int, full_name: str | None = None, role: str = 'Viewer', is_superuser: bool = False):
    hashed = pwd_context.hash(password)
    user = models.User(email=email, hashed_password=hashed, organization_id=organization_id, full_name=full_name, role=role, is_superuser=is_superuser)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Vendor CRUD
def create_vendor(db: Session, organization_id: int, legal_name: str, vendor_code: str | None = None, tax_id: str | None = None, registration_number: str | None = None, address: str | None = None):
    vendor = models.Vendor(organization_id=organization_id, legal_name=legal_name, vendor_code=vendor_code, tax_id=tax_id, registration_number=registration_number, address=address)
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor

def list_vendors(db: Session, organization_id: int) -> List[models.Vendor]:
    return db.query(models.Vendor).filter(models.Vendor.organization_id == organization_id).all()

def get_vendor(db: Session, vendor_id: int, organization_id: int):
    return db.query(models.Vendor).filter(models.Vendor.id == vendor_id, models.Vendor.organization_id == organization_id).first()

def mask_account_number(acc: str) -> str:
    # Keep last 4 digits visible, mask the rest into groups
    s = ''.join(ch for ch in acc if ch.isdigit())
    if len(s) <= 4:
        return '•••• ' + s
    last4 = s[-4:]
    masked_len = max(0, len(s) - 4)
    groups = []
    while masked_len > 0:
        take = 4 if masked_len >=4 else masked_len
        groups.append('••••')
        masked_len -= take
    return ' '.join(groups) + ' ' + last4

def create_vendor_bank_account(db: Session, vendor_id: int, bank_name: str, account_number: str, ifsc_swift: str | None = None, account_holder: str | None = None):
    from app.core.crypto import encrypt
    masked = mask_account_number(account_number)
    encrypted = encrypt(account_number)
    account = models.VendorBankAccount(vendor_id=vendor_id, bank_name=bank_name, account_number_encrypted=encrypted, masked_account=masked, ifsc_swift=ifsc_swift, account_holder=account_holder)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

def list_vendor_bank_accounts(db: Session, vendor_id: int):
    # return bank accounts with masked numbers only
    return db.query(models.VendorBankAccount).filter(models.VendorBankAccount.vendor_id == vendor_id).all()

def get_decrypted_account(db: Session, account_id: int, user):
    # Enforce that only authorized users call this helper; caller should check RBAC
    from app.core.crypto import decrypt
    acc = db.query(models.VendorBankAccount).filter(models.VendorBankAccount.id == account_id).first()
    if not acc or not acc.account_number_encrypted:
        return None
    try:
        return decrypt(acc.account_number_encrypted)
    except Exception:
        return None

def create_vendor_contact(db: Session, vendor_id: int, name: str, email: str, phone: str | None = None, is_trusted: bool = False):
    contact = models.VendorContact(vendor_id=vendor_id, name=name, email=email, phone=phone, is_trusted=is_trusted)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

# Invoice CRUD and simple analytics
def create_invoice(db: Session, organization_id: int, vendor_id: int, invoice_number: str, total_amount: float, currency: str | None = 'INR', invoice_date=None, due_date=None, subtotal: float | None = None, tax: float | None = None):
    invoice = models.Invoice(organization_id=organization_id, vendor_id=vendor_id, invoice_number=invoice_number, total_amount=total_amount, currency=currency, invoice_date=invoice_date, due_date=due_date, subtotal=subtotal, tax=tax)
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice

def list_invoices(db: Session, organization_id: int):
    return db.query(models.Invoice).filter(models.Invoice.organization_id == organization_id).all()

def get_invoice(db: Session, invoice_id: int, organization_id: int):
    return db.query(models.Invoice).filter(models.Invoice.id == invoice_id, models.Invoice.organization_id == organization_id).first()

# Risk engine (deterministic rules)
RULE_WEIGHTS = {
    'new_bank_account': 40,
    'recent_bank_detail_change': 25,
    'unusual_invoice_amount': 20,
    'new_vendor_contact': 15,
    'duplicate_invoice': 35,
    'new_vendor': 15,
    'unusual_payment_frequency': 10,
    'unauthorized_approver': 30,
    'new_payment_destination': 25,
    'suspicious_email': 20,
    'vendor_identity_mismatch': 30,
    'invoice_vendor_mismatch': 25,
}

def determine_risk_level(score: int) -> str:
    if score < 30:
        return 'LOW'
    if score < 60:
        return 'MEDIUM'
    if score < 80:
        return 'HIGH'
    return 'CRITICAL'

def analyze_invoice_rules(db: Session, invoice: models.Invoice):
    """Run deterministic rules and return a dict with score, rules_triggered, evidence"""
    rules = []
    evidence = {}
    total = 0

    vendor = db.query(models.Vendor).filter(models.Vendor.id == invoice.vendor_id).first()
    if not vendor:
        # new vendor
        rules.append('new_vendor')
        evidence['new_vendor'] = True
        total += RULE_WEIGHTS['new_vendor']
    else:
        # check duplicate invoice for vendor
        dup = db.query(models.Invoice).filter(models.Invoice.vendor_id == vendor.id, models.Invoice.invoice_number == invoice.invoice_number, models.Invoice.id != invoice.id).first()
        if dup:
            rules.append('duplicate_invoice')
            evidence['duplicate_invoice'] = {'existing_invoice_id': dup.id}
            total += RULE_WEIGHTS['duplicate_invoice']

        # check unusual amount vs historical mean
        hist = db.query(models.Invoice).filter(models.Invoice.vendor_id == vendor.id, models.Invoice.id != invoice.id).all()
        if hist:
            amounts = [float(h.total_amount) for h in hist if h.total_amount is not None]
            if amounts:
                import statistics
                mean = statistics.mean(amounts)
                stdev = statistics.pstdev(amounts) if len(amounts) > 1 else 0
                deviation = 0
                if mean > 0:
                    deviation = (float(invoice.total_amount) - mean) / mean
                evidence['vendor_mean_amount'] = mean
                evidence['vendor_stdev_amount'] = stdev
                evidence['deviation_pct'] = deviation
                # unusual if > 2x mean or > 3 stdev
                if deviation > 2 or (stdev and abs(float(invoice.total_amount) - mean) > 3*stdev):
                    rules.append('unusual_invoice_amount')
                    total += RULE_WEIGHTS['unusual_invoice_amount']
        # check bank accounts: if invoice references payment destination different from trusted (we'll treat this as new_payment_destination)
        # For Slice 2 we don't have invoice bank destination fields; simulate detection placeholder
        # If vendor has bank accounts and newly added account exists that is not verified -> new_bank_account
        accounts = db.query(models.VendorBankAccount).filter(models.VendorBankAccount.vendor_id == vendor.id).all()
        unverified = [a for a in accounts if not a.is_verified]
        if unverified:
            rules.append('new_bank_account')
            evidence['new_bank_accounts_count'] = len(unverified)
            total += RULE_WEIGHTS['new_bank_account']

    # cap score to 100
    score = min(100, total)
    level = determine_risk_level(score)

    return {'score': score, 'level': level, 'rules': rules, 'evidence': evidence}

def save_risk_score(db: Session, organization_id: int, invoice_id: int | None, score_payload: dict, ai_findings: dict | None = None, provider: str | None = None):
    rs = models.RiskScore(organization_id=organization_id, invoice_id=invoice_id, score=score_payload['score'], level=score_payload['level'], rules_triggered=score_payload.get('rules'), evidence=score_payload.get('evidence'), ai_findings=ai_findings, provider=provider)
    db.add(rs)
    db.commit()
    db.refresh(rs)
    return rs

def create_fraud_alert(db: Session, organization_id: int, invoice_id: int | None, alert_type: str, severity: str, risk_score: int, reason: str, evidence: dict | None = None):
    fa = models.FraudAlert(organization_id=organization_id, invoice_id=invoice_id, alert_type=alert_type, severity=severity, risk_score=risk_score, reason=reason, evidence=evidence)
    db.add(fa)
    db.commit()
    db.refresh(fa)
    return fa

# Payment helper
def create_payment(db: Session, organization_id: int, invoice_id: int | None, amount: float, currency: str | None = 'INR'):
    from decimal import Decimal
    from app.core.config import settings
    payment = models.Payment(organization_id=organization_id, invoice_id=invoice_id, amount=Decimal(amount), currency=currency, status='PENDING', held='NO')
    # If invoice is held, hold payment immediately
    if invoice_id:
        inv = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
        if inv and inv.status == 'HELD':
            payment.status = 'HELD'
            payment.held = 'YES'
    # determine approval threshold from org policy if available
    db.add(payment)
    db.commit()
    db.refresh(payment)

    pol = None
    try:
        pol = get_approval_policy(db, organization_id)
    except Exception:
        pol = None

    if pol:
        threshold = float(pol.threshold_amount or 500000.0)
        req_roles = pol.required_roles or ['Finance Manager', 'CFO']
    else:
        try:
            threshold = float(settings.APPROVAL_THRESHOLD)
        except Exception:
            threshold = 500000.0
        req_roles = ['Finance Manager', 'CFO']

    if float(payment.amount) >= threshold:
        apr = models.ApprovalRequest(organization_id=organization_id, payment_id=payment.id, status='PENDING', required_roles=req_roles)
        db.add(apr)
        db.commit()
        db.refresh(apr)
        # create notifications for approvers (by role)
        try:
            create_notification(db, organization_id=organization_id, user_id=None, target_roles=req_roles, notif_type='APPROVAL_REQUEST_CREATED', message=f'Approval required for payment {payment.id}', metadata={'payment_id': payment.id, 'approval_request_id': apr.id})
        except Exception:
            db.rollback()
    return payment

# Audit logs
def create_audit_log(db: Session, organization_id: int, user_id: int, action: str, object_type: str | None, object_id: int | None, previous_state: str | None, new_state: str | None, reason: str | None = None, metadata: dict | None = None):
    al = models.AuditLog(organization_id=organization_id, user_id=user_id, action=action, object_type=object_type, object_id=object_id, previous_state=previous_state, new_state=new_state, reason=reason, metadata=metadata)
    db.add(al)
    db.commit()
    db.refresh(al)
    return al

# Approval helpers

# Notification helpers
def create_notification(db: Session, organization_id: int, user_id: int | None, target_roles: list | None, notif_type: str, message: str, metadata: dict | None = None):
    notif = models.Notification(organization_id=organization_id, user_id=user_id, target_roles=target_roles, notif_type=notif_type, message=message, metadata=metadata)
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def list_notifications_for_user(db: Session, organization_id: int, user_id: int, user_role: str):
    # return notifications that are either directly to the user or target the user's role
    q = db.query(models.Notification).filter(models.Notification.organization_id == organization_id)
    q = q.filter(((models.Notification.user_id == user_id) | (models.Notification.target_roles != None)))
    # We'll filter target_roles in Python since JSON matching across DB varies
    all_notifs = q.order_by(models.Notification.seen.asc(), models.Notification.created_at.desc()).all()
    out = []
    for n in all_notifs:
        if n.user_id == user_id:
            out.append(n)
            continue
        if n.target_roles:
            try:
                if user_role in (n.target_roles or []):
                    out.append(n)
            except Exception:
                pass
    return out


def mark_notification_seen(db: Session, notification_id: int, user_id: int | None = None):
    n = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if not n:
        return None
    n.seen = True
    db.add(n)
    db.commit()
    db.refresh(n)
    return n


def get_approval_request(db: Session, approval_id: int):
    return db.query(models.ApprovalRequest).filter(models.ApprovalRequest.id == approval_id).first()


def get_approval_for_payment(db: Session, payment_id: int):
    return db.query(models.ApprovalRequest).filter(models.ApprovalRequest.payment_id == payment_id).first()


def add_approval_action(db: Session, approval_request_id: int, user_id: int, action: str, comment: str | None = None):
    apr = get_approval_request(db, approval_request_id)
    if not apr:
        return None
    act = models.ApprovalAction(approval_request_id=approval_request_id, user_id=user_id, action=action, comment=comment)
    db.add(act)
    # If action is REJECTED, mark request rejected
    if action == 'REJECTED':
        apr.status = 'REJECTED'
    db.commit()
    db.refresh(act)
    db.refresh(apr)
    # If action is APPROVED check if required roles satisfied
    if action == 'APPROVED':
        # fetch actions and detect if someone from required_roles approved
        acts = db.query(models.ApprovalAction).filter(models.ApprovalAction.approval_request_id == approval_request_id).all()
        approved = False
        for a in acts:
            user = db.query(models.User).filter(models.User.id == a.user_id).first()
            if user and user.role in (apr.required_roles or []):
                approved = True
                break
        if approved:
            apr.status = 'APPROVED'
            db.commit()
            db.refresh(apr)
    return act


def is_approval_satisfied(db: Session, approval_request_id: int) -> bool:
    apr = get_approval_request(db, approval_request_id)
    if not apr:
        return True
    if apr.status == 'APPROVED':
        return True
    return False
