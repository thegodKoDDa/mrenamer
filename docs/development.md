# Desenvolvimento e distribuição

Preservar a versão funcional e testar com arquivos fictícios. A interface e o executável têm como alvo Windows. Linux/WSL permite análise e testes sem janela; isso não valida o executável Windows.

## Execução

Na pasta `renamer/Renomeador_de_Midia_Projeto`, em ambiente Windows Python 3.10+ com Tkinter, instalar requirements se necessário e executar `python media_renamer.py`. Não atualizar dependências por rotina. As versões usadas na build herdada não estão registradas por lock; estabelecer ambiente reproduzível antes de uma nova release.

## Ciclo obrigatório de alteração do aplicativo

1. Criar checkpoint antes da mudança estrutural; editar e testar em pastas temporárias.
2. Localizar as cópias ativas de MediaRenamer.exe (arquitetura lista as duas atuais).
3. Copiar cada executável ativo individualmente para um novo backup com timestamp; conferir SHA-256 e preservar todos os anteriores.
4. No Windows, a partir da pasta do aplicativo, executar `python -m PyInstaller --clean media_renamer.spec`. Usar o spec, que inclui recursos de tkinterdnd2.
5. Só após build válida, atualizar `renamer final/MediaRenamer.exe` e as demais cópias ativas. A saída PyInstaller também conta como cópia que exige backup antes da build.
6. Conferir hashes idênticos das cópias e registrar hash da fonte, dependências, ambiente e resultado do teste do executável. Igualdade entre executáveis sozinha não comprova correspondência com a fonte.
7. Testar abertura, arrastar/soltar, filtros, seleção, datas, prévia, conflitos, renomeação e desfazer em arquivos fictícios no Windows. Se falhar, manter/restaurar a distribuição anterior e registrar a pendência.

Históricos e backups nunca recebem a nova versão. Não declarar mudança no aplicativo entregue sem recompilar, atualizar e verificar o executável.

## Ferramentas locais

`python3 -m unittest discover -s scripts -p 'test_*.py' -v` testa recuperação, exclusões, corrupção e caminhos inválidos. Não exige rebuild do aplicativo. Não há suíte automatizada permanente da GUI nesta etapa; a revisão contém evidências isoladas de problemas existentes.
