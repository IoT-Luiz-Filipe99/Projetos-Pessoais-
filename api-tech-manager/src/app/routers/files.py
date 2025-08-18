import os, uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlmodel import Session
from ..deps import get_db, get_current_user
from ..models import Order
from ..core.config import settings

router = APIRouter(prefix="/files", tags=["files"])

def _save_local(file: UploadFile) -> str:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1]
    name = f"{uuid.uuid4().hex}{ext or ''}"
    dst = os.path.join(settings.UPLOAD_DIR, name)
    with open(dst, "wb") as f:
        f.write(file.file.read())
    return f"/static/{name}"

def _save_supabase(file: UploadFile) -> str:
    from supabase import create_client
    if not (settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY and settings.SUPABASE_BUCKET):
        raise HTTPException(500, "Supabase não configurado")
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    ext = os.path.splitext(file.filename or "")[1]
    path = f"{uuid.uuid4().hex}{ext or ''}"
    data = file.file.read()
    client.storage.from_(settings.SUPABASE_BUCKET).upload(path, data, {"contentType": file.content_type or "application/octet-stream"})
    public_url = client.storage.from_(settings.SUPABASE_BUCKET).get_public_url(path)
    return public_url

@router.post("/orders/{order_id}/attach")
def attach_file(order_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), _user = Depends(get_current_user)):
    order = db.get(Order, order_id)
    if not order: raise HTTPException(404, "Ordem não encontrada")

    if settings.UPLOAD_BACKEND == "supabase":
        url = _save_supabase(file)
    else:
        url = _save_local(file)

    order.attachment_url = url
    db.add(order); db.commit(); db.refresh(order)
    return {"ok": True, "attachment_url": url}
