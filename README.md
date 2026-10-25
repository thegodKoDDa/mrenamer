# mrenamer — Renomeador de Mídia

Aplicativo desktop para Windows, feito em Python/Tkinter, para renomear arquivos em lote com prévia, filtros, contador, datas, substituição de texto e desfazer. Projeto preservado da versão desenvolvida no Cursor/VS Code.

Código público: [thegodKoDDa/mrenamer](https://github.com/thegodKoDDa/mrenamer). Executáveis e backups continuam locais; esta publicação não inclui uma release binária.

Abra `renamer final/MediaRenamer.exe` no Windows. O [manual](docs/user-guide.md) descreve os recursos; veja as [limitações conhecidas](docs/KNOWN_ISSUES.md) antes de trabalhar com arquivos importantes.

Para executar pelo código no Windows, com Python 3.10+ e Tkinter:

```powershell
cd renamer/Renomeador_de_Midia_Projeto
python -m pip install -r requirements.txt
python media_renamer.py
```

A instalação é necessária apenas em um ambiente ainda sem dependências. A versão executável dispensa Python instalado. O suporte de arrastar/soltar usa tkinterdnd2.

## Organização

| Caminho | Responsabilidade |
| --- | --- |
| `AGENTS.md` | Regras para agentes e manutenção |
| `docs/` | Estado atual, memória, arquitetura, revisão e continuidade |
| `scripts/` | Rotinas locais de recuperação e seus testes |
| `renamer/Renomeador_de_Midia_Projeto/` | Código atual, dependências e specs herdados |
| `renamer final/` | Distribuição Windows atual e guia legado |
| `renamer original/` | Versão original preservada, sem desenvolvimento ativo |
| `backups/` | Histórico local de executáveis, preservado |
| `.checkpoints/` | Recuperação local verificada; fora do Git |
| `build/`, `dist/` em qualquer nível | Artefatos de empacotamento |

Os caminhos do aplicativo foram mantidos para preservar comandos, distribuição e referências existentes. A modularização do código é uma etapa futura, acompanhada de testes e nova distribuição Windows.

## Retomar e encerrar

Na raiz, com Python 3.10+ (`python3` no Linux/WSL; `python` no Windows):

```sh
python3 scripts/continuity.py retomar
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/continuity.py encerrar
python3 scripts/continuity.py verificar
```

Leia [CURRENT_STATE](docs/CURRENT_STATE.md) e [PROJECT_MEMORY](docs/PROJECT_MEMORY.md) ao retomar. O checkpoint inclui código, documentação e executáveis em `dist/` e `renamer final/`; backups históricos e gerados de build ficam fora dos checkpoints rotineiros. Nenhuma mídia externa escolhida no aplicativo entra nessa cópia.

Mudanças no aplicativo exigem backup individual dos executáveis, testes e compilação no Windows antes da entrega, conforme [desenvolvimento](docs/development.md). Mudanças somente na documentação ou nas ferramentas locais de continuidade não alteram o aplicativo distribuído.

[Índice da documentação](docs/README.md) · [Changelog](CHANGELOG.md)
