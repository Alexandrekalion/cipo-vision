# Plano de implantação isolada

1. Validar requisitos e contrato HTTPS da API externa.
2. Criar o frontend em `frontend/` e gerar build reproduzível.
3. Testar o build localmente sem acessar produção.
4. Preparar diretório exclusivo na VM 108 e um usuário de serviço sem privilégios excessivos.
5. Publicar somente após definir o mecanismo aprovado de entrega e o proxy autorizado.
6. Manter API e PostgreSQL fora da VM 108.

## Estado da Fase 2.1

O frontend inicial é um protótipo local com dados demonstrativos. Não possui conexão com AD, API, PostgreSQL, câmeras ou armazenamento de gravações. A VM 108 não deve ser usada até uma etapa de implantação aprovada separadamente.

As pendências de boot `scsi0` e remoção da ISO da VM 108 permanecem separadas e não bloqueiam a documentação desta fase.
