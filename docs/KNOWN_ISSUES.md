# Pendências conhecidas

Identificadas na revisão de 25/10/2026. Não corrigidas nesta etapa de organização; fonte e executáveis mantidos.

| Prioridade | Achado e evidência | Próxima ação |
| --- | --- | --- |
| Alta | `rename_operations`: erro após mover parte das fontes deixa nomes `.__renamer_tmp_*`; não há rollback e esses arquivos são ocultados da lista. Reproduzido com falha simulada na segunda fonte em diretório temporário. | Planejar transação recuperável, rollback e testes de falha em ambas as fases. |
| Alta | `_replace_preview_name` aplica substituição sobre o nome completo. `jpg` → `png` transforma `Foto_001.jpg` em `Foto_001.png`, sem converter conteúdo. Reproduzido sem GUI. | Separar stem e extensão e testar os dois fluxos de substituição. |
| Alta | `undo_last_rename` restaura sequencialmente, rejeitando nomes originais que ainda são destino de outro item do lote. Trocas/ciclos não podem ser desfeitos; falha intermediária pode deixar estado parcial. Evidência por leitura do fluxo. | Usar operação reversa com duas fases e recuperação. |
| Alta | Substituição direta não valida destinos duplicados globalmente; dois nomes podem convergir ao remover texto. Validação é por arquivo existente. | Centralizar validação do lote e comparação sem distinção de caixa Windows. |
| Média | `make_new_name` aceita base/separador/substituição sem validar nomes Windows reservados, caracteres inválidos e caminhos; números digitados nos Spinboxes podem lançar TclError/ValueError durante callbacks. | Validar entradas e mostrar erros antes de formar operações. |
| Média | `completed` só recebe o progresso após sucesso completo; em falha na segunda fase a mensagem pode dizer zero mesmo com itens processados. | Registrar progresso e estado real também na falha. |
| Média | Prévia/substituição direta usam bases diferentes: prévia gera nome por padrão, botão de substituição atua no stem original. | Especificar comportamento e alinhar rótulos/prévia. |
| Média | Build herdada não possui manifesto de fonte/dependências/ambiente. Binários ativos idênticos não provam que correspondem à fonte atual. | Registrar proveniência em próxima build Windows; fixar dependências após validação. |
| Média | Monitoramento varre árvore na thread da GUI; `_file_is_stable` recalcula chaves de todos os listados para cada arquivo. Prévia e numeração usam buscas repetidas. | Medir em acervos grandes antes de modularizar/otimizar. |
| Baixa | README/PROJECT_CONTEXT e guias legados divergem da implementação (numeração selecionada, botões, tema e recursos novos). Specs duplicados equivalentes. | Usar docs atuais; consolidar legados/specs em etapa acompanhada de build. |

Antes de corrigir o aplicativo: seguir o ciclo obrigatório de backup, testes e distribuição de `development.md`. A ordenação por data de criação usa st_ctime, cuja semântica depende do sistema; o alvo continua Windows.
