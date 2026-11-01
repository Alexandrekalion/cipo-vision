# Requisitos — CIPO VISION

## Status

Especificação funcional para aprovação. A implementação não deve começar antes da validação do proprietário do processo.

## Escopo

O CIPO VISION gerencia solicitações corporativas de extração e arquivamento de gravações após ocorrências. Não monitora câmeras ao vivo.

## Fluxo principal

1. O encarregado registra colaborador, data, horário, local/câmera e motivo.
2. Giuliano analisa a solicitação e aprova ou recusa.
3. Testemunhas e RH participam da formalização e das assinaturas exigidas.
4. TI extrai as imagens autorizadas, registra o armazenamento e finaliza o atendimento.
5. O solicitante acompanha o status e o histórico completo.

## Estados da solicitação

`RASCUNHO` → `ENVIADA` → `EM_ANALISE` → `APROVADA` ou `RECUSADA`.

Após aprovação: `AGUARDANDO_FORMALIZACAO` → `AGUARDANDO_ASSINATURAS` → `PRONTA_PARA_EXTRACAO` → `EM_EXTRACAO` → `ARQUIVADA` → `FINALIZADA`.

Estados auxiliares: `DEVOLVIDA_PARA_CORRECAO`, `CANCELADA` e `ERRO_DE_EXTRACAO`. Toda transição deve registrar usuário, data, motivo e evidências aplicáveis.

## Matriz inicial de permissões

| Perfil | Permissões principais |
| --- | --- |
| Solicitante/Encarregado | Criar, enviar, acompanhar e consultar suas solicitações |
| Giuliano/Aprovador | Analisar, solicitar correção, aprovar ou recusar |
| Testemunha | Consultar formalização e assinar quando designada |
| RH | Validar participação, assinar e consultar solicitações autorizadas |
| TI | Administrar solicitações, executar extração, registrar armazenamento e finalizar |
| Administrador | Administrar perfis, parâmetros, integrações, auditoria e suporte |
| Auditor | Consultar histórico e evidências sem alterar o processo |

## Telas necessárias

- Login integrado ao Active Directory.
- Painel inicial conforme o perfil.
- Nova solicitação e validação dos dados.
- Lista, filtros e detalhe da solicitação.
- Caixa de análise e decisão de Giuliano.
- Formalização, testemunhas e assinaturas.
- Fila de extração da TI e registro do armazenamento.
- Consulta de gravações autorizadas e metadados.
- Histórico, trilha de auditoria e relatórios.
- Administração de usuários, perfis e parâmetros.

## Requisitos não funcionais

- Interface responsiva e profissional.
- Autenticação individual via Active Directory.
- Autorização por perfil e por vínculo com a solicitação.
- Auditoria de acessos, decisões, assinaturas, extrações e downloads.
- HTTPS entre frontend e API.
- Segredos fora do Git e arquivos `.env` reais fora do repositório.
- Retenção e acesso às gravações definidos por política corporativa.

## Pontos para aprovação

- Quais assinaturas são obrigatórias em cada tipo de ocorrência.
- Prazo de retenção e destino final das gravações.
- Regras para download, expiração e revogação de acesso.
- Dados e grupos do Active Directory autorizados.
- Responsáveis substitutos quando Giuliano, RH ou TI estiverem indisponíveis.
