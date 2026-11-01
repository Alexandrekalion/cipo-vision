# Fluxo de solicitações — Fase 2.1

```text
RASCUNHO -> ENVIADA -> EM_ANALISE
                         |-> DEVOLVIDA_PARA_CORRECAO -> ENVIADA
                         |-> RECUSADA
                         `-> APROVADA -> AGUARDANDO_FORMALIZACAO
                                      -> AGUARDANDO_ASSINATURAS
                                      -> PRONTA_PARA_EXTRACAO
                                      -> EM_EXTRACAO
                                      -> ARQUIVADA -> FINALIZADA
```

`CANCELADA` e `ERRO_DE_EXTRACAO` são estados auxiliares. Cada transição deve ser autorizada pela API e gerar evento de auditoria.
# Regra operacional vigente — aprovação e testemunha

Na aprovação gerencial, o gerente selecionado indica a testemunha entre os usuários autorizados, assina a decisão e informa se RH participa. A solicitação segue para testemunha e Segurança do Trabalho; RH participa quando indicado. A TI só recebe itens com todas as assinaturas obrigatórias confirmadas. A testemunha não é presumida nem escolhida automaticamente.
