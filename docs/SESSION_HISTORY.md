# Histórico de sessões

## 25/10/2026 — Revisão e organização inicial

- Pedido: conhecer o projeto e organizar conforme o EletroProjeto e novos projetos.
- Inspecionadas fontes, documentação, specs, requisitos e distribuição; criado backup completo dos 90 arquivos antes de modificar a estrutura documental.
- Adicionados README/AGENTS/CHANGELOG de raiz, índice e documentos responsáveis por estado, memória, arquitetura, desenvolvimento, recuperação, manual, revisão e pendências.
- Adicionadas rotinas locais retomar/encerrar/verificar e três testes de recuperação/exclusões/corrupção/caminhos inválidos aprovados.
- Código do aplicativo e todos os binários/backups mantidos byte a byte; caminhos legados preservados. Sem atualização de dependências, build Windows ou teste de interface.
- Experimentos em diretório temporário confirmaram risco de extensão modificada e falha parcial sem rollback. Correções registradas para próximo ciclo com distribuição Windows.
- Git local inicializado na main com baseline revisado de fontes/docs e exclusões de arquivos locais; sem acesso/publicação remota. Checkpoint final validado por restauração isolada; ponto indicado por latest.json.

## 25/10/2026 — Publicação no GitHub

- Usuário solicitou repositório público. Criado `thegodKoDDa/mrenamer` e configurado origin HTTPS.
- Revisados arquivos versionados; fontes e documentação incluídas, executáveis/backups/checkpoints excluídos. Nenhuma licença foi escolhida em nome do usuário.
- Autenticação existente do gerenciador de credenciais reutilizada sem armazenar tokens no projeto.
- Conferir branch main remota e visibilidade após o envio; sem alteração no aplicativo ou nova build.

## 25/10/2026 — Correções e nova distribuição Windows

- Pedido: corrigir problemas encontrados na revisão. Checkpoint anterior criado antes da mudança.
- Extraído motor sem GUI com validação global de nomes Windows/destinos/extensões, movimentos sem substituição, mapa persistido e rollback em duas fases. Desfazer utiliza o mesmo motor e suporta ciclos.
- Separadas as prévias Padrão/Substituição, preservada a extensão, bloqueadas entradas inválidas e corrigido progresso em falhas. StringVar nos campos numéricos evita truncar decimais pelo IntVar.
- Monitoramento varre em thread sem Tk, descarta resultados antigos e compara assinaturas salvas. Removidas buscas quadráticas de seleção/estabilidade. Corrigida também a mistura de strings/Paths da seleção oculta.
- Specs consolidados, requisitos fixados nas versões existentes e guias ativos/documentação alinhados.
- 32 casos do aplicativo cobertos no Windows (31 aprovados, symlink pulado por privilégio); oito testes Tk, incluindo bloqueio real de arquivo. Três testes de continuidade aprovados. 24 testes comuns aprovados no Linux.
- Criado script de build Windows: testes, backups individuais com hash, staging, abertura/encerramento normais e conferência de cópias. O primeiro smoke falhou porque PowerShell não retinha o handle do processo para ler ExitCode; corrigida a verificação, sem distribuir a build rejeitada.
- Build final `20261025T233426653659Z`, SHA-256 `7b8fe26f74ca2713779c37334dbd1de6ea0573acf8e40ca31b84032ca3b28bfa`; duas cópias ativas atualizadas. Fontes/ambiente registrados em build-manifest.json. Backups de cada tentativa e históricos anteriores preservados. Preferências e mídias reais não foram usadas nos testes.
- Limites remanescentes documentados: recuperação manual após interrupção/bloqueio persistente; grandes acervos, DPI e drop físico não validados. Código/docs preparados para sincronização normal do GitHub público e checkpoint final verificado.

## 25/10/2026 — Encerramento solicitado pelo usuário

- Estado de entrega mantido: correções e build Windows concluídas; sem mudanças posteriores no aplicativo. Testes aprovados não repetidos sem mudança de código.
- Registrada a preferência de enviar alterações revisadas/testadas ao GitHub ao concluir o trabalho, conferindo sincronização.
- Conferidos hashes da distribuição e entradas do manifesto; documentação de continuidade atualizada. Encerramento inclui commit/envio desses registros e checkpoint com recuperação isolada verificada.
- Próxima sessão: ler CURRENT_STATE/PROJECT_MEMORY e executar retomar; seguir a próxima demanda, mantendo os limites registrados em KNOWN_ISSUES.

## 26/10/2026 — Pendências de uso e recuperação assistida

