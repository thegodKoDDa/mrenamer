# Arquitetura

## Aplicativo

`media_renamer.py` mantém a classe MediaRenamer, interface Tkinter/ttk, preferências, filtros, datas, monitoramento e integração. Entrada: TkinterDnD.Tk() com fallback Tk, seguido de mainloop. A identidade visual e os caminhos de distribuição foram preservados.

`rename_engine.py` reúne regras sem GUI: validação de nomes Windows, substituição somente no stem, validação global de operações e renomeação com restauração em caso de falha. GUI usa esse motor para padrão, substituição e desfazer.

## Fluxos

Escolher pasta/arrastar → filtrar/ordenar → selecionar → escolher modo da prévia → validar lote → confirmar → executar → registrar desfazer → recarregar.

Padrão gera base/separador/data opcional/contador/extensão. Substituição atua no nome atual antes da última extensão; os campos de substituição não alteram o padrão. A sequência usa o índice dos selecionados na ordem corrente, sem buscas repetidas por item.

Monitoramento captura contexto na GUI e faz a varredura em thread daemon; resultados chegam por fila. Somente a thread principal usa Tk. A geração de contexto muda em recargas manuais para descartar resultados anteriores a renomeações ou mudanças de pasta. Arquivos novos aguardam tamanho estável em duas observações. Tabela e metadados ainda são atualizados na GUI.

## Segurança de renomeação

Antes de mover: validar origens, extensão, mesma pasta, nomes Windows e colisões globais sem distinção de caixa. Nenhuma mídia é testada/modificada fora dos caminhos selecionados pelo usuário.

O motor escreve e sincroniza um mapa JSON na pasta da primeira origem, com caminhos absolutos e identidade de cada arquivo. Move todas as origens para nomes temporários únicos e depois aos destinos. Windows usa rename sem substituição; POSIX usa link exclusivo seguido de unlink, pois rename POSIX poderia sobrescrever outro arquivo.

Em falha, libera primeiro os destinos já concluídos e depois restaura as origens, permitindo ciclos. Informa progresso real e resultado da restauração. Se incompleta, preserva mapa e caminhos atuais para recuperação manual. Não é atomicidade contra queda de energia; ver KNOWN_ISSUES.

## Dados e distribuição

Preferências reais: `~/.media_renamer.json`. Desfazer: pilha em memória. Mídias externas não entram nos checkpoints do projeto. Mapas de recuperação ficam nas pastas das mídias e são excluídos da listagem de arquivos elegíveis.

Spec canônico: `media_renamer.spec`; `MediaRenamer.spec` delega ao mesmo arquivo por compatibilidade. PyInstaller coleta tkinterdnd2, gera onefile sem console e inclui o motor importado. Dependências fixadas em requirements.txt e requirements-build.txt.

Cópias ativas: `renamer final/MediaRenamer.exe` e `renamer/Renomeador_de_Midia_Projeto/dist/MediaRenamer.exe`. `scripts/build_windows.py` testa, preserva cada cópia anterior, compila em pasta temporária Windows, abre/fecha a build e só então atualiza as cópias ativas. `renamer final/build-manifest.json` registra ambiente, hashes das entradas e do executável. Históricos em backups e renamer original não são atualizados.
