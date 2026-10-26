# Desenvolvimento e distribuição

O aplicativo usa Python, Tkinter/ttk e tkinterdnd2; a distribuição Windows é gerada com PyInstaller. Use arquivos fictícios em diretórios temporários e preferências isoladas nos testes.

## Execução e dependências

Para executar pelo código, siga a instalação em ambiente virtual no [README](../README.md). O ambiente de empacotamento validado usa Python 3.13.15, PyInstaller 6.22.3 e tkinterdnd2 0.6.3. As dependências são fixadas; atualizações devem ser avaliadas separadamente.

Para preparar um novo ambiente de build no Windows, ative o ambiente virtual e instale os requisitos a partir da raiz:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r renamer/Renomeador_de_Midia_Projeto/requirements-build.txt
```

Se a política do PowerShell impedir a ativação, use `.\.venv\Scripts\python.exe` no lugar de `python`, sem alterar a política do sistema.

### Estrutura do projeto

| Caminho | Conteúdo |
| --- | --- |
| `renamer/Renomeador_de_Midia_Projeto/` | Fontes ativas, dependências e specs |
| `tests/` | Testes do motor e da interface Windows |
| `scripts/` | Build, benchmark e continuidade |
| `docs/` | Documentação de uso e manutenção |
| `renamer original/` | Fontes históricas, sem desenvolvimento ativo |
| `renamer final/build-manifest.json` | Proveniência da última distribuição local |

Executáveis, ambientes virtuais, backups e checkpoints são locais e ficam fora do Git. O clone não contém `MediaRenamer.exe`; a primeira build cria as cópias ativas.

## Verificações

Na raiz:

```sh
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

No Linux, testes Windows são pulados; no Windows usar `python`. A suíte de GUI abre widgets reais com janela recolhida e arquivos/preferências temporários; cobre padrão, substituição, desfazer, datas, busca, seleção, ordenação, tema, Configurações e drop simulado. Não substitui validação manual de gesto físico/monitores/DPI.

### Integração contínua

O workflow [Verificações](../.github/workflows/ci.yml) executa os testes em pushes para `main` e em pull requests. No Linux, usa o Python do sistema com Tkinter e pula os casos exclusivos de Windows. No Windows, prepara Python 3.13 com as dependências fixadas e executa também os testes Tk. Ambos executam os testes de continuidade. O job Windows usa o diretório temporário completo do runner para as fixtures, evitando o alias DOS 8.3 presente no TEMP padrão da imagem.

O workflow verifica o código, sem gerar ou publicar executáveis. A entrega de uma alteração no aplicativo continua exigindo a rotina Windows abaixo.

## Build obrigatória após mudança no aplicativo

Criar checkpoint antes da mudança estrutural. Após editar, executar na raiz com Python Windows:

```powershell
python scripts/build_windows.py
```

O script:

1. Confere versões instaladas e executa testes do aplicativo, integração Windows e continuidade.
2. Cria backup individual de cada executável ativo, com timestamp e conferência SHA-256. Todos os backups anteriores permanecem.
3. Copia entradas para pasta temporária no Windows e executa `python -m PyInstaller --noconfirm --clean media_renamer.spec`.
4. Confere saída PE, abre e fecha normalmente a janela do novo exe, usando USERPROFILE temporário. Não fecha programas do usuário.
5. Confere que a fonte não mudou durante a build e prepara/confronta todas as cópias antes de substituir as ativas. Em falha de cópia/substituição tenta restaurar as versões anteriores dos backups.
6. Confere hashes iguais dos executáveis ativos e grava build-manifest.json com hashes das fontes/specs/requisitos, Python, plataforma e dependências.

Se testes, build ou abertura falharem, não distribui o resultado. Falhas de disco/ACL também podem impedir uma restauração de distribuição; os backups individuais permanecem disponíveis. Históricos nunca recebem a nova versão. O manifesto não é assinatura digital nem garante reprodutibilidade binária entre máquinas.

A partir do WSL, chamar o Python Windows instalado com o caminho Windows do script (converter com wslpath -w). O script cuida do staging local para evitar compilar diretamente em UNC.

Documentação e continuidade não integram o exe. Mudança somente nelas não exige build; mudança em media_renamer.py ou rename_engine.py exige.

## Benchmark e validações de uso — 26/10/2026

Reproduzir no Windows: `python scripts/benchmark.py --gui`. Aceita `--counts 1000 10000`; sem `--gui` mede somente varredura/motor. Usa diretório temporário Windows, arquivos fictícios de 10 bytes e preferências isoladas, restaura nomes e confere todos os conteúdos ao terminar. Não aponta para mídia do usuário.

Medição única local com Python 3.13.15, cache aquecido, GUI recolhida, sem descarregar cache ou simular rede. Não representa leitura/decodificação de mídia nem desempenho garantido; testes de GUI também estavam em execução durante parte da coleta.

| Arquivos | Varredura | Carregar + prévia | Atualizar prévia | Validar lote | Renomear | Desfazer |
| --- | --- | --- | --- | --- | --- | --- |
| 1.000 | 0,090 s | 0,601 s | 0,159 s | 0,132 s | 1,248 s | 1,256 s |
| 10.000 | 0,846 s | 5,661 s | 1,580 s | 1,268 s | 12,323 s | 12,799 s |

Os tempos indicam crescimento próximo ao proporcional nesse intervalo; carregamento manual/renderização/renomeação ainda são síncronos. A medição não comprova responsividade em acervos arbitrariamente grandes.

A suíte Windows acrescenta recuperação pela interface (cancelar/confirmar), listas Tcl de drop com Unicode/espaços/chaves e rejeições, além de inicialização/linhas nos fatores Tk correspondentes a 100%, 150% e 200%. Testes comuns usam processo isolado com `os._exit` após cada movimento para simular interrupção, conflitos, mudança de arquivos, mapas inválidos, links, subpastas e falha na recuperação. Nenhum teste interrompe o Windows ou usa mídia real.

Para fechar a validação física: arrastar uma pasta temporária e arquivos fictícios do Explorer para a janela e a tabela; conferir seleção; repetir nos monitores disponíveis e nas escalas reais, incluindo troca de monitor e abertura de Configurações. Conferir texto, botões e linhas sem cortes. Esse roteiro depende do desktop e dos monitores reais e continua pendente.
