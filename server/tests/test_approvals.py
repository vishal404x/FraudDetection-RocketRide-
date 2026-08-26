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


def test_payment_creation_creates_approval_and_approval_flow(db_session):
    # create org and users
    org = models.Organization(name='Org')
    db_session.add(org)
    db_session.commit()

    user_creator = models.User(email='creator@example.com', hashed_password='x', organization_id=org.id, role='AP Specialist')
    approver = models.User(email='approver@example.com', hashed_password='x', organization_id=org.id, role='CFO')
    db_session.add_all([user_creator, approver])
    db_session.commit()

    # create a payment above the approval threshold (use 600000)
    payment = crud.create_payment(db_session, org.id, None, 600000, 'INR')
    assert payment is not None

    # approval request should be created
    apr = crud.get_approval_for_payment(db_session, payment.id)
    assert apr is not None
    assert apr.status == 'PENDING'

    # approver approves
    act = crud.add_approval_action(db_session, apr.id, approver.id, 'APPROVED', 'looks good')
    assert act is not None

    # approval should be satisfied
    assert crud.is_approval_satisfied(db_session, apr.id)
    apr_refreshed = crud.get_approval_request(db_session, apr.id)
    assert apr_refreshed.status == 'APPROVED'
