"""Provision one explicitly named homologation user interactively.

This script never prints or stores the plaintext password. It is intended to
be run locally by an administrator on the VM, not exposed through the API.
"""
from getpass import getpass
from datetime import datetime, timezone
import sys

from app.db import SessionLocal
from app.models import User, UserCredential
from app.security import hash_password

ALLOWED = {
    "administrador": "Administrador",
    "solicitante": "Gestor solicitante",
    "gerente": "Gerente aprovador",
}

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ALLOWED:
        raise SystemExit("Uso: python scripts/provision_user.py administrador|solicitante|gerente")
    username = f"homolog_{sys.argv[1]}"
    role = ALLOWED[sys.argv[1]]
    password = getpass(f"Senha para {username}: ")
    confirmation = getpass("Confirme a senha: ")
    if not password or password != confirmation:
        raise SystemExit("Senha vazia ou confirmação divergente")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).one_or_none()
        if user is None:
            user = User(username=username, display_name=username.replace("_", " ").title(), role=role, active=True)
            db.add(user); db.flush()
        else:
            user.role = role; user.active = True
        credential = db.get(UserCredential, user.id)
        if credential is None:
            credential = UserCredential(user_id=user.id, password_hash=hash_password(password), changed_at=datetime.now(timezone.utc))
            db.add(credential)
        else:
            credential.password_hash = hash_password(password)
            credential.changed_at = datetime.now(timezone.utc)
        db.commit()
        print(f"Usuário provisionado: {username} ({role})")
    finally:
        db.close()

if __name__ == "__main__":
    main()
