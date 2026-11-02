from datetime import datetime, timezone
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .auth import current_user as dev_current_user, require_roles as dev_require_roles
from .security import SESSION_COOKIE, create_session, current_session, current_user, hash_password, require_csrf, require_roles, verify_password
from .db import get_db
from .models import AuditEvent, Extraction, Request, Signature, User, UserCredential, WorkflowEvent
from .schemas import Decision, DevLogin, ExtractionCreate, LoginPayload, RequestCreate, RequestOut, SignatureCreate, SignatureOut, Token

app = FastAPI(title="CIPO VISION API", version="0.1.0", description="API de desenvolvimento isolada; sem AD, NAS ou câmeras reais.")

@app.post('/auth/login', response_model=Token)
def login(payload: LoginPayload, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username, User.active.is_(True)).first()
    credential = db.get(UserCredential, user.id) if user else None
    if not user or not credential or not verify_password(payload.password, credential.password_hash):
        raise HTTPException(401, 'Credenciais inválidas')
    session = create_session(response, user, db)
    return Token(access_token=session.csrf_token)

@app.post('/auth/logout')
def logout(response: Response, session_data=Depends(current_session), csrf=Depends(require_csrf), db: Session = Depends(get_db)):
    session_data[1].revoked_at = datetime.now(timezone.utc); db.commit(); response.delete_cookie(SESSION_COOKIE)
    return {'ok': True}

@app.get('/auth/me')
def me(user: User = Depends(current_user)):
    return {'id': user.id, 'username': user.username, 'display_name': user.display_name, 'role': user.role}

@app.post('/auth/dev-login', response_model=Token)
def dev_login(payload: DevLogin, db: Session = Depends(get_db)):
    from .config import settings
    if not settings.dev_auth_enabled: raise HTTPException(404, 'Not found')
    user = db.query(User).filter(User.username == payload.username, User.active.is_(True)).first()
    if not user: raise HTTPException(401, "Usuário de desenvolvimento não encontrado")
    return Token(access_token=f"dev-{user.username}")

@app.post('/requests', response_model=RequestOut)
def create_request(payload: RequestCreate, db: Session = Depends(get_db), user: User = Depends(require_roles('Gestor solicitante')), csrf=Depends(require_csrf)):
    item = Request(protocol=f"CV-DEV-{int(datetime.now().timestamp())}", requester_id=user.id, manager_id=payload.manager_id, status='RASCUNHO', employee=payload.employee, occurrence_type=payload.occurrence_type, occurred_at=payload.occurred_at, location=payload.location, camera_area=payload.camera_area, reason=payload.reason)
    db.add(item); db.flush(); db.add(AuditEvent(request_id=item.id, actor_id=user.id, action='REQUEST_CREATED')); db.add(WorkflowEvent(request_id=item.id, actor_id=user.id, to_status='RASCUNHO')); db.commit(); db.refresh(item); return item

@app.get('/requests', response_model=list[RequestOut])
def list_requests(db: Session = Depends(get_db), user: User = Depends(current_user)):
    query=db.query(Request)
    if user.role == 'Gestor solicitante': query=query.filter(Request.requester_id==user.id)
    return query.all()

@app.post('/requests/{request_id}/decision', response_model=RequestOut)
def decide(request_id:int,payload:Decision,db:Session=Depends(get_db),user:User=Depends(require_roles('Gerente aprovador')), csrf=Depends(require_csrf)):
    item=db.query(Request).with_for_update().filter(Request.id == request_id).first()
    if not item or item.manager_id!=user.id: raise HTTPException(404,'Solicitação não encontrada')
    if item.status != 'RASCUNHO': raise HTTPException(409, 'Decisão gerencial já realizada ou solicitação fora da etapa')
    if payload.decision=='APPROVE':
        if not payload.manager_signature or not payload.witness_id or payload.rh_required is None: raise HTTPException(422,'Assinatura, testemunha e decisão de RH são obrigatórias')
        witness = db.get(User, payload.witness_id)
        if not witness or witness.role != 'Testemunha': raise HTTPException(422, 'Testemunha inválida')
        item.status='AGUARDANDO_ASSINATURAS';item.witness_id=payload.witness_id;item.rh_required=payload.rh_required; item.safety_required=True
        db.add(Signature(request_id=item.id,user_id=user.id,kind='GERENTE',purpose='aprovacao',document_hash=f'request-{item.id}',confirmed=True))
    elif payload.decision=='REJECT':
        if not payload.reason: raise HTTPException(422,'Justificativa obrigatória para recusa')
        item.status='RECUSADA'
    elif payload.decision=='RETURN': item.status='DEVOLVIDA_PARA_CORRECAO'
    else: raise HTTPException(422,'Decisão inválida')
    db.add(AuditEvent(request_id=item.id,actor_id=user.id,action=f'DECISION_{payload.decision}',detail=payload.reason or '')); db.add(WorkflowEvent(request_id=item.id, actor_id=user.id, from_status='RASCUNHO', to_status=item.status, detail=payload.reason or '')); db.commit();db.refresh(item);return item

