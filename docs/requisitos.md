# Requisitos — CIPO VISION

## Status

Documento inicial para validação. Nenhuma funcionalidade de negócio foi considerada aprovada ainda.

## Premissas confirmadas

- Frontend na VM 108 (`192.168.0.54`).
- API em infraestrutura externa.
- PostgreSQL dedicado e externo.
- Comunicação frontend/API por HTTPS.
- Isolamento completo das aplicações de produção existentes.

## Pontos a validar

- Perfis de usuário e permissões.
- Fluxos de autenticação e recuperação de acesso.
- Módulos e telas do produto.
- Dados recebidos da API.
- Política de retenção de vídeos temporários.
- Auditoria de operações e eventos.
- Endpoints, contratos e códigos de erro da API.
- Requisitos de armazenamento e integração futura com NAS.

## Critério de implementação

Não iniciar telas definitivas nem contratos de API até que os itens acima sejam revisados e aprovados.
