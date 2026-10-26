# Limites conhecidos

## Renomeação e recuperação

- O lote não é uma transação atômica do sistema de arquivos. Queda de energia, remoção externa, disco indisponível ou bloqueios podem interromper a operação e a tentativa de restauração.
- **Desfazer** existe apenas na sessão atual e restaura nomes, sem reverter alterações no conteúdo. Evite outros programas modificando os mesmos arquivos durante o lote.
- A recuperação assistida exige um mapa versão 2 e os arquivos nos caminhos registrados. Mapas versão 1, arquivos ausentes ou metadados alterados podem exigir recuperação manual. Não há retomada automática ao reiniciar.
- Se a recuperação também for interrompida e gerar um novo mapa, resolva esse mapa antes de voltar ao inicial. Um mapa residual pode permanecer se sua remoção falhar; confira os nomes e as identidades antes de restaurar. Não execute mapas como código.
- Os testes simulam encerramento abrupto de processo, incluindo ciclos de nomes. Não simulam corte de energia ou garantem persistência física do sistema de arquivos.

Veja o procedimento no [manual de uso](user-guide.md).

## Desempenho e monitoramento

- A varredura automática usa uma thread, mas carregamento manual, metadados, tabela e renomeação ainda podem pausar a interface em lotes grandes.
- No benchmark local com 10.000 arquivos fictícios, carregar a lista levou 5,66 s e renomear levou 12,32 s. Volumes de rede, milhões de itens e arquivos grandes não foram medidos. Consulte a [metodologia e os resultados](development.md#benchmark-e-validações-de-uso--26102026).
- Tamanho estável em duas observações não garante que uma cópia ou download terminou.

## Compatibilidade e interface

- Links simbólicos são recusados. As regressões passaram no Linux; no ambiente Windows de validação, foram puladas por falta de privilégio para criar links.
- O campo de criação usa a semântica Windows de `st_ctime`. O comprimento máximo do caminho completo depende das políticas do Windows e do sistema de arquivos.
- Os testes Windows cobrem widgets reais, listas Tcl de drop e escalas Tk de 100%, 150% e 200%. Gesto físico no Explorer, troca real entre monitores/DPI, telas pequenas e interferência de antivírus ainda precisam de validação manual.
- O executável de distribuição local ainda não foi publicado em Releases nem assinado digitalmente.
