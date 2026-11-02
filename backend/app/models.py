from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

def now(): return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(160))
    role: Mapped[str] = mapped_column(String(80))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class UserCredential(Base):
    __tablename__ = "user_credentials"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    password_hash: Mapped[str] = mapped_column(String(300), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class UserSession(Base):
    __tablename__ = "user_sessions"
    id: Mapped[str] = mapped_column(String(96), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    csrf_token: Mapped[str] = mapped_column(String(96), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class UserSignature(Base):
    __tablename__ = "user_signatures"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    signature_data: Mapped[str] = mapped_column(Text, nullable=False)
    signature_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Request(Base):
    __tablename__ = "requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    protocol: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    manager_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(80), default="RASCUNHO")
    employee: Mapped[str] = mapped_column(String(160))
    occurrence_type: Mapped[str] = mapped_column(String(120))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    location: Mapped[str] = mapped_column(String(200))
    camera_area: Mapped[str | None] = mapped_column(String(200), nullable=True)
    reason: Mapped[str] = mapped_column(Text)
    rh_required: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    witness_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    safety_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

class Signature(Base):
    __tablename__ = "signatures"
    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    kind: Mapped[str] = mapped_column(String(80))
    document_version: Mapped[str] = mapped_column(String(40), default="v1")
    confirmed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    purpose: Mapped[str] = mapped_column(String(120), default="solicitacao")
    document_hash: Mapped[str] = mapped_column(String(128), default="")
    confirmed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int | None] = mapped_column(ForeignKey("requests.id"), nullable=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(120))
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class WorkflowEvent(Base):
    __tablename__ = "workflow_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"), nullable=False, index=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(80), nullable=True)
    to_status: Mapped[str] = mapped_column(String(80), nullable=False)
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Extraction(Base):
    __tablename__ = "extractions"
    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"), unique=True, nullable=False)
    operator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    storage_reference: Mapped[str] = mapped_column(String(255), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