@app.post('/requests/{request_id}/sign', response_model=SignatureOut)
def sign_request(request_id: int, payload: SignatureCreate, db: Session = Depends(get_db), user: User = Depends(current_user), csrf=Depends(require_csrf)):
    item = db.get(Request, request_id)
    if not item or not payload.confirmed or not payload.document_hash: raise HTTPException(422, 'Confirmação e integridade do documento são obrigatórias')
    if item.status not in ('RASCUNHO', 'AGUARDANDO_ASSINATURAS'):
        raise HTTPException(409, 'Solicitação fora da etapa de assinatura')
    allowed = {'SOLICITANTE': ('Gestor solicitante', item.requester_id), 'TESTEMUNHA': ('Testemunha', item.witness_id), 'SEGURANCA': ('Segurança do Trabalho', None), 'RH': ('RH', None)}
    rule = allowed.get(payload.purpose)
    if not rule or user.role != rule[0] or (rule[1] is not None and user.id != rule[1]): raise HTTPException(403, 'Usuário não autorizado para esta assinatura')
    if payload.purpose == 'RH' and not item.rh_required:
        raise HTTPException(409, 'RH não foi exigido pelo gerente')
    if payload.purpose == 'GERENTE':
        raise HTTPException(403, 'A assinatura gerencial ocorre durante a aprovação')
    existing = db.query(Signature).filter_by(request_id=request_id, user_id=user.id, purpose=payload.purpose).first()
    if existing: raise HTTPException(409, 'Assinatura já confirmada')
    sig = Signature(request_id=request_id,user_id=user.id,kind=payload.purpose,purpose=payload.purpose,document_hash=payload.document_hash,confirmed=True)
    db.add(sig); db.add(AuditEvent(request_id=request_id,actor_id=user.id,action='SIGNATURE_CONFIRMED',detail=payload.purpose)); db.flush()
    required = ['SOLICITANTE', 'GERENTE', 'TESTEMUNHA', 'SEGURANCA'] + (['RH'] if item.rh_required else [])
    kinds = {s.kind for s in db.query(Signature).filter_by(request_id=request_id).all()}
    if set(required) <= kinds: item.status = 'PRONTA_PARA_EXTRACAO'
    db.commit(); db.refresh(sig); return sig

@app.get('/requests/{request_id}/history')
def history(request_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.get(Request, request_id)
    if not item or (user.role == 'Gestor solicitante' and item.requester_id != user.id): raise HTTPException(404, 'Solicitação não encontrada')
    return db.query(AuditEvent).filter_by(request_id=request_id).order_by(AuditEvent.created_at).all()

def _video_access(item: Request, user: User) -> bool:
    return user.role == 'TI' or (user.role == 'Gerente aprovador' and item.manager_id == user.id)

@app.get('/requests/{request_id}/video')
def view_video(request_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.get(Request, request_id)
    if not item:
        raise HTTPException(404, 'Solicitação não encontrada')
    if not _video_access(item, user):
        db.add(AuditEvent(request_id=request_id, actor_id=user.id, action='VIDEO_VIEW_DENIED'))
        db.commit()
        raise HTTPException(403, 'Perfil sem permissão para visualizar vídeo')
    db.add(AuditEvent(request_id=request_id, actor_id=user.id, action='VIDEO_VIEW_ALLOWED'))
    db.commit()
    extraction = db.query(Extraction).filter_by(request_id=request_id).first()
    return {'request_id': request_id, 'available': bool(extraction), 'storage_reference': extraction.storage_reference if extraction else None}

@app.get('/requests/{request_id}/video/download')
def download_video(request_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.get(Request, request_id)
    if not item:
        raise HTTPException(404, 'Solicitação não encontrada')
    if user.role != 'TI':
        db.add(AuditEvent(request_id=request_id, actor_id=user.id, action='VIDEO_DOWNLOAD_DENIED'))
        db.commit()
        raise HTTPException(403, 'Somente TI pode baixar vídeos')
    db.add(AuditEvent(request_id=request_id, actor_id=user.id, action='VIDEO_DOWNLOAD_ALLOWED'))
    db.commit()
    extraction = db.query(Extraction).filter_by(request_id=request_id).first()
    if not extraction:
        raise HTTPException(404, 'Vídeo ainda não registrado')
    return {'request_id': request_id, 'download_allowed': True, 'storage_reference': extraction.storage_reference}

@app.post('/requests/{request_id}/extraction/start', response_model=RequestOut)
def start_extraction(request_id: int, payload: ExtractionCreate, db: Session = Depends(get_db), user: User = Depends(require_roles('TI')), csrf=Depends(require_csrf)):
    item = db.query(Request).with_for_update().filter(Request.id == request_id).first()
    if not item or item.status != 'PRONTA_PARA_EXTRACAO': raise HTTPException(409, 'Extração bloqueada até concluir assinaturas obrigatórias')
    item.status='EM_EXTRACAO'; db.add(Extraction(request_id=request_id,operator_id=user.id,storage_reference=payload.storage_reference)); db.add(AuditEvent(request_id=request_id,actor_id=user.id,action='EXTRACTION_STARTED'))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Extração já iniciada')
    db.refresh(item); return item

@app.post('/requests/{request_id}/extraction/finish', response_model=RequestOut)
def finish_extraction(request_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles('TI')), csrf=Depends(require_csrf)):
    item=db.get(Request,request_id); extraction=db.query(Extraction).filter_by(request_id=request_id).first()
    if not item or not extraction or item.status != 'EM_EXTRACAO': raise HTTPException(409, 'Extração não está em andamento')
    item.status='FINALIZADA'; extraction.finished_at=datetime.now(timezone.utc); db.add(AuditEvent(request_id=request_id,actor_id=user.id,action='EXTRACTION_FINISHED')); db.commit(); db.refresh(item); return item

@app.post('/requests/{request_id}/extraction', response_model=RequestOut)
def extraction(request_id:int,db:Session=Depends(get_db),user:User=Depends(require_roles('TI')), csrf=Depends(require_csrf)):
    item=db.get(Request,request_id)
    if not item or item.status!='PRONTA_PARA_EXTRACAO': raise HTTPException(409,'Extração bloqueada até concluir assinaturas obrigatórias')
    item.status='EM_EXTRACAO';db.add(AuditEvent(request_id=item.id,actor_id=user.id,action='EXTRACTION_STARTED'));db.commit();db.refresh(item);return item
