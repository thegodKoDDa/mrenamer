# Manual do Renomeador de Mídia

Abra `renamer final/MediaRenamer.exe` no Windows ou execute pelo código conforme o README.

1. Selecione uma pasta ou arraste uma pasta para a janela. Arquivos arrastados juntos precisam pertencer à mesma pasta.
2. Escolha o filtro de categoria e a ordenação. A busca por nome (Ctrl+F) restringe a lista visível.
3. Selecione os arquivos desejados. Use Ctrl/clique para seleção múltipla ou os botões de selecionar/desmarcar todos.
4. Para gerar uma sequência, defina nome base, separador, número inicial (0 a 999999) e dígitos (1 a 8). Opcionalmente inclua data/hora e escolha sua fonte/formato. A sequência acompanha os selecionados na ordenação atual.
5. Selecione a prévia Padrão e confira a coluna Novo nome. Use RENOMEAR (PADRÃO) para aplicar; a confirmação depende da preferência em Configurações.
6. Para alterar texto dos nomes existentes, preencha Procurar/Substituir por e selecione a prévia Substituição. Confira e use Aplicar substituição, que sempre pede confirmação. Esses campos não afetam a renomeação por padrão.

Ambas as operações preservam a última extensão original e recusam nomes inválidos ou destinos conflitantes. Não convertem formatos de mídia. Campos inválidos exibem mensagem na tela e impedem a operação.

Configurações reúne tema claro/escuro, confirmação, intervalo de monitoramento e abertura de subpastas. Preferências ficam em `~/.media_renamer.json`.

Monitoramento atualiza a lista automaticamente, sem renomear sozinho. Downloads parciais, arquivos sem extensão, symlinks e temporários reconhecidos são ignorados. Duplo clique abre no aplicativo padrão do Windows. O formato de data DD/MM/AAAA usa hífens no nome.

DESFAZER restaura os nomes do último lote, inclusive trocas de nomes, durante a sessão atual. Não fica salvo ao fechar. LIMPAR encerra a pasta na tela, preservando opções do padrão e sem desfazer operações aplicadas.

Em falha, o programa tenta restaurar os nomes anteriores e informa se conseguiu. Se a recuperação ficar incompleta, não repita o lote: guarde o caminho do mapa JSON e os arquivos indicados na mensagem. O mapa contém nomes originais, temporários e destinos para recuperação manual. Não apague temporários antes de recuperar.

Queda de energia e bloqueios externos podem exigir recuperação manual. Para arquivos importantes, trabalhe primeiro com cópias. Checkpoints do código não incluem as mídias externas. Consulte [limites atuais](KNOWN_ISSUES.md).
