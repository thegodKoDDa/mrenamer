# mrenamer

**Renomeie arquivos em lote, com prévia antes de aplicar.**

Aplicativo desktop para Windows que organiza nomes de fotos, vídeos, áudios e documentos. Crie sequências, inclua datas ou substitua trechos dos nomes, preservando as extensões originais.

[Manual de uso](docs/user-guide.md) · [Desenvolvimento](docs/development.md) · [Histórico de versões](CHANGELOG.md)

## Recursos

- **Prévia de nomes:** confira o resultado dos modos Padrão e Substituição antes de confirmar.
- **Sequências personalizadas:** combine nome base, separador, contador e data opcional.
- **Busca e seleção:** filtre por categoria, ordene a lista e escolha quais arquivos alterar.
- **Pastas e subpastas:** carregue pelo seletor ou por arrastar e soltar; acompanhe alterações na pasta.
- **Validação do lote:** detecte nomes inválidos e destinos conflitantes antes da renomeação.
- **Desfazer e recuperação:** reverta o último lote na sessão ou inspecione um mapa de lote interrompido.
- **Tema claro e escuro:** ajuste a aparência nas configurações.

## Executar no Windows

Requisitos: **Python 3.10 ou superior**, com Tkinter. O ambiente de distribuição é validado com Python 3.13.

```powershell
git clone https://github.com/thegodKoDDa/mrenamer.git
cd mrenamer
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r renamer/Renomeador_de_Midia_Projeto/requirements.txt
.\.venv\Scripts\python.exe renamer/Renomeador_de_Midia_Projeto/media_renamer.py
```

O repositório disponibiliza o código-fonte. Ainda não há instalador ou executável publicado em Releases. Para gerar o executável no Windows, consulte o [guia de desenvolvimento](docs/development.md).

## Uso rápido

1. Escolha uma pasta e selecione os arquivos.
2. Configure uma sequência no modo **Padrão** ou preencha os campos de **Substituição**.
3. Confira a coluna **Novo nome** e confirme a operação.

Exemplo de sequência:

```text
IMG_4821.jpg  →  Viagem_001.jpg
IMG_4822.jpg  →  Viagem_002.jpg
```

A renomeação altera o nome, sem converter o formato ou o conteúdo. **Desfazer** funciona durante a sessão. A recuperação de lotes interrompidos exige um mapa compatível e confirmação; ela não ocorre automaticamente após reiniciar. Consulte o [manual](docs/user-guide.md) e os [limites conhecidos](docs/KNOWN_ISSUES.md).

## Documentação

| Guia | Conteúdo |
| --- | --- |
| [Manual](docs/user-guide.md) | Uso, seleção, modos de renomeação e recuperação |
| [Desenvolvimento](docs/development.md) | Ambiente, testes, build Windows e benchmark |
| [Arquitetura](docs/architecture.md) | Interface, motor e fluxo de renomeação |
| [Limites conhecidos](docs/KNOWN_ISSUES.md) | Restrições e validações pendentes |
| [Changelog](CHANGELOG.md) | Evolução do produto |

## Contribuir

Consulte o [guia de contribuição](CONTRIBUTING.md). Para relatar um problema ou propor uma melhoria, [abra uma issue](https://github.com/thegodKoDDa/mrenamer/issues).
