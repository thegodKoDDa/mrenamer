# Pendências conhecidas

## Corrigido em 25/10/2026

- Renomeação em duas fases agora tenta restaurar todas as origens ao falhar. Erros informam progresso real e se a restauração foi completa. Um mapa JSON persistido antes dos movimentos permite localizar origens, temporários e destinos caso a recuperação fique incompleta.
- Desfazer usa o mesmo motor transacional, incluindo trocas e ciclos de nomes.
- Substituição preserva a extensão e valida o lote inteiro, incluindo colisões sem distinção de caixa, arquivos existentes e nomes Windows inválidos.
- Prévia possui modos explícitos Padrão/Substituição; cada botão mostra a prévia correspondente antes da confirmação. Campos de substituição não modificam silenciosamente o padrão.
- Campos numéricos inválidos mostram erro na tela e impedem a operação, sem quebrar callbacks.
- Nenhuma operação substitui destinos criados por outro processo entre validação e movimento.
- Monitoramento varre diretórios em uma thread sem chamadas Tk. Resultados de um contexto antigo são descartados; assinaturas anteriores detectam alterações de tamanho/data. Removidas buscas repetidas de seleção e chaves na prévia/estabilidade.
- Dependências da build foram fixadas nas versões já instaladas e verificadas. Build temporária, backups individuais, teste do executável e manifesto de fonte/ambiente/hash fazem parte da entrega.
- Spec alternativo delega ao canônico; documentação e guias ativos atualizados. Originais históricos continuam preservados.

## Limites atuais

- O lote não é uma transação atômica do filesystem. Queda de energia, remoção externa, disco indisponível ou bloqueio também durante rollback podem exigir recuperação manual pelo `.__renamer_recovery_*.json`. Não há retomada automática após reiniciar.
- Desfazer fica em memória e se perde ao fechar. Alterações externas no conteúdo não são revertidas. Não executar outro programa alterando os mesmos arquivos simultaneamente.
- Um mapa residual pode permanecer se sua remoção falhar depois de sucesso/rollback; conferir os arquivos e as identidades registradas antes de recuperar manualmente. Não executar o mapa como código.
- Varredura automática foi retirada da thread da GUI; abertura manual de pasta, estatísticas e renderização da tabela ainda podem demorar em grandes acervos ou volumes de rede. Não houve benchmark representativo desses cenários.
- Estabilidade de tamanho em duas observações não garante que uma cópia terminou.
- st_ctime segue a semântica Windows para o campo de criação. Comprimento do caminho completo também depende das políticas Windows/filesystem; nomes individuais são validados.
- Symlinks são recusados. A regressão de symlinks passou no Linux e foi pulada no Windows por falta de privilégio para criá-los.
- Testes Windows cobrem widgets/callbacks reais e evento de drop simulado; o gesto físico do Explorer, outros monitores/DPI e antivírus não foram validados.
- O executável local não foi publicado como release nem assinado digitalmente.
