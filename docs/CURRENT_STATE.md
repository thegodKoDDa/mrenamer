# Estado atual — 26/10/2026

Apresentação pública reorganizada: README voltado ao produto e à instalação, navegação por uso/desenvolvimento/manutenção, changelog consolidado, guia de contribuição e modelos de issues/PR. Descrição e tópicos do GitHub atualizados. Esta revisão altera somente documentação e metadados; fontes e executáveis mantêm a build abaixo.

Recuperação assistida implementada em **Configurações → Recuperar lote interrompido…**, com inspeção, prévia, confirmação e revalidação. Preservados produto, identidade visual, fontes originais, stack e históricos.

Fontes ativas: `renamer/Renomeador_de_Midia_Projeto/media_renamer.py` (GUI) e `rename_engine.py` (motor). Mapas novos versão 2 registram identidade, tamanho e mtime_ns; ficam na pasta ancestral comum às origens. Recuperação recusa arquivos ausentes/alterados, conflitos, links e mapas inconsistentes. Mapas versão 1 continuam manuais. O fluxo não inicia recuperação sozinho, nem garante atomicidade contra queda de energia. Manual e limites em user-guide.md e KNOWN_ISSUES.md.

Interface mantém a escala do Tk em vez de impor 1.1; janela inicial respeita os limites da tela e altura das linhas acompanha a fonte. Drop foi ampliado nos testes para listas Tcl com múltiplos arquivos, acentos, espaços e chaves, além de rejeições de pastas diferentes/itens misturados.

Validação: 44 casos Windows, 42 aprovados e dois symlinks pulados por privilégio; 44 casos Linux, 32 aprovados e 12 pulados por dependerem do Windows. Três testes de continuidade aprovados. Inclui encerramento abrupto de processo em cada movimento de um ciclo, recuperação pela GUI com cancelamento/confirmação, bloqueio real Windows e escalas Tk 100%/150%/200%.

Benchmark Windows reproduzível: `python scripts/benchmark.py --gui`, somente mídia fictícia/preferências temporárias. Com 1.000/10.000 arquivos: carregar lista + prévia 0,601/5,661 s; atualizar prévia 0,159/1,580 s; renomear 1,248/12,323 s. Cache aquecido e GUI recolhida; não representa rede nem garante responsividade. Tabela completa em development.md.

Build Windows `20261026T035150145944Z`: Python 3.13.15 e dependências fixadas mantidos. Executável abriu/fechou com código zero; duas cópias ativas atualizadas e conferidas, com backups individuais prévios preservados. SHA-256: `7949d7a1ed74431adcb9c270a047534f0b128e798b6340a3130c824547cdcffe`. Proveniência em `renamer final/build-manifest.json`.

Ainda dependem do ambiente físico: gesto real do Explorer e mudança entre monitores/DPI. Escala programática não substitui essas verificações. Grandes volumes/rede e responsividade durante carregamento/renomeação continuam limitados; o benchmark agora fornece referência local. Se a recuperação for interrompida e gerar outro mapa, resolver esse novo mapa antes do inicial.

GitHub público autorizado: https://github.com/thegodKoDDa/mrenamer, branch main. Somente fontes/docs/testes/manifesto; executáveis, backups e checkpoints permanecem locais. Encerramento cria checkpoint com restauração temporária verificada, apontado por `.checkpoints/latest.json`. Retomar com `python3 scripts/continuity.py retomar`.
