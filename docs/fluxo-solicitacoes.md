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
