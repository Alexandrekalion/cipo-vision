# Preparação para Active Directory

O CIPO VISION mantém autenticação e autorização separadas. Nesta fase, a
autenticação de homologação continua local e nenhuma consulta ao domínio é
realizada.

O mapeamento preparado em `backend/app/ad_roles.py` associa grupos autorizados
aos perfis internos:

- `GG_CIPOVISION_GESTOR` → Gestor solicitante
- `GG_CIPOVISION_GERENTE` → Gerente aprovador
- `GG_CIPOVISION_SEGTRAB` → Segurança do Trabalho
- `GG_CIPOVISION_RH` → RH
- `GG_CIPOVISION_TI` → TI

Uma futura integração deverá usar LDAPS ou o mecanismo corporativo aprovado,
identificar o usuário por um subject ID estável, consultar os grupos e
recalcular os perfis a cada autenticação. Senhas do AD nunca serão armazenadas
no banco da aplicação. Usuários sem grupo autorizado não devem receber acesso.
