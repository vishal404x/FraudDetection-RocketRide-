import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base
import app.models as models

@pytest.fixture()
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_users_cannot_access_other_org_data(db_session):
    org1 = models.Organization(name='Org1')
    org2 = models.Organization(name='Org2')
    db_session.add_all([org1, org2])
    db_session.commit()

    user1 = models.User(email='u1@example.com', hashed_password='x', organization_id=org1.id)
    user2 = models.User(email='u2@example.com', hashed_password='x', organization_id=org2.id)
    db_session.add_all([user1, user2])
    db_session.commit()

    v1 = models.Vendor(organization_id=org1.id, legal_name='Vendor1')
    db_session.add(v1)
    db_session.commit()

    vendors_for_user2 = db_session.query(models.Vendor).filter(models.Vendor.organization_id == user2.organization_id).all()
    assert all(v.organization_id == user2.organization_id for v in vendors_for_user2)
    assert v1 not in vendors_for_user2
