# Arquitetura

## Aplicativo

`media_renamer.py` reúne a classe `MediaRenamer`, interface Tkinter/ttk, preferências JSON, filtros, monitoramento, geração de nomes e execução de renomeações. A entrada cria `TkinterDnD.Tk()` quando disponível, ou `tk.Tk()`, e inicia `mainloop()`.

Fluxo: escolher pasta/arrastar → coletar arquivos → filtrar/ordenar → selecionar → gerar prévia → validar destinos → confirmar → renomear em duas fases → recarregar. Monitoramento usa `root.after`, respeita `_busy` e compara tamanho em duas observações para arquivos novos. Não é garantia de que uma cópia externa terminou.

`rename_operations` move primeiro as fontes para nomes temporários e depois para destinos. Não há rollback persistente. `undo_stack` guarda operações apenas na memória; o desfazer atual renomeia sequencialmente. Ver KNOWN_ISSUES antes de alterar esse núcleo.

A numeração segue somente os selecionados na ordem atual. Filtros distinguem fotos, vídeos, áudio, documentos e outros; arquivos sem extensão, downloads parciais, temporários do programa e nomes iniciados em `~$` são excluídos.

## Dados

Preferências em `~/.media_renamer.json`: tema, confirmação, intervalo de monitoramento e subpastas. Arquivos escolhidos não são copiados para o projeto. Desfazer não persiste ao fechar. Checkpoint do projeto não desfaz renomeações nem protege mídias externas.

## Distribuição

Spec documentado: `renamer/Renomeador_de_Midia_Projeto/media_renamer.spec`; `MediaRenamer.spec` é equivalente após normalizar fins de linha. Ambos usam coleta dos dados de tkinterdnd2, onefile e janela sem console. Dependências herdadas sem pin em requirements.txt: pyinstaller e tkinterdnd2.

Cópias ativas de MediaRenamer.exe: `renamer final/` e `renamer/Renomeador_de_Midia_Projeto/dist/`. Outros executáveis Renomeador_de_Midia.exe e `renamer original/` são históricos. Não atualizar históricos como se fossem distribuição ativa.

Scripts em `scripts/` são ferramentas de manutenção separadas e não integram o pacote PyInstaller.
