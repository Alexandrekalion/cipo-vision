# CIPO VISION API — desenvolvimento

Backend FastAPI isolado para desenvolvimento. O modo local usa usuários fictícios e token `dev-*`; ele não deve ser usado em produção. PostgreSQL é o destino de desenvolvimento planejado, via `DATABASE_URL`. Não há conexão com Active Directory, NAS, câmeras ou serviços corporativos.

```powershell
cd backend
python -m pip install -e ".[test]"
python -m pytest
uvicorn app.main:app --reload
```

Swagger: `http://127.0.0.1:8000/docs`.

Para PostgreSQL local, use `docker compose up -d postgres` e configure `DATABASE_URL` a partir de `.env.example`. O segredo de exemplo é apenas local e não deve ser reutilizado.
