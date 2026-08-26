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


def test_default_policy_created_on_org_creation(db_session):
    org = crud.create_organization(db_session, 'OrgX')
    pol = crud.get_approval_policy(db_session, org.id)
    assert pol is not None
    assert pol.threshold_amount == 500000.0
    assert isinstance(pol.required_roles, list)


def test_update_policy(db_session):
    org = crud.create_organization(db_session, 'OrgY')
    pol = crud.update_approval_policy(db_session, org.id, threshold_amount=250000.0, required_roles=['Finance Manager'])
    assert pol.threshold_amount == 250000.0
    assert pol.required_roles == ['Finance Manager']
