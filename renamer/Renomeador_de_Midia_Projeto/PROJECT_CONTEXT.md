# Project context — Renomeador de Mídia

Documento técnico para desenvolvedores e assistentes de código. Descreve o **estado atual** do repositório; a implementação em `media_renamer.py` é a fonte de verdade.

---

## Objetivo

Aplicação **Windows** (GUI) para renomear em lote arquivos em uma pasta (opcionalmente subpastas), com padrão `nomeBase + separador + contador`, prévia em tempo real, filtros por categoria de extensão e proteções contra sobrescrita e colisão de nomes.

---

## Normas obrigatórias do projeto (obrigatórias para desenvolvimento e agentes/IA)

Estas regras devem ser tratadas como parte do processo de desenvolvimento e não como diretrizes opcionais.

1. **Compilação obrigatória após qualquer alteração no código**
   - Após qualquer alteração concluída no código-fonte, o projeto deve ser recompilado imediatamente.
   - A compilação deve ocorrer após cada alteração concluída.
   - A versão executável precisa refletir exatamente o estado mais recente do código.
   - Não se considera uma alteração concluída sem atualizar o executável.

2. **Executável principal de distribuição**
   - O executável principal de distribuição é `renamer final/MediaRenamer.exe`.
   - Sempre que o projeto for recompilado, o `MediaRenamer.exe` da pasta `renamer final` deve ser atualizado.
   - Todos os outros `MediaRenamer.exe` existentes no projeto também devem ser atualizados para a mesma versão, quando aplicável.
   - Todos os executáveis `MediaRenamer.exe` devem corresponder à versão atual do código.

3. **Regra de conclusão do processo**
   - Alterar o código sem recompilar e sem atualizar o executável não é considerado um processo concluído.
   - O ciclo correto de trabalho é: alterar código → recompilar → atualizar os executáveis → validar a versão distribuída.

4. **Norma geral — backup dos executáveis**
   - Antes de realizar qualquer nova compilação de um arquivo `.exe`, é obrigatório criar uma cópia de segurança da versão anterior do executável.
   - Antes de substituir qualquer `MediaRenamer.exe`, o executável atual deve ser copiado primeiro e preservado como backup.
   - A cópia de segurança deve preservar exatamente a versão anterior do executável.
   - Depois que o novo `.exe` for compilado, ele poderá substituir o executável atual.
   - Essa regra deve ser aplicada a todas as pastas que contenham um `MediaRenamer.exe` atualmente utilizado pelo projeto.
   - Nenhum executável em uso deve ser sobrescrito sem que sua versão anterior tenha sido preservada primeiro.
   - A cada nova compilação, uma nova cópia de segurança deve ser criada.
   - Não sobrescrever backups anteriores; cada backup deve ser preservado individualmente.
   - Os backups devem usar nomes claros e organizados, preferencialmente com data e hora ou algum identificador de versão.
   - Se a compilação falhar, o executável anterior deve continuar intacto e disponível.
   - Se a nova versão apresentar problemas, a versão anterior deve poder ser recuperada pelo backup.

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

6. **Instrução obrigatória para Agents/IA**
   > "Após qualquer alteração no código, recompilar imediatamente o projeto e atualizar o MediaRenamer.exe da pasta renamer final. Atualizar também todos os demais MediaRenamer.exe existentes que façam parte do projeto. Antes de cada nova compilação, criar backup individual da versão anterior de cada MediaRenamer.exe atual e preservar todos os backups anteriores."

A compilação, a atualização dos executáveis e a criação de backup do executável anterior devem ser consideradas parte da implementação, não tarefas separadas ou opcionais.

---

## Tecnologias

| Item | Uso |
|------|-----|
| **Python 3** | Linguagem principal |
| **Tkinter / ttk** | Interface gráfica |
| **pathlib / os** | Sistema de arquivos e renomeação |
| **tkinterdnd2** | Arrastar arquivos e pastas do Windows Explorer |
| **PyInstaller** | Empacotamento em `.exe` (`--onefile`, `--windowed`) |

O código-fonte usa Tkinter e `tkinterdnd2`; o executável compilado já inclui esses componentes.

---

## Estrutura do código

Arquivo único: **`media_renamer.py`**.

| Elemento | Descrição |
|----------|-----------|
| `PHOTO_EXTENSIONS`, `VIDEO_EXTENSIONS`, `AUDIO_EXTENSIONS`, `DOCUMENT_EXTENSIONS` | Conjuntos de extensões (minúsculas) |
| `FILTER_OPTIONS` | Valores do combobox de filtro |
| `MediaRenamer` | Classe principal: UI, tema, carga de arquivos, prévia, renomeação, limpeza |

Fluxo principal:

1. `choose_folder` → `load_files` → `refresh_preview`
2. Alterações em padrão disparam `refresh_preview` via `trace_add`
3. `rename_files` valida, confirma, renomeia via arquivos temporários, recarrega lista

Ponto de entrada: bloco `if __name__ == "__main__"` cria `TkinterDnD.Tk()` quando `tkinterdnd2` está disponível, instancia `MediaRenamer` e inicia `mainloop()`.

---

