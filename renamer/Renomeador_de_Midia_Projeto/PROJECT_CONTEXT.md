# Contexto técnico

Documentação consolidada em [arquitetura](../../docs/architecture.md), [desenvolvimento](../../docs/development.md), [memória](../../docs/PROJECT_MEMORY.md) e [estado atual](../../docs/CURRENT_STATE.md). Leia também [AGENTS](../../AGENTS.md).

GUI em media_renamer.py e motor de validação/renomeação em rename_engine.py. Alterações no aplicativo exigem build Windows e backup individual prévio de cada executável ativo; `scripts/build_windows.py` executa o fluxo a partir da raiz. Históricos e backups antigos não são sobrescritos.