- Pedido: resolver pendências informadas na retomada. Estado/memória lidos e rotina retomar executada; Git inicialmente limpo. Checkpoint prévio `20261026T034754022756Z` criado e restaurado/verificado antes das mudanças.
- Adicionadas inspeção/revalidação de mapas e recuperação assistida em Configurações, com prévia e confirmação. Mapas novos versão 2 registram identidade, tamanho e mtime_ns; usam a pasta ancestral comum para lotes em subpastas. Mapas antigos e históricos preservados, sem conversão silenciosa.
- Removida escala fixa 1.1; altura da tabela usa métrica da fonte e tamanho inicial respeita escala Tk/limites da tela. Novos testes de listas Tcl com múltiplos arquivos Unicode/espaços/chaves, rejeições, recuperação pela GUI e escala Tk 100%/150%/200%.
- Regressões encerram processo isolado após cada movimento de um ciclo e verificam recuperação dos bytes fictícios. Cobrem conflitos, arquivo alterado/ausente, mapa antigo/inválido/duplicado, caminhos externos/links, grafia Windows, subpastas e falha durante recuperação.
- 44 casos Windows: 42 aprovados, dois symlinks pulados por privilégio. Linux: 32 aprovados, 12 pulados por dependência de Windows. Três testes de continuidade aprovados. Uma primeira execução revelou erro no mock de remoção do mapa no teste de grafia; teste corrigido e suíte final aprovada.
- Benchmark sintético Windows com 1.000/10.000 arquivos: carregar lista + prévia 0,601/5,661 s; prévia 0,159/1,580 s; renomear 1,248/12,323 s; desfazer 1,256/12,799 s. Script reproduzível e limites registrados em development.md. Sem uso de mídia/configuração real.
- Build `20261026T035150145944Z` entregue: `7949d7a1ed74431adcb9c270a047534f0b128e798b6340a3130c824547cdcffe`. Backups individuais em `backups/MediaRenamer_20261026T035150145944Z/`, duas cópias ativas conferidas e executável abriu/fechou com códigos zero. Nenhum histórico sobrescrito.
- Pendências físicas permanecem explícitas: gesto do Explorer, monitores/DPI reais e rede não foram validados. Operações grandes ainda podem pausar a GUI; não houve promessa de recuperação automática ou resistência a queda de energia.
- Documentação, arquivos novos e manifesto revisados; finalização inclui sincronização de fontes/documentação com GitHub e checkpoint restaurado/verificado.

## 26/10/2026 — Organização da apresentação pública

- Pedido: publicar as alterações e organizar o GitHub com apresentação profissional e sem informações desnecessárias. Rotina retomar executada; checkpoint prévio `20261026T035602558112Z` restaurado/verificado antes da revisão.
- README reescrito com proposta do produto, recursos, instalação em ambiente virtual Windows, exemplo de nomes, limites essenciais e links de documentação. Não anuncia executável disponível em Releases.
- Índice documental separado em uso, desenvolvimento e manutenção; changelog consolidado por data e impacto no produto. Limites conhecidos agrupados sem repetir a lista de correções já registrada no changelog. Guias ativos de texto atualizados para recuperação assistida.
- Adicionados CONTRIBUTING e modelos curtos de issues de erro/melhoria e de pull request. README da pasta ativa simplificado; removido PROJECT_CONTEXT.md, que duplicava referências da documentação. Originais históricos, decisões e registros de sessões preservados.
- Descrição e seis tópicos do repositório atualizados e conferidos pela API com autenticação Git reutilizada em memória. Nenhuma credencial incluída em arquivos ou saída. Integração disponível não oferece edição desses metadados, por isso foi usada a CLI.
- Links locais de Markdown e estrutura dos modelos YAML validados; três testes de continuidade aprovados. Fontes, executáveis e manifesto de build conferidos sem mudança; nenhuma reconstrução necessária para esta entrega documental.
- Revisão da seleção pública antes do commit/envio; mídias, executáveis, backups, checkpoints e preferências permanecem locais. Encerramento inclui checkpoint restaurado/verificado e conferência da sincronização com main remota.

## 26/10/2026 — Apresentação visual e verificações automáticas

