from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlmodel import Session, select
from ..models import Order
from ..schemas import OrderIn, OrderOut
from ..deps import get_db, get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/", response_model=List[OrderOut])
def list_orders(
    status: Optional[str] = None,
    client_id: Optional[int] = None,
    technician_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    _user = Depends(get_current_user),
):
    stmt = select(Order)
    rows = db.exec(stmt).all()
    def ok(o: Order) -> bool:
        if status and o.status != status: return False
        if client_id and o.client_id != client_id: return False
        if technician_id and o.technician_id != technician_id: return False
        return True
    return [o for o in rows if ok(o)][:limit]

@router.post("/", response_model=OrderOut)
def create_order(payload: OrderIn, db: Session = Depends(get_db), _user = Depends(get_current_user)):
    order = Order(**payload.dict())
    db.add(order); db.commit(); db.refresh(order)
    return order

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), _user = Depends(get_current_user)):
    order = db.get(Order, order_id)
    if not order: raise HTTPException(404, "Ordem não encontrada")
    return order

@router.put("/{order_id}", response_model=OrderOut)
def update_order(order_id: int, payload: OrderIn, db: Session = Depends(get_db), _user = Depends(get_current_user)):
    order = db.get(Order, order_id)
    if not order: raise HTTPException(404, "Ordem não encontrada")
    for k, v in payload.dict().items(): setattr(order, k, v)
    db.add(order); db.commit(); db.refresh(order)
    return order

@router.delete("/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db), _user = Depends(get_current_user)):
    order = db.get(Order, order_id)
    if not order: raise HTTPException(404, "Ordem não encontrada")
    db.delete(order); db.commit()
    return {"ok": True}