## Funcionalidades atuais

 - Seleção de pasta (`filedialog.askdirectory`)
 - Listagem em `ttk.Treeview` com nome atual, tipo, tamanho, modificação e prévia
 - Seleção múltipla na árvore; **Selecionar todos** / **Desmarcar todos**
 - Padrão: nome base, número inicial, dígitos (1–8), separador
 - Filtros por categoria (ver abaixo)
 - **Abrir subpastas por padrão**, configurado exclusivamente em Configurações
 - Monitoramento automático configurável, com espera de estabilidade para novos arquivos
 - **LIMPAR** (`clear_workspace`): zera pasta, lista, seleção e prévia
 - Temas **Claro** / **Escuro** (`apply_theme`, estilos ttk customizados)
 - Layout em grid com área de lista expansível; `minsize` 840×640
 - Status: contagem de encontrados, selecionados e tamanho total
 - Busca rápida por nome e abertura por duplo clique
 - Diálogo de confirmação antes da renomeação em massa
 - Tratamento de exceções na renomeação com `messagebox` e reload

---

## Categorias de arquivos suportadas

Arquivo elegível: `path.is_file()` e `path.suffix` não vazio.

Classificação (`file_category`):

- **Fotos** → `PHOTO_EXTENSIONS`
- **Vídeos** → `VIDEO_EXTENSIONS`
- **Áudio** → `AUDIO_EXTENSIONS`
- **Documentos** → `DOCUMENT_EXTENSIONS`
- **Arquivos/Outros** → qualquer outra extensão

Extensões definidas no topo de `media_renamer.py` (lista completa no **README.md**).

## Sistema de filtros

- `filter_type` (`StringVar`) ligado ao `Combobox` com `FILTER_OPTIONS`
- `load_files` itera a pasta; para cada arquivo chama `is_renameable_file` e `matches_filter`
- **Todos**: qualquer arquivo elegível
- Demais filtros: `file_category(suffix) == filter_type`

Ao recarregar, tenta preservar seleção por caminho absoluto; se não havia seleção anterior, seleciona todos os itens da nova lista.

O carregamento inicial inclui imediatamente os arquivos já existentes. Durante o monitoramento automático, um arquivo novo só entra na lista depois de apresentar o mesmo tamanho em duas verificações, reduzindo o risco de listar arquivos ainda em cópia. A atualização preserva a seleção existente e nunca renomeia arquivos por conta própria.

---

## Sistema de renomeação

- `make_new_name(index, path)` → `{base}{sep}{number:0{digits}d}{path.suffix}`
- A lista é reordenada automaticamente conforme `sort_mode`: Nome, Data de criação, Data de modificação ou Tamanho.
- A sequência dos nomes gerados usa a ordem atual dos arquivos selecionados.
- Apenas paths em `selected` entram em `operations`, mas o índice usado é o da lista completa
- Validação: nomes duplicados no lote; destino existente que não seja fonte da operação
- Execução: rename para `. __renamer_tmp_{pid}_{n}{suffix}` depois rename para nome final

Extensão original sempre em `path.suffix`.

---

## Cancelamento / limpeza da pasta

- `clear_workspace`: confirma se `should_confirm_clear()` (arquivos, seleção, pasta ativa ou padrão alterado com pasta)
- Limpa `folder`, `files`, `selected`; `refresh_preview` restaura status inicial
- Não redefine variáveis de padrão de renomeação

Botão **LIMPAR** no rodapé (estilo `Danger.TButton`).

---

## Responsividade

- Janela redimensionável; `main.rowconfigure` com peso na linha da lista
- Colunas da treeview com `minwidth` e scroll vertical/horizontal
- Botões principais fixos no rodapé (`RENOMEAR ARQUIVOS`, **LIMPAR**)

---

## Temas claro / escuro

- `theme_mode`: Claro / Escuro, alterado apenas pelo diálogo Configurações
- `apply_theme` define paleta (background, accent, danger, tree, bordas)
- Estilos: `Primary.TButton`, `Secondary.TButton`, `Danger.TButton`, `Field.TEntry`, `Compact.*`, etc.

---

## Proteção contra conflitos

Descrita em `rename_files`: duplicatas no conjunto de destinos, arquivo existente no disco, pipeline com nomes temporários únicos por PID/contador.

---

## Inclusão de subpastas

- `include_subfolders` False: `Path(folder).glob("*")`
- True: `Path(folder).rglob("*")`
- Apenas arquivos (não diretórios) após filtros

---

## Empacotamento PyInstaller

- Spec: **`media_renamer.spec`** → executável **`MediaRenamer.exe`**, `console=False`
- Comando equivalente:

```bash
python -m pip install -r requirements.txt
python -m PyInstaller --onefile --windowed --name MediaRenamer --clean media_renamer.py
```

Saída: `dist/MediaRenamer.exe`.

Importante para distribuição e manutenção:
- O executável principal de distribuição é `renamer final/MediaRenamer.exe`.
- Após qualquer alteração no código, o processo de geração deve ser repetido e o executável principal deve ser substituído pela nova build.
- Todos os outros `MediaRenamer.exe` que existam dentro do projeto devem refletir a mesma versão mais recente, quando aplicável.

---

## Executar em desenvolvimento

```bash
python media_renamer.py
```

Requer Python com Tkinter no PATH.

---

## Possíveis melhorias futuras

1. Seleção direta de arquivos em pastas diferentes
2. Ícone e metadados de versão no executável
3. Instalador (MSI/Inno Setup)
4. Assinatura digital para distribuição
5. Testes automatizados de UI/filtros (hoje validados manualmente ou via scripts ad hoc)

---

## Orientações para IA / manutenção

1. Leia **`PROJECT_CONTEXT.md`** e **`media_renamer.py`** antes de alterar o projeto.
2. Preserve comportamento existente; prefira diffs pequenos e testáveis.
3. Não recrie o projeto do zero sem necessidade.
4. Ao mudar extensões ou filtros, atualize **README.md** e este arquivo.
5. Após renomear entrypoint ou spec, alinhe documentação e comandos PyInstaller.
