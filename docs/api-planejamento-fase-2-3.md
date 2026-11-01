# Contratos planejados — Fase 2.3

Documento de planejamento. Nenhum contrato está conectado a serviços reais nesta fase.

## Aprovação gerencial

`POST /solicitacoes/{id}/decisao`

Payload planejado: `decision`, `manager_signature`, `witness_user_id`, `rh_required`, `reason`.

Regras: somente o gerente autorizado vinculado à solicitação decide; a aprovação exige assinatura do gerente, testemunha autorizada e decisão explícita sobre RH. A testemunha é indicada exclusivamente pelo gerente.

## Formalização

`POST /solicitacoes/{id}/assinaturas`

Registra participante, tipo, versão do documento, confirmação, data e evidência. A testemunha e Segurança do Trabalho são obrigatórias em toda solicitação aprovada; RH é obrigatório quando `rh_required=true`.

## Extração

`POST /solicitacoes/{id}/extracao`

Permitido apenas quando todas as assinaturas obrigatórias estiverem confirmadas. Registra resultado, referência do arquivo, armazenamento autorizado, responsável, data e falhas.

## Auditoria

Toda indicação ou substituição de testemunha registra autor, identidade anterior/nova, motivo, data e vínculo com a solicitação. A API deve bloquear transições inválidas e downloads não autorizados.
