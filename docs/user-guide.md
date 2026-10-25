# Manual do Renomeador de Mídia

Abra `renamer final/MediaRenamer.exe` no Windows ou execute pelo código conforme o README.

1. Selecione uma pasta ou arraste uma pasta para a janela. Arquivos arrastados juntos precisam pertencer à mesma pasta.
2. Escolha o filtro de categoria e a ordenação. A busca por nome (Ctrl+F) restringe a lista visível.
3. Selecione os arquivos desejados. Use Ctrl/clique para seleção múltipla ou os botões de selecionar/desmarcar todos.
4. Defina nome base, separador, número inicial e dígitos. A sequência acompanha os selecionados na ordenação atual.
5. Opcionalmente habilite data/hora, formato e fonte da data. O formato DD/MM/AAAA usa hífens no nome do arquivo.
6. Confira a coluna de prévia e clique em RENOMEAR ARQUIVOS. A confirmação depende da preferência em Configurações.

Configurações reúne tema claro/escuro, confirmação, intervalo de monitoramento e abertura de subpastas. Preferências ficam em `~/.media_renamer.json`.

O monitoramento atualiza a lista automaticamente, sem renomear sozinho. Downloads parciais, arquivos sem extensão e temporários reconhecidos são ignorados. Duplo clique abre um arquivo no aplicativo padrão do Windows.

Substituir texto atua sobre os nomes originais selecionados; os campos também afetam a prévia do padrão. Esses fluxos têm diferenças e limitações registradas em KNOWN_ISSUES. A aplicação da substituição ao padrão pode alterar a extensão; confira o resultado com cuidado e teste em cópias.

DESFAZER funciona na sessão atual e não fica salvo ao fechar; tem limitações em trocas de nomes e falhas parciais. LIMPAR encerra a pasta atual na tela, preservando as opções de padrão e sem desfazer renomeações já aplicadas.

Para arquivos importantes, trabalhe primeiro com uma cópia. A operação não tem recuperação automática completa em caso de falha. Checkpoints do projeto não incluem as mídias escolhidas fora dele. Consulte [pendências conhecidas](KNOWN_ISSUES.md).
