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

## Decisões aprovadas — Fase 2.1

- Assinaturas configuráveis por tipo de ocorrência e etapa; não presumir RH ou testemunhas em todos os casos.
- Retenção configurável por categoria, sujeita à política corporativa, preservação legal e bloqueio de descarte. Nenhuma exclusão automática nesta fase.
- Downloads somente para TI com permissão específica; API deve autorizar e auditar sucessos e negativas.
- Active Directory somente para autenticação futura; perfis e permissões permanecem internos ao CIPO VISION. Senhas do AD não serão armazenadas.
- Substitutos com titular, período, permissões delegadas e autorizador; substituto não pode autoelevar privilégios e todas as ações serão auditadas.

## Pontos ainda pendentes

## Decisão oficial — testemunha obrigatória (Fase 2.3)

- O gerente aprovador é o único responsável por indicar a testemunha, escolhida entre usuários autorizados.
- Toda aprovação exige assinatura do gerente, indicação da testemunha e decisão explícita sobre o RH.
- Toda solicitação aprovada exige assinatura da testemunha e da Segurança do Trabalho; RH assina quando indicado pelo gerente.
- A API deve bloquear a fila de extração enquanto houver assinatura obrigatória pendente.
- Indicações, substituições e confirmações de assinatura devem ser auditadas com autor, data, motivo e versão do documento.

- Quais assinaturas são obrigatórias em cada tipo de ocorrência.
- Prazo de retenção e destino final das gravações.
- Regras para download, expiração e revogação de acesso.
- Dados e grupos do Active Directory autorizados.
- Responsáveis substitutos quando Giuliano, RH ou TI estiverem indisponíveis.
