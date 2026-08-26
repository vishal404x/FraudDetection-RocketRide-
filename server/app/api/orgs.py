from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app import crud, models
from app.schemas import OrganizationCreate, OrganizationOut

router = APIRouter(prefix="/api/organizations", tags=["organizations"])

@router.post('/', response_model=dict)
def create_org(payload: OrganizationCreate, db: Session = Depends(get_db)):
    org = crud.create_organization(db, payload.name)
    return {'id': org.id, 'name': org.name, 'created_at': org.created_at.isoformat()}

@router.get('/', response_model=list)
def list_orgs(db: Session = Depends(get_db)):
    orgs = db.query(models.Organization).all()
    return [{'id': o.id, 'name': o.name, 'created_at': o.created_at.isoformat()} for o in orgs]
