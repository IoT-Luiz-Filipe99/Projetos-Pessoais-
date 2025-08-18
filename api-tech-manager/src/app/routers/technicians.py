from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlmodel import Session, select
from ..models import Technician
from ..schemas import TechnicianIn, TechnicianOut
from ..deps import get_db, get_current_user

router = APIRouter(prefix="/technicians", tags=["technicians"])

@router.get("/", response_model=List[TechnicianOut])
def list_techs(
    q: Optional[str] = Query(None, description="Busca por nome/cidade/skills"),
    city: Optional[str] = None,
    state: Optional[str] = None,
    active: Optional[bool] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    _user = Depends(get_current_user),
):
    statement = select(Technician)
    rows = db.exec(statement).all()
    def matches(t: Technician) -> bool:
        if q and (q.lower() not in (t.name or "").lower() and q.lower() not in (t.city or "").lower() and q.lower() not in (t.skills or "").lower()):
            return False
        if city and (t.city or "").lower() != city.lower(): return False
        if state and (t.state or "").upper() != state.upper(): return False
        if active is not None and t.is_active != active: return False
        return True
    return [t for t in rows if matches(t)][:limit]

@router.post("/", response_model=TechnicianOut)
def create_tech(payload: TechnicianIn, db: Session = Depends(get_db), _user = Depends(get_current_user)):
    tech = Technician(**payload.dict())
    db.add(tech); db.commit(); db.refresh(tech)
    return tech

@router.get("/{tech_id}", response_model=TechnicianOut)
def get_tech(tech_id: int, db: Session = Depends(get_db), _user = Depends(get_current_user)):
    tech = db.get(Technician, tech_id)
    if not tech: raise HTTPException(404, "Técnico não encontrado")
    return tech

@router.put("/{tech_id}", response_model=TechnicianOut)
def update_tech(tech_id: int, payload: TechnicianIn, db: Session = Depends(get_db), _user = Depends(get_current_user)):
    tech = db.get(Technician, tech_id)
    if not tech: raise HTTPException(404, "Técnico não encontrado")
    for k, v in payload.dict().items(): setattr(tech, k, v)
    db.add(tech); db.commit(); db.refresh(tech)
    return tech

@router.delete("/{tech_id}")
def delete_tech(tech_id: int, db: Session = Depends(get_db), _user = Depends(get_current_user)):
    tech = db.get(Technician, tech_id)
    if not tech: raise HTTPException(404, "Técnico não encontrado")
    db.delete(tech); db.commit()
    return {"ok": True}
