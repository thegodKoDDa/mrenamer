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

- O lote não é uma transação atômica do filesystem. Queda de energia, remoção externa, disco indisponível ou bloqueio também durante rollback podem exigir recuperação pelo `.__renamer_recovery_*.json`. Há recuperação assistida explícita em Configurações para mapas versão 2; mapas versão 1 ou arquivos indisponíveis/alterados ainda exigem tratamento manual. Não há retomada automática após reiniciar.
- Desfazer fica em memória e se perde ao fechar. Alterações externas no conteúdo não são revertidas. Não executar outro programa alterando os mesmos arquivos simultaneamente.
- Um mapa residual pode permanecer se sua remoção falhar depois de sucesso/rollback; conferir os arquivos e as identidades registradas antes de recuperar manualmente. Não executar o mapa como código.
- Varredura automática foi retirada da thread da GUI; abertura manual de pasta, estatísticas e renderização da tabela ainda podem demorar em grandes acervos ou volumes de rede. Benchmark sintético Windows com 1.000/10.000 arquivos foi executado em 26/10/2026; resultados e limites em development.md. Com 10.000 arquivos houve 5,66 s para carregar a lista e 12,32 s para renomear; essas operações ainda podem pausar a interface. Rede, milhões de itens e arquivos grandes não foram medidos.
- Estabilidade de tamanho em duas observações não garante que uma cópia terminou.
- st_ctime segue a semântica Windows para o campo de criação. Comprimento do caminho completo também depende das políticas Windows/filesystem; nomes individuais são validados.
- Symlinks são recusados. A regressão de symlinks passou no Linux e foi pulada no Windows por falta de privilégio para criá-los.
- Testes Windows cobrem widgets/callbacks reais, drop com lista Tcl (múltiplos arquivos, acentos/espaços/chaves e rejeição de misturas/pastas diferentes), escala Tk de 100%/150%/200%, altura de linhas e limites da janela. Removida a escala fixa 1.1. O gesto físico do Explorer, mudança real entre monitores/DPI, telas pequenas e interferência de antivírus ainda exigem validação manual; não são cobertos pela simulação.
- O executável local não foi publicado como release nem assinado digitalmente.

## Entregue em 26/10/2026

- Recuperação assistida de mapas versão 2, com prévia e confirmação, bloqueio de identidades ausentes/ambíguas, alterações de tamanho/data, caminhos externos/links e conflitos; revalidação antes dos movimentos.
- Testes encerram processo isolado abruptamente após cada movimento de um ciclo e verificam a restauração do conteúdo fictício. Isso simula interrupção de processo, não corte de energia nem persistência física do filesystem.
- Mapas registram a pasta comum às origens para permitir lotes em subpastas. Arquivos e mapa não devem ser movidos antes de recuperar. Interrupção durante a recuperação pode produzir outro mapa a resolver antes do inicial.
