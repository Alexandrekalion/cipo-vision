# Arquitetura — CIPO VISION

## Componentes

### Frontend

React + TypeScript + Vite, hospedado exclusivamente na VM 108. A VM não deverá conter banco de dados nem API.

### API

FastAPI em infraestrutura externa e independente. Deve expor somente HTTPS, autenticar usuários individualmente e aplicar autorização por perfil.

### Banco

PostgreSQL dedicado, externo à VM 108 e isolado de bancos das aplicações existentes.

## Segurança

- Segredos somente em gerenciadores de segredo ou variáveis protegidas do ambiente.
- Nenhuma credencial no Git.
- Logs sem senhas, tokens ou dados sensíveis.
- Auditoria de operações relevantes.
- Validação de autorização em todas as rotas protegidas.

## Alternativas

React/Vite foi escolhido por simplicidade e ecossistema. Next.js pode ser avaliado se SSR ou roteamento no servidor forem requisitos; não é necessário adotá-lo sem essa demanda.
