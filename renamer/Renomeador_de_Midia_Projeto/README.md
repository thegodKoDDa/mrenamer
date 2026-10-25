# Renomeador de Mídia

Aplicativo desktop para **Windows** que renomeia em lote fotos, vídeos, áudios, documentos e outros arquivos com extensão, usando um padrão configurável (nome base + contador).

---

## O que é e para que serve

O **Renomeador de Mídia** organiza nomes de arquivos de forma rápida e previsível. Você escolhe uma pasta, filtra o tipo de arquivo, seleciona o que deseja alterar, define o padrão (nome, separador, dígitos e número inicial) e confere a **prévia** antes de aplicar.

Ideal para sequências como `Gameplay_001.mp4`, `Gameplay_002.jpg`, pastas de projetos, backups e bibliotecas de mídia.

---

## Normas obrigatórias de desenvolvimento e distribuição

Estas regras são obrigatórias para todo trabalho no projeto e devem ser seguidas por desenvolvedores e agentes/IA.

1. **Compilação obrigatória após qualquer alteração no código**
   - Após qualquer alteração concluída no código-fonte do projeto, o projeto deve ser recompilado imediatamente.
   - A compilação é parte do processo de conclusão e não uma etapa opcional.
   - Não se considera uma alteração concluída sem atualizar o executável correspondente.

2. **Executável principal de distribuição**
   - O executável principal de distribuição do projeto é: `renamer final/MediaRenamer.exe`.
   - Sempre que o projeto for recompilado, o `MediaRenamer.exe` da pasta `renamer final` deve ser atualizado para refletir exatamente a versão mais recente do código.
   - Todos os demais `MediaRenamer.exe` existentes no projeto também devem ser atualizados para a mesma versão, quando aplicável.
   - Todos os executáveis `MediaRenamer.exe` do repositório devem corresponder à versão atual do código.

3. **Regra de conclusão do processo**
   - Alterar código sem recompilar e sem atualizar os executáveis não é considerado um processo concluído.
   - A atualização do executável é requisito obrigatório e deve acompanhar cada mudança de código.

4. **Norma geral — backup dos executáveis**
   - Antes de qualquer nova compilação de um `.exe`, é obrigatório criar uma cópia de segurança da versão anterior do executável.
   - Antes de substituir qualquer `MediaRenamer.exe`, o executável atual deve ser copiado primeiro e preservado como backup.
   - A cópia de segurança deve preservar exatamente a versão anterior do executável.
   - Cada backup deve ser preservado individualmente; não sobrescrever backups anteriores.
   - Use nomes claros e organizados para os backups, preferencialmente incluindo data e hora ou identificador de versão.
   - Essa regra vale para todos os diretórios que contenham `MediaRenamer.exe` atualmente utilizados pelo projeto.
   - Se a compilação falhar, a versão anterior deve continuar intacta e disponível.
   - Se a nova versão apresentar problemas, deve ser possível recuperar a versão anterior por meio do backup.

5. **Fluxo obrigatório para qualquer alteração que exija nova compilação**
   1. Alterar o código.
   2. Testar/verificar a alteração.
   3. Localizar todos os `MediaRenamer.exe` atualmente utilizados pelo projeto.
   4. Criar um backup individual de cada executável atual.
   5. Somente depois dos backups estarem criados, realizar a nova compilação.
   6. Atualizar o `renamer final/MediaRenamer.exe`.
   7. Atualizar todos os demais `MediaRenamer.exe` utilizados pelo projeto.
   8. Confirmar que os novos executáveis correspondem à versão atual do código.
   9. Manter todos os backups anteriores preservados.

6. **Instrução explícita para Agents/IA**
   > "Após qualquer alteração no código, recompilar imediatamente o projeto e atualizar o MediaRenamer.exe da pasta renamer final. Atualizar também todos os demais MediaRenamer.exe existentes que façam parte do projeto. Antes de cada nova compilação, criar backup individual da versão anterior de cada MediaRenamer.exe atual e preservar todos os backups anteriores."

Essas normas devem ser observadas em todas as alterações futuras do projeto e devem constar como exigência permanente de desenvolvimento e distribuição.

