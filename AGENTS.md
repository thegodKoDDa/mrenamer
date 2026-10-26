# Regras permanentes do mrenamer

- Ao retomar, ler `docs/CURRENT_STATE.md` e `docs/PROJECT_MEMORY.md`; executar `python3 scripts/continuity.py retomar` (Windows: `python`).
- Preservar produto, identidade visual, funcionalidades corretas, fontes originais e histórico de executáveis. Não recriar nem trocar a stack sem necessidade.
- Fontes ativas: `renamer/Renomeador_de_Midia_Projeto/media_renamer.py` (GUI) e `rename_engine.py` na mesma pasta (motor). Original histórico em `renamer original/`; distribuição principal em `renamer final/MediaRenamer.exe`.
- Antes de mudanças estruturais, criar checkpoint e verificar recuperação. Nunca apagar pontos únicos de recuperação ou substituir executáveis sem backup individual prévio.
- Regra herdada: qualquer alteração no código do aplicativo exige testes, backup individual de cada MediaRenamer.exe ativo, compilação Windows, atualização de todas as cópias ativas e conferência dos hashes. Backups históricos são imutáveis e não devem receber o novo executável. Ver `docs/development.md`.
- Documentação e scripts locais de continuidade não integram o executável; mudanças apenas neles não exigem reconstruir a distribuição.
- Testar renomeação somente em diretórios temporários com arquivos fictícios; nunca usar a mídia real do usuário como fixture. Não salvar configurações reais durante testes.
- Após mudar continuidade: `python3 -m unittest discover -s scripts -p 'test_*.py' -v`. Para o aplicativo: `python -m unittest discover -s tests -v` e build obrigatório com `python scripts/build_windows.py` no Windows. A rotina inclui testes e abertura/fechamento do executável.
- Extensões devem ser preservadas. Não prometer atomicidade ou recuperação automática após queda de energia; mapas persistentes ajudam na recuperação manual. Ver limites em KNOWN_ISSUES.
- Atualizar documento responsável e CURRENT_STATE; acrescentar SESSION_HISTORY e CHANGELOG nas entregas. Evitar duplicar arquitetura e regras em novos arquivos.
- Não versionar mídia, executáveis, backups, checkpoints, dependências, caches, configurações pessoais nem credenciais. Não copiar stack, regras elétricas ou autorizações remotas de outros projetos.
- Ao encerrar: revisar alterações e arquivos novos, executar verificações proporcionais, criar checkpoint com `encerrar` e conferir o resultado. A rotina não faz commit ou push automaticamente. Repositório público autorizado em 25/10/2026: `thegodKoDDa/mrenamer`. Publicar fontes e documentação revisadas no Git. Em 26/10/2026, usuário autorizou distribuir o executável e ZIP portátil em Releases e automatizar novas versões validadas; executáveis continuam fora do histórico Git. Dados pessoais, backups e checkpoints permanecem locais.
