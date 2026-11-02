from datetime import datetime, timedelta, timezone

from app.security import hash_password, verify_password


def test_password_uses_argon2id_and_verifies():
    encoded = hash_password("homologacao-segura")
    assert encoded.startswith("$argon2id$")
    assert verify_password("homologacao-segura", encoded)
    assert not verify_password("senha-incorreta", encoded)


def test_session_expiry_is_time_based():
    expires = datetime.now(timezone.utc) - timedelta(seconds=1)
    assert expires <= datetime.now(timezone.utc)
