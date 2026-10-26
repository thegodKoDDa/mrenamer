# Memória do projeto

- Produto: Renomeador de Mídia/MediaRenamer; pasta `/home/gabriel/dev/mrenamer`. Criado originalmente no Cursor/VS Code.
- Organização solicitada em 25/10/2026 baseada no EletroProjeto/Minecoord: regras na raiz, estado/memória/histórico, documentação por responsabilidade e recuperação verificável. Stack própria preservada: Python/Tkinter, tkinterdnd2, PyInstaller, distribuição Windows.
- Fontes ativas: `renamer/Renomeador_de_Midia_Projeto/media_renamer.py` (GUI) e `rename_engine.py` (motor independente de GUI). Original de 278 linhas preservado em `renamer original/`.
- Caminhos antigos preservados para compatibilidade. Distribuição principal `renamer final/MediaRenamer.exe`; segunda cópia ativa no dist do aplicativo. Executáveis e backups históricos não são atualizados como cópias ativas.
- Regra permanente herdada: mudanças no aplicativo exigem testes, backup individual de cada exe ativo ANTES da compilação, nova build Windows e atualização/verificação das cópias. Documentação/continuidade não integram o produto empacotado.
- Python Windows existente é chamado a partir do WSL. Build automatizada em `scripts/build_windows.py`, com staging local Windows, testes, smoke do exe, backups e manifesto de proveniência. Dependências fixadas nas versões já instaladas/validadas; não atualizar por rotina.
- Correções solicitadas após publicação: validação global, rollback, recuperação manual por mapa, extensão preservada, desfazer por duas fases, modos de prévia separados, entradas numéricas seguras e monitoramento em thread. Não prometer atomicidade contra queda de energia.
- Preferências reais em `~/.media_renamer.json`; mídias nas pastas do usuário não entram nos checkpoints do projeto. Desfazer é somente em memória.
- Backup inicial completo `.checkpoints/before-organization/`: 90 arquivos iniciais e SHA-256. Fontes originais, backups herdados e pontos anteriores preservados. Novos checkpoints são restaurados isoladamente antes de atualizar latest.json.
- Inicialmente não havia Git. Usuário autorizou explicitamente publicar em repositório público em 25/10/2026: `thegodKoDDa/mrenamer`, origin HTTPS e branch main. Fontes/docs/testes/manifesto são públicos; executáveis, backups, checkpoints e credenciais permanecem locais. Não há autorização herdada de outros projetos nem publicação de release binária.
- Fluxo confirmado com o usuário ao encerrar em 25/10/2026: após alterações, testar, gerar exe quando o aplicativo mudar, revisar, fazer commit e enviar ao GitHub, conferindo sincronização. Não há envio automático a cada salvamento; arquivos locais privados permanecem excluídos.

- Entrega de 26/10/2026: recuperação assistida explícita em Configurações; mapas versão 2 incluem tamanho/mtime_ns e ficam na ancestral comum às origens. Mapas versão 1 não são convertidos e precisam de recuperação manual. Interrupção da própria recuperação pode exigir resolver primeiro um novo mapa.
- Escala fixa 1.1 removida; janela usa escala Tk e linhas seguem métrica de fonte. Testes programáticos 100%/150%/200% e listas Tcl de drop ampliados; não equivalem a gesto físico nem troca real de monitores.
- Benchmark local com 1.000/10.000 arquivos fictícios e preferências isoladas em scripts/benchmark.py; resultados e metodologia em docs/development.md. Carregamento manual e renomeação ainda são síncronos, rede não avaliada.
