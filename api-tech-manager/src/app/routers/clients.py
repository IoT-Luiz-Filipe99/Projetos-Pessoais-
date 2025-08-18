from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlmodel import Session, select
from ..models import Client
from ..schemas import ClientIn, ClientOut
from ..deps import get_db, get_current_user

router = APIRouter(prefix="/clients", tags=["clients"])

@router.get("/", response_model=List[ClientOut])
def list_clients(db: Session = Depends(get_db), _user = Depends(get_current_user)):
    return db.exec(select(Client)).all()

@router.post("/", response_model=ClientOut)
def create_client(payload: ClientIn, db: Session = Depends(get_db), _user = Depends(get_current_user)):
    c = Client(**payload.dict())
    db.add(c); db.commit(); db.refresh(c)
    return c

@router.put("/{client_id}", response_model=ClientOut)
def update_client(client_id: int, payload: ClientIn, db: Session = Depends(get_db), _user = Depends(get_current_user)):
    c = db.get(Client, client_id)
    if not c: raise HTTPException(404, "Cliente não encontrado")
    for k, v in payload.dict().items(): setattr(c, k, v)
    db.add(c); db.commit(); db.refresh(c)
    return c

@router.delete("/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db), _user = Depends(get_current_user)):
    c = db.get(Client, client_id)
    if not c: raise HTTPException(404, "Cliente não encontrado")
    db.delete(c); db.commit()
    return {"ok": True}
