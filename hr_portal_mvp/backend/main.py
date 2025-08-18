
import os
import shutil
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from sqlmodel import SQLModel, Field, create_engine, Session, select
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt

import aiofiles
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm

# ---------------- Config ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
UPLOADS_DIR = os.path.join(PROJECT_ROOT, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

SECRET_KEY = os.environ.get("APP_SECRET_KEY", "CHANGE_ME_SUPER_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 days

DATABASE_URL = "sqlite:///" + os.path.join(BASE_DIR, "app.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------- Models ----------------
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    password_hash: str
    department: str = "Geral"
    is_admin: bool = False


class Announcement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VacationRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    start_date: datetime
    end_date: datetime
    status: str = "Pendente"  # Pendente, Aprovado, Reprovado
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Payslip(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    month: int
    year: int
    file_path: str
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TimeEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    latitude: float
    longitude: float
    photo_path: Optional[str] = None
    entry_type: str = "check_in"  # check_in / check_out


class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    department: str = Field(index=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    username: str
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str


class Quiz(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    course_id: int = Field(index=True, foreign_key="course.id")
    question: str
    options_json: str  # JSON list of strings
    correct_index: int


class Completion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    course_id: int = Field(index=True, foreign_key="course.id")
    score: float
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    certificate_path: Optional[str] = None


# ---------------- Auth schemas ----------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    department: str = "Geral"


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    department: str
    is_admin: bool


class LoginIn(BaseModel):
    email: EmailStr
    password: str


# ---------------- Helpers ----------------
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_session():
    with Session(engine) as session:
        yield session


def get_current_user(token: str = Depends(lambda authorization: authorization),
                     session: Session = Depends(get_session)) -> User:
    # authorization header parser
    # FastAPI injects the full "Authorization" header value in this lambda since there's no standard dependency.
    from fastapi import Request
    # We need to grab header from request (workaround)
    # But FastAPI can't inject Request inside Depends(lambda ...)). Let's implement a proper dependency:
    raise NotImplementedError  # will be replaced below


from fastapi import Request, Header

async def authorization_header(authorization: Optional[str] = Header(default=None)):
    return authorization


def current_user_dependency(authorization: Optional[str] = Depends(authorization_header),
                            session: Session = Depends(get_session)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token ausente")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return user


# WebSocket connection manager per department
class ConnectionManager:
    def __init__(self):
        self.active: Dict[str, List[WebSocket]] = {}

    async def connect(self, department: str, websocket: WebSocket):
        await websocket.accept()
        self.active.setdefault(department, []).append(websocket)

    def disconnect(self, department: str, websocket: WebSocket):
        if department in self.active and websocket in self.active[department]:
            self.active[department].remove(websocket)

    async def broadcast(self, department: str, message: dict):
        for ws in list(self.active.get(department, [])):
            try:
                await ws.send_json(message)
            except Exception:
                # remove broken connections
                self.disconnect(department, ws)


manager = ConnectionManager()


# ---------------- App ----------------
app = FastAPI(title="HR Portal MVP", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
app.mount("/static", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
# Serve uploads (photos, certificates, payslips)
app.mount("/uploads", StaticFiles(directory=os.path.join(PROJECT_ROOT, "uploads")), name="uploads")


@app.get("/", include_in_schema=False)
def root():
    # Redirect to frontend index
    return RedirectResponse(url="/static/index.html")


# ---------------- DB Init & Seed ----------------
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def seed_data():
    with Session(engine) as session:
        # Admin user
        admin = session.exec(select(User).where(User.email == "admin@corp.com")).first()
        if not admin:
            admin = User(
                name="Administrador",
                email="admin@corp.com",
                password_hash=get_password_hash("admin123"),
                department="RH",
                is_admin=True,
            )
            session.add(admin)
        # Announcements
        if session.exec(select(Announcement)).first() is None:
            session.add(Announcement(title="Bem-vindos ao Portal do Colaborador",
                                     content="Acompanhe comunicados internos, solicite férias e muito mais!"))
        # Course + Quiz
        if session.exec(select(Course)).first() is None:
            c = Course(title="Boas Práticas de Segurança da Informação",
                       description="Módulo introdutório com dicas rápidas para o dia a dia.")
            session.add(c)
            session.commit()
            q1 = Quiz(course_id=c.id, question="Qual é a melhor prática para senhas?",
                      options_json=json.dumps(["Usar a mesma senha em todos os sites",
                                               "Anotar num papel e colar no monitor",
                                               "Usar gerenciador de senhas e 2FA"]),
                      correct_index=2)
            q2 = Quiz(course_id=c.id, question="Ao receber um e-mail suspeito, você deve:",
                      options_json=json.dumps(["Clicar no link para verificar",
                                               "Encaminhar ao TI e não clicar em links",
                                               "Responder pedindo mais informações ao remetente"]),
                      correct_index=1)
            session.add(q1)
            session.add(q2)
        session.commit()


@app.on_event("startup")
def on_startup():
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    create_db_and_tables()
    seed_data()


# ---------------- Auth Routes ----------------
@app.post("/auth/register", response_model=UserOut)
def register(user_in: UserCreate, session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.email == user_in.email)).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
    user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        department=user_in.department,
        is_admin=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserOut(id=user.id, name=user.name, email=user.email, department=user.department, is_admin=user.is_admin)


@app.post("/auth/login", response_model=Token)
def login(data: LoginIn, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == data.email)).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="E-mail ou senha inválidos.")
    token = create_access_token({"sub": str(user.id), "name": user.name, "dept": user.department, "adm": user.is_admin})
    return Token(access_token=token)


@app.get("/me", response_model=UserOut)
def me(current_user: User = Depends(current_user_dependency)):
    return UserOut(id=current_user.id, name=current_user.name, email=current_user.email,
                   department=current_user.department, is_admin=current_user.is_admin)


# ---------------- Announcements ----------------
class AnnouncementIn(BaseModel):
    title: str
    content: str


@app.get("/announcements", response_model=List[AnnouncementIn])
def get_announcements(session: Session = Depends(get_session)):
    anns = session.exec(select(Announcement).order_by(Announcement.created_at.desc())).all()
    return [{"title": a.title, "content": a.content} for a in anns]


@app.post("/announcements")
def create_announcement(data: AnnouncementIn, current_user: User = Depends(current_user_dependency),
                        session: Session = Depends(get_session)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Somente admin.")
    a = Announcement(title=data.title, content=data.content)
    session.add(a)
    session.commit()
    return {"ok": True}


# ---------------- Vacation Requests ----------------
class VacationIn(BaseModel):
    start_date: datetime
    end_date: datetime


@app.post("/vacations")
def create_vacation(v: VacationIn, current_user: User = Depends(current_user_dependency),
                    session: Session = Depends(get_session)):
    req = VacationRequest(user_id=current_user.id, start_date=v.start_date, end_date=v.end_date, status="Pendente")
    session.add(req)
    session.commit()
    return {"ok": True}


@app.get("/vacations/my")
def list_my_vacations(current_user: User = Depends(current_user_dependency), session: Session = Depends(get_session)):
    rows = session.exec(select(VacationRequest).where(VacationRequest.user_id == current_user.id)
                        .order_by(VacationRequest.created_at.desc())).all()
    return [{"id": r.id, "start_date": r.start_date, "end_date": r.end_date, "status": r.status} for r in rows]


# ---------------- Payslips (Holerites) ----------------
@app.post("/payslips/upload")
async def upload_payslip(month: int = Form(...), year: int = Form(...),
                         file: UploadFile = File(...),
                         current_user: User = Depends(current_user_dependency),
                         session: Session = Depends(get_session)):
    user_dir = os.path.join(UPLOADS_DIR, f"user_{current_user.id}", "payslips")
    os.makedirs(user_dir, exist_ok=True)
    filename = f"holerite_{year}_{month}_{file.filename}"
    path = os.path.join(user_dir, filename)
    async with aiofiles.open(path, "wb") as f:
        content = await file.read()
        await f.write(content)

    p = Payslip(user_id=current_user.id, month=month, year=year, file_path=path)
    session.add(p)
    session.commit()
    return {"ok": True, "url": f"/uploads/user_{current_user.id}/payslips/{filename}"}


@app.get("/payslips/my")
def my_payslips(current_user: User = Depends(current_user_dependency), session: Session = Depends(get_session)):
    rows = session.exec(select(Payslip).where(Payslip.user_id == current_user.id)
                        .order_by(Payslip.uploaded_at.desc())).all()
    return [{"id": r.id, "month": r.month, "year": r.year,
             "url": f"/uploads/user_{current_user.id}/payslips/{os.path.basename(r.file_path)}"} for r in rows]


# ---------------- Time Clock (Ponto) ----------------
@app.post("/time_entries")
async def create_time_entry(latitude: float = Form(...), longitude: float = Form(...),
                            entry_type: str = Form("check_in"),
                            photo: Optional[UploadFile] = File(None),
                            current_user: User = Depends(current_user_dependency),
                            session: Session = Depends(get_session)):
    photo_path = None
    if photo is not None:
        user_dir = os.path.join(UPLOADS_DIR, f"user_{current_user.id}", "time_photos")
        os.makedirs(user_dir, exist_ok=True)
        filename = f"ponto_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{photo.filename}"
        path = os.path.join(user_dir, filename)
        async with aiofiles.open(path, "wb") as f:
            content = await photo.read()
            await f.write(content)
        photo_path = path

    t = TimeEntry(user_id=current_user.id, latitude=latitude, longitude=longitude,
                  photo_path=photo_path, entry_type=entry_type)
    session.add(t)
    session.commit()
    return {"ok": True, "id": t.id}


@app.get("/time_entries/my")
def my_time_entries(current_user: User = Depends(current_user_dependency), session: Session = Depends(get_session)):
    rows = session.exec(select(TimeEntry).where(TimeEntry.user_id == current_user.id)
                        .order_by(TimeEntry.timestamp.desc())).all()
    return [{"id": r.id, "timestamp": r.timestamp, "lat": r.latitude, "lng": r.longitude,
             "photo_url": (f"/uploads/user_{current_user.id}/time_photos/{os.path.basename(r.photo_path)}"
                           if r.photo_path else None),
             "type": r.entry_type} for r in rows]


# ---------------- Chat (WebSocket por departamento) ----------------
def decode_token(token: str, session: Session) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        user = session.get(User, user_id)
        if not user:
            raise ValueError("Usuário inválido")
        return user
    except Exception as e:
        raise e


@app.websocket("/ws/chat/{department}")
async def websocket_chat(websocket: WebSocket, department: str, token: Optional[str] = None):
    await websocket.accept()
    # Validate token from query params
    query_params = dict(websocket.scope.get("query_string", b"").decode().split("=", 1)) if websocket.scope.get("query_string") else {}
    token_q = None
    if "token" in websocket.query_params:
        token_q = websocket.query_params["token"]
    elif token is not None:
        token_q = token

    with Session(engine) as session_db:
        try:
            user = decode_token(token_q, session_db) if token_q else None
            if not user:
                await websocket.send_json({"system": True, "message": "Token inválido."})
                await websocket.close()
                return
        except Exception:
            await websocket.send_json({"system": True, "message": "Token inválido."})
            await websocket.close()
            return

        await manager.connect(department, websocket)
        try:
            # send backlog (last 20 messages)
            msgs = session_db.exec(select(ChatMessage).where(ChatMessage.department == department)
                                   .order_by(ChatMessage.timestamp.desc()).limit(20)).all()
            for m in reversed(msgs):
                await websocket.send_json({"user": m.username, "content": m.content, "timestamp": m.timestamp.isoformat()})
            # loop
            while True:
                data = await websocket.receive_json()
                text = data.get("content", "").strip()
                if not text:
                    continue
                msg = ChatMessage(department=department, user_id=user.id, username=user.name, content=text)
                session_db.add(msg)
                session_db.commit()
                await manager.broadcast(department, {"user": user.name, "content": text, "timestamp": msg.timestamp.isoformat()})
        except WebSocketDisconnect:
            manager.disconnect(department, websocket)


# ---------------- Training & Certificates ----------------
@app.get("/courses")
def list_courses(session: Session = Depends(get_session)):
    rows = session.exec(select(Course)).all()
    return [{"id": r.id, "title": r.title, "description": r.description} for r in rows]


@app.get("/quizzes/{course_id}")
def get_quiz(course_id: int, session: Session = Depends(get_session)):
    rows = session.exec(select(Quiz).where(Quiz.course_id == course_id)).all()
    return [{"id": q.id, "question": q.question, "options": json.loads(q.options_json)} for q in rows]


class QuizSubmitIn(BaseModel):
    answers: List[int]  # index chosen per question


def generate_certificate_pdf(username: str, course_title: str, outfile: str):
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    c = canvas.Canvas(outfile, pagesize=landscape(A4))
    width, height = landscape(A4)
    # Background
    c.setFillColorRGB(0.93, 0.96, 1.0)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    # Border
    c.setStrokeColor(colors.HexColor("#1E3A8A"))
    c.setLineWidth(6)
    c.rect(1*cm, 1*cm, width-2*cm, height-2*cm, stroke=1, fill=0)
    # Title
    c.setFillColor(colors.HexColor("#1E3A8A"))
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(width/2, height-4*cm, "CERTIFICADO DE CONCLUSÃO")
    # Body
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 20)
    c.drawCentredString(width/2, height-7*cm, f"Certificamos que {username}")
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height-9*cm, f"concluiu o curso \"{course_title}\"")
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height-11*cm, f"Data: {datetime.now().strftime('%d/%m/%Y')}")
    # Footer
    c.setFont("Helvetica-Oblique", 12)
    c.drawString(2*cm, 1.5*cm, "Emitido automaticamente pelo Portal do Colaborador")
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width-2*cm, 1.5*cm, "Futura Tecnologia")
    c.save()


@app.post("/quizzes/{course_id}/submit")
def submit_quiz(course_id: int, data: QuizSubmitIn, current_user: User = Depends(current_user_dependency),
                session: Session = Depends(get_session)):
    qs = session.exec(select(Quiz).where(Quiz.course_id == course_id).order_by(Quiz.id)).all()
    if not qs:
        raise HTTPException(status_code=404, detail="Quiz não encontrado.")
    correct = 0
    for i, q in enumerate(qs):
        ans = data.answers[i] if i < len(data.answers) else None
        if ans is not None and ans == q.correct_index:
            correct += 1
    score = round(100.0 * correct / len(qs), 2)
    cert_path = None
    if score >= 70.0:
        # generate certificate
        user_dir = os.path.join(UPLOADS_DIR, f"user_{current_user.id}", "certificates")
        cert_path = os.path.join(user_dir, f"cert_curso_{course_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        course = session.get(Course, course_id)
        generate_certificate_pdf(current_user.name, course.title, cert_path)

    comp = Completion(user_id=current_user.id, course_id=course_id, score=score,
                      certificate_path=cert_path)
    session.add(comp)
    session.commit()

    return {"score": score, "passed": score >= 70.0,
            "certificate_url": (f"/uploads/user_{current_user.id}/certificates/{os.path.basename(cert_path)}"
                                if cert_path else None)}


# ---------------- Basic Reports ----------------
@app.get("/reports/basic")
def basic_reports(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    vacations_pending = session.exec(select(VacationRequest).where(VacationRequest.status == "Pendente")).all()
    time_entries_count = session.exec(select(TimeEntry)).count()
    messages_count = session.exec(select(ChatMessage)).count()
    return {
        "users": len(users),
        "vacations_pending": len(vacations_pending),
        "time_entries": time_entries_count,
        "chat_messages": messages_count,
    }
