from datetime import datetime, timezone
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from sqlalchemy.orm import Session
from .auth import current_user as dev_current_user, require_roles as dev_require_roles
from .security import SESSION_COOKIE, create_session, current_session, current_user, hash_password, require_csrf, require_roles, verify_password
from .db import get_db
from .models import AuditEvent, Request, Signature, User, UserCredential
from .schemas import Decision, DevLogin, LoginPayload, RequestCreate, RequestOut, Token

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
def create_request(payload: RequestCreate, db: Session = Depends(get_db), user: User = Depends(require_roles('Gestor solicitante'))):
    item = Request(protocol=f"CV-DEV-{int(datetime.now().timestamp())}", requester_id=user.id, manager_id=payload.manager_id, status='RASCUNHO', employee=payload.employee, occurrence_type=payload.occurrence_type, occurred_at=payload.occurred_at, location=payload.location, camera_area=payload.camera_area, reason=payload.reason)
    db.add(item); db.flush(); db.add(AuditEvent(request_id=item.id, actor_id=user.id, action='REQUEST_CREATED')); db.commit(); db.refresh(item); return item

@app.get('/requests', response_model=list[RequestOut])
def list_requests(db: Session = Depends(get_db), user: User = Depends(current_user)):
    query=db.query(Request)
    if user.role == 'Gestor solicitante': query=query.filter(Request.requester_id==user.id)
    return query.all()

@app.post('/requests/{request_id}/decision', response_model=RequestOut)
def decide(request_id:int,payload:Decision,db:Session=Depends(get_db),user:User=Depends(require_roles('Gerente aprovador'))):
    item=db.get(Request,request_id)
    if not item or item.manager_id!=user.id: raise HTTPException(404,'Solicitação não encontrada')
    if payload.decision=='APPROVE':
        if not payload.manager_signature or not payload.witness_id or payload.rh_required is None: raise HTTPException(422,'Assinatura, testemunha e decisão de RH são obrigatórias')
        item.status='AGUARDANDO_ASSINATURAS';item.witness_id=payload.witness_id;item.rh_required=payload.rh_required
    elif payload.decision=='REJECT':
        if not payload.reason: raise HTTPException(422,'Justificativa obrigatória para recusa')
        item.status='RECUSADA'
    elif payload.decision=='RETURN': item.status='DEVOLVIDA_PARA_CORRECAO'
    else: raise HTTPException(422,'Decisão inválida')
    db.add(AuditEvent(request_id=item.id,actor_id=user.id,action=f'DECISION_{payload.decision}',detail=payload.reason or ''));db.commit();db.refresh(item);return item

@app.post('/requests/{request_id}/extraction', response_model=RequestOut)
def extraction(request_id:int,db:Session=Depends(get_db),user:User=Depends(require_roles('TI'))):
    item=db.get(Request,request_id)
    if not item or item.status!='PRONTA_PARA_EXTRACAO': raise HTTPException(409,'Extração bloqueada até concluir assinaturas obrigatórias')
    item.status='EM_EXTRACAO';db.add(AuditEvent(request_id=item.id,actor_id=user.id,action='EXTRACTION_STARTED'));db.commit();db.refresh(item);return item
