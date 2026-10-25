# Desenvolvimento e distribuição

Python/Tkinter e distribuição Windows preservados. Testar somente com arquivos fictícios em pastas temporárias. Não modificar preferências reais em testes.

## Execução e dependências

Na pasta `renamer/Renomeador_de_Midia_Projeto`, executar `python media_renamer.py` com Python Windows. Quando o ambiente ainda não possui dependências, instalar `python -m pip install -r requirements-build.txt`. As versões fixadas refletem o ambiente validado: Python 3.13.15, PyInstaller 6.22.3 e tkinterdnd2 0.6.3. Não instalar/atualizar por rotina.

## Verificações

Na raiz:

```sh
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

No Linux, testes Windows são pulados; no Windows usar `python`. A suíte de GUI abre widgets reais com janela recolhida e arquivos/preferências temporários; cobre padrão, substituição, desfazer, datas, busca, seleção, ordenação, tema, Configurações e drop simulado. Não substitui validação manual de gesto físico/monitores/DPI.

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
