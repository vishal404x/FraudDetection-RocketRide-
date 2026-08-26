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


def test_notification_created_on_approval_request(db_session):
    org = crud.create_organization(db_session, 'OrgNotifs')
    # create users
    approver = models.User(email='approver@org.com', hashed_password='x', organization_id=org.id, role='Finance Manager')
    db_session.add(approver)
    db_session.commit()

    # create a payment above threshold to trigger approval and notification
    payment = crud.create_payment(db_session, org.id, None, 600000, 'INR')
    # find approval
    apr = crud.get_approval_for_payment(db_session, payment.id)
    assert apr is not None

    # list notifications for approver
    notifs = crud.list_notifications_for_user(db_session, org.id, approver.id, approver.role)
    assert any(n.notif_type == 'APPROVAL_REQUEST_CREATED' for n in notifs)


def test_mark_notification_seen(db_session):
    org = crud.create_organization(db_session, 'Org2')
    notif = crud.create_notification(db_session, organization_id=org.id, user_id=None, target_roles=['Owner'], notif_type='TEST', message='hello')
    assert notif.seen == False
    n2 = crud.mark_notification_seen(db_session, notif.id, None)
    assert n2.seen == True