---

## Requisitos

- **Windows** 10 ou superior (recomendado)
- **Python 3.10+** (apenas se for executar pelo código-fonte)
- Biblioteca padrão **Tkinter** (incluída na instalação oficial do Python no Windows)
- **tkinterdnd2** para arrastar arquivos e pastas do Windows Explorer para a janela

---

## Como instalar e executar

### Opção A — Executável (.exe)

1. Abra `dist\MediaRenamer.exe` (após gerar com PyInstaller; veja [Gerar o .exe](#gerar-o-exe)).
2. Não é necessário instalar Python.

### Opção B — Código-fonte (desenvolvimento)

Na pasta do projeto:

```bash
python -m pip install -r requirements.txt
python media_renamer.py
```

> `requirements.txt` lista as dependências de execução e de **build**. Para rodar pelo código-fonte, instale-o antes.

---

## Manual de uso (passo a passo)

### 1. Abrir o programa

Inicie o `.exe` ou `python media_renamer.py`. A janela **Renomeador de Mídia** será exibida.

### 2. Selecionar uma pasta

1. Em **Pasta de trabalho**, clique em **Selecionar pasta**.
2. Escolha a pasta que contém os arquivos.
3. O caminho aparece no campo **Pasta** e a lista é carregada automaticamente.

Por padrão, todos os arquivos elegíveis da pasta (com extensão) entram na lista quando o filtro está em **Todos**.

### 3. Selecionar arquivos

- **Clique** nas linhas da tabela para marcar ou desmarcar.
- **Selecionar todos** — marca todos os itens visíveis (respeitando o filtro atual).
- **Desmarcar todos** — remove a seleção.
- Ao carregar uma pasta **pela primeira vez**, todos os arquivos listados já vêm selecionados.

A barra de status mostra quantos arquivos foram encontrados e quantos estão selecionados.

### 4. Usar filtros

No bloco **Padrão de renomeação**, use o campo **Filtro**:

| Filtro | O que aparece na lista |
|--------|-------------------------|
| **Todos** | Todos os arquivos com extensão na pasta (todas as categorias abaixo + outros) |
| **Fotos** | Apenas imagens |
| **Vídeos** | Apenas vídeos |
| **Áudio** | Apenas áudio |
| **Documentos** | Documentos e compactados listados abaixo |
| **Arquivos/Outros** | Arquivos com extensão que não se encaixam nas categorias acima |

Alterar o filtro recarrega a lista. A pasta selecionada também é monitorada automaticamente: novos arquivos elegíveis aparecem na lista após serem detectados e estabilizados, respeitando o filtro, as subpastas e a ordenação atual. A seleção existente é preservada sempre que possível.

### 5. Configurações permanentes

Abra **Configurações** para alterar o tema, a confirmação antes de renomear, o intervalo da atualização automática e a opção **Abrir subpastas por padrão**. Essas preferências ficam centralizadas nesse menu.

Quando a opção de subpastas estiver ativada, a lista também considera arquivos em subdiretórios. Desativada, apenas a pasta raiz selecionada é considerada.

### 6. Definir o padrão de renomeação

| Campo | Função |
|-------|--------|
| **Nome base** | Texto fixo no início do nome (ex.: `Gameplay`) |
| **Nº inicial** | Primeiro número da sequência (ex.: `1`) |
| **Dígitos** | Quantidade de dígitos do contador, com zeros à esquerda (ex.: `3` → `001`, `002`) |
| **Separador** | Caractere entre o nome base e o número (ex.: `_`) |

**Exemplo**

- Nome base: `Gameplay`
- Nº inicial: `1`
- Dígitos: `3`
- Separador: `_`

Resultado:

```text
Gameplay_001.mp4
Gameplay_002.mp4
Gameplay_003.jpg
```

A numeração segue imediatamente a ordem escolhida em **Ordenar por**: Nome, Data de criação, Data de modificação ou Tamanho. Apenas os **selecionados** são renomeados, e a sequência numérica é recalculada na ordem atual dos selecionados.

Ao escolher uma opção em **Ordenar por**, a lista e a prévia são reorganizadas automaticamente.

Também é possível arrastar uma pasta para a janela para carregá-la como pasta de trabalho ou arrastar um ou mais arquivos da mesma pasta para carregá-los e selecioná-los. Arquivos de pastas diferentes devem ser processados separadamente.

O monitoramento automático apenas atualiza a lista. Nenhum arquivo é renomeado sem que você clique em **RENOMEAR ARQUIVOS**.

### 7. Visualizar a prévia

A tabela **Arquivo atual** / **Novo nome (prévia)** atualiza ao mudar pasta, filtro, seleção ou qualquer campo do padrão. Confira os nomes antes de confirmar.

### 8. Renomear

1. Clique em **RENOMEAR ARQUIVOS** (botão principal, no rodapé).
2. Leia o diálogo de confirmação com a amostra dos nomes.
3. Confirme para aplicar.

Em caso de erro (arquivo em uso, permissão, etc.), uma mensagem será exibida e a lista será atualizada.

### 9. Limpar / cancelar a pasta atual

Use **LIMPAR** (na área da pasta ou no rodapé) para encerrar o trabalho com a pasta atual **sem fechar o programa**:

- Limpa caminho da pasta, lista, seleções e prévia.
- O padrão de renomeação (nome base, dígitos, etc.) **permanece** como você deixou.

Se houver pasta carregada, arquivos na lista, seleção ou padrão alterado com pasta ativa, o programa **pede confirmação** antes de limpar.

### 10. Tema claro / escuro

Abra **Configurações** e escolha **Claro** ou **Escuro**. A preferência é salva para as próximas execuções.

---

## Extensões reconhecidas

Arquivos **sem extensão** não entram na lista.

### Fotos

`.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.bmp`, `.tiff`

### Vídeos

`.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`, `.m4v`, `.wmv`

### Áudio

`.mp3`, `.wav`, `.flac`, `.aac`, `.m4a`, `.ogg`, `.wma`

### Documentos (inclui compactados comuns)

`.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`, `.txt`, `.csv`, `.zip`, `.rar`, `.7z`

### Arquivos / outros

Qualquer outra extensão (ex.: `.psd`, `.exe`, `.json`) aparece em **Arquivos/Outros** e também em **Todos**.

Comparação de extensões **não diferencia maiúsculas de minúsculas** (`.JPG` = `.jpg`).

---

## Preservação da extensão

O programa altera apenas o **nome** do arquivo, não a extensão.  
Ex.: `video.mp4` com padrão acima vira `Gameplay_001.mp4` — o `.mp4` é mantido.

---

## Proteção contra conflitos e sobrescrita

Antes de renomear, o programa:

1. **Detecta nomes duplicados** gerados pelo mesmo padrão e cancela com aviso.
2. **Não sobrescreve** arquivos que já existem no destino (a menos que sejam os próprios arquivos da operação).
3. Usa **nomes temporários** durante o processo para reduzir colisões e permitir trocas de nome com mais segurança.

---

## Gerar o .exe

Na pasta do projeto:

```bash
python -m pip install -r requirements.txt
python -m PyInstaller --onefile --windowed --name MediaRenamer --clean media_renamer.py
```

Ou, usando o arquivo de especificação:

```bash
python -m PyInstaller --clean media_renamer.spec
```

O executável será criado em:

```text
dist\MediaRenamer.exe
```

Pastas `build\` e arquivos gerados pelo PyInstaller podem ser ignorados no controle de versão.

---

## Estrutura básica do projeto

```text
projeto/
├── README.md              # Manual do usuário e visão geral
├── PROJECT_CONTEXT.md     # Contexto técnico (desenvolvedores / IA)
├── media_renamer.py       # Aplicativo (Tkinter)
├── media_renamer.spec     # Configuração PyInstaller
├── requirements.txt       # Dependências de execução e build
├── build/                 # Artefatos temporários do PyInstaller
└── dist/                  # Executável gerado
```

---

## Documentação adicional

Detalhes de arquitetura, constantes de extensão e orientações para manutenção estão em **PROJECT_CONTEXT.md**.