- Pedido: aproximar a apresentação do formato do Minecoord disponível localmente. Consultados apenas README, índice de documentação e workflow do projeto de referência, sem modificá-lo ou transferir regras/stack/licença.
- Checkpoint prévio `20261026T040206099934Z` criado e restaurado/verificado. README recebeu abertura curta, captura real da GUI com arquivos fictícios, selo de verificações e navegação semelhante à referência, mantendo as instruções próprias do mrenamer.
- Prévia em `docs/assets/preview.png` capturada da própria janela Tk no Windows; pasta e preferências temporárias, sem mídia ou caminho pessoal. Captura inspecionada visualmente. Uma primeira limpeza temporária falhou por o processo ainda estar dentro da pasta; ajustado o diretório de trabalho antes de encerrar e a pasta fictícia foi removida.
- Workflow Verificações adicionado para Linux e Windows, com permissões de leitura, testes do aplicativo e de continuidade. Não compila nem publica executáveis. Documentação responsável e changelog atualizados.
- Validação local: 44 casos Linux (32 aprovados, 12 específicos do Windows pulados); 44 casos Windows (42 aprovados, dois symlinks pulados por privilégio); três testes de continuidade aprovados. Links, YAML e captura revisados. Fontes e binários preservados, sem necessidade de nova build.
- Envio acompanhado da execução remota inicial do workflow; fechamento com revisão dos arquivos públicos, sincronização de main e checkpoint com restauração verificada.
- Primeira execução remota: Linux aprovado; Windows revelou que o TEMP padrão da imagem usa caminho DOS 8.3 (`RUNNER~1`), recusado pela verificação conservadora dos mapas. Job ajustado para usar `runner.temp` como TEMP/TMP, sem alterar ou desativar as validações do motor. Restrição de caminhos abreviados documentada em KNOWN_ISSUES.

## 26/10/2026 — Distribuição pública e atualização das Releases

- Pedido: oferecer várias formas de uso, priorizando baixar e abrir o EXE mais atualizado. Autorização ampliada explicitamente para binários em Releases e publicação automática; a exclusão de executáveis do histórico Git e a privacidade dos dados locais continuam vigentes.
- Checkpoint anterior `20261026T041405739902Z` criado e restaurado/verificado antes da mudança. Sem alteração nas fontes do aplicativo ou nas cópias locais de executáveis.
- README passa a destacar download direto do EXE Windows x64 e ZIP portátil, além de código por clone/ZIP e build própria. Links Latest acompanham a última release estável; cópias já baixadas não atualizam sozinhas.
- Workflow release.yml testa no Linux, instala ambiente fixado no Windows e executa build_windows.py (testes, backups de cópias existentes, compilação e abertura/fechamento do EXE). Publicação limitada à main, serializada e com permissão de escrita apenas no job responsável.
- package_release.py valida inventário/hashes das fontes e cópias ativas, exige PE x64 e produz somente EXE, ZIP com guia/manifesto, manifesto com commit e lista SHA-256. O workflow cria rascunho, baixa os assets e confere hashes/conteúdo antes de publicar como Latest. Versões anteriores permanecem preservadas.
- Quatro testes novos de empacotamento aprovados junto aos três de continuidade; cobrem conteúdo público do pacote, divergência de fontes/binários, corrupção no download e proteção contra sobrescrever a saída. Empacotamento local real também conferido contra o manifesto, sem publicar o pacote de teste.
- Documentação, regras permanentes, memória e estado atual atualizados para refletir a autorização e as formas de distribuição. Envio acompanhado da primeira release e conferência dos downloads públicos antes do encerramento.
- Primeira release `build-1-1-7b4bc188` publicada pela automação; testes e build/smoke Windows aprovados. Downloads EXE/ZIP/manifesto/hashes testados anonimamente via HTTPS e conferidos: SHA-256 público `673df538b9ec53176ff64894d1adf5f19cbea5a30da5d77bb8d9dbfa2b339d76`. Sidebar do GitHub aponta para a última release. Acrescentada conferência da main antes de promover rascunho para impedir que a reexecução de um job antigo publique fontes já substituídas.

## 26/10/2026 — Encerramento solicitado pelo usuário

- Conferida sincronização da main com GitHub e disponibilidade da release estável `build-2-1-516d5be0`; release anterior preservada.
- Downloads públicos da última release já validados sem autenticação, com hashes e conteúdo do ZIP conferidos. EXE público: `93afeaef7388280b84947f9895ff4ff9a0299ca238f2b2b0c38dda6f4de89bcf`. Workflows de testes e publicação aprovados para o commit da distribuição.
- Estado atualizado para a última release. Fontes e duas cópias locais conferidas contra o manifesto local; nenhuma alteração no aplicativo ou nova compilação nesta finalização documental.
- Mantidas as quatro formas de uso: EXE recomendado, ZIP portátil, execução pelo código e build própria. Pendências físicas e limites operacionais continuam documentados.
- Encerramento inclui revisão documental, commit/envio dos registros e checkpoint com restauração temporária verificada. Retomar pela rotina habitual, sem refazer trabalho já validado.
