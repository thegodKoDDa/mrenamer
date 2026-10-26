# Contribuir

Use as [issues](https://github.com/thegodKoDDa/mrenamer/issues) para relatar problemas ou discutir melhorias. Antes de propor uma mudança ampla, descreva o comportamento desejado e seu impacto.

## Preparar o ambiente

Siga a instalação no [README](README.md). As fontes ativas ficam em `renamer/Renomeador_de_Midia_Projeto/`:

- `media_renamer.py`: interface Tkinter/ttk e integração com o usuário.
- `rename_engine.py`: validação e operações sobre nomes de arquivos.

Os caminhos existentes, a identidade visual e as fontes históricas devem ser preservados. Consulte a [arquitetura](docs/architecture.md) antes de alterar o fluxo de renomeação.

## Validar uma alteração

Na raiz do repositório:

```powershell
python -m unittest discover -s tests -v
python -m unittest discover -s scripts -p "test_*.py" -v
```

No Linux, use `python3`; os testes específicos do Windows são pulados. Teste renomeações apenas em diretórios temporários com arquivos fictícios e preferências isoladas.

Alterações no aplicativo também exigem build Windows, testes do executável e backup individual de cada cópia ativa antes da atualização. A rotina e os requisitos estão em [Desenvolvimento](docs/development.md). Mudanças apenas na documentação não exigem reconstruir o executável.

## Enviar uma proposta

Abra um pull request com o problema, o comportamento resultante e as verificações executadas. Atualize o documento responsável e o [changelog](CHANGELOG.md) quando houver alteração visível ao usuário.

Não inclua mídias, preferências pessoais, credenciais, executáveis, dependências instaladas, backups ou checkpoints. Para relatar um erro com nomes de arquivos, use exemplos fictícios e remova caminhos pessoais.
