# Renomeador de Mídia

A documentação atual está na raiz do projeto:

- [Visão geral e execução](../../README.md)
- [Manual de uso](../../docs/user-guide.md)
- [Desenvolvimento, testes e build Windows](../../docs/development.md)
- [Estado atual](../../docs/CURRENT_STATE.md)
- [Limites conhecidos](../../docs/KNOWN_ISSUES.md)

Nesta pasta: media_renamer.py (GUI), rename_engine.py (motor sem GUI), requirements.txt/requirements-build.txt e media_renamer.spec (canônico). MediaRenamer.spec é compatibilidade com o nome antigo.

Regra permanente: qualquer mudança no aplicativo exige testes, backup individual de cada executável ativo antes de compilar, nova build Windows e atualização verificada das cópias ativas. Executar `python scripts/build_windows.py` a partir da raiz com Python Windows. Preservar todos os backups anteriores. Distribuição principal: `renamer final/MediaRenamer.exe` na raiz.
