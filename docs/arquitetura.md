# Arquitetura — CIPO VISION

## Componentes

### Frontend

React + TypeScript + Vite, hospedado exclusivamente na VM 108 (`192.168.0.54`). A VM não conterá banco de dados nem API.

### API

FastAPI em infraestrutura externa e independente. Deve expor somente HTTPS, integrar-se ao Active Directory por mecanismo aprovado e aplicar autorização por perfil e vínculo com a solicitação.

### Banco

PostgreSQL dedicado, externo à VM 108 e isolado de bancos das aplicações existentes.

## Segurança

- Segredos somente em gerenciadores de segredo ou variáveis protegidas do ambiente.
- Nenhuma credencial no Git.
- Logs sem senhas, tokens ou dados sensíveis.
- Auditoria de operações relevantes.
- Validação de autorização em todas as rotas protegidas.
- Registro imutável de decisões, assinaturas, extrações, downloads e alterações de estado.
- Acesso às gravações somente após autorização e dentro do prazo definido.
- Separação entre metadados no PostgreSQL e arquivos de gravação no armazenamento aprovado.

## Modelo de processo

O frontend apresenta o estado atual e as ações permitidas para cada perfil. A API é a autoridade para transições de estado, permissões, assinaturas e auditoria. A TI registra a extração e o destino do arquivo sem expor dispositivos ou credenciais de gravação ao frontend.

## Integrações

- Active Directory: autenticação e grupos corporativos.
- PostgreSQL externo: solicitações, usuários sincronizados, decisões, assinaturas, auditoria e metadados.
- Armazenamento externo/NAS: arquivos extraídos, conforme política aprovada.

Não haverá conexão com câmeras ao vivo nesta fase; qualquer integração com fontes de gravação será tratada posteriormente pela API externa, mediante especificação e autorização.

## Alternativas

React/Vite foi escolhido por simplicidade e ecossistema. Next.js pode ser avaliado se SSR ou roteamento no servidor forem requisitos; não é necessário adotá-lo sem essa demanda.
