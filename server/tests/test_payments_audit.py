import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base
import app.models as models
from app import crud

@pytest.fixture()
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_audit_log_created_on_hold_and_release(db_session):
    org = models.Organization(name='Org')
    db_session.add(org)
    db_session.commit()

    user = models.User(email='user@example.com', hashed_password='x', organization_id=org.id)
    db_session.add(user)
    db_session.commit()

    payment = models.Payment(organization_id=org.id, amount=1000, currency='INR', status='PENDING', held='NO')
    db_session.add(payment)
    db_session.commit()

    # simulate hold
    prev = payment.status
    payment.status = 'HELD'
    payment.held = 'YES'
    db_session.add(payment)
    db_session.commit()
    al = crud.create_audit_log(db_session, org.id, user.id, action='PAYMENT_HELD', object_type='payment', object_id=payment.id, previous_state=prev, new_state=payment.status, reason='test hold')
    assert al.action == 'PAYMENT_HELD'
    assert al.object_id == payment.id

    # simulate release
    prev = payment.status
    payment.status = 'RELEASED'
    payment.held = 'NO'
    db_session.add(payment)
    db_session.commit()
    al2 = crud.create_audit_log(db_session, org.id, user.id, action='PAYMENT_RELEASED', object_type='payment', object_id=payment.id, previous_state=prev, new_state=payment.status, reason='test release')
    assert al2.action == 'PAYMENT_RELEASED'
    assert al2.object_id == payment.id
