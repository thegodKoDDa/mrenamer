import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from datetime import datetime

MEDIA_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff",
    ".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".wmv"
}

class MediaRenamer:
    def __init__(self, root):
        self.root = root
        self.root.title("Renomeador de Mídia")
        self.root.geometry("900x650")
        self.root.minsize(760, 560)

        self.folder = tk.StringVar()
        self.base_name = tk.StringVar(value="Arquivo")
        self.start_number = tk.IntVar(value=1)
        self.digits = tk.IntVar(value=3)
        self.separator = tk.StringVar(value="_")
        self.filter_type = tk.StringVar(value="Todos")
        self.include_subfolders = tk.BooleanVar(value=False)

        self.files = []
        self.selected = set()

        self.build_ui()

    def build_ui(self):
        main = ttk.Frame(self.root, padding=15)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="RENOMEADOR DE MÍDIA",
                  font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 12))

        folder_frame = ttk.Frame(main)
        folder_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(folder_frame, text="Pasta:").pack(side="left")
        ttk.Entry(folder_frame, textvariable=self.folder).pack(
            side="left", fill="x", expand=True, padx=8)
        ttk.Button(folder_frame, text="Selecionar pasta",
                   command=self.choose_folder).pack(side="left")

        options = ttk.LabelFrame(main, text="Padrão de renomeação", padding=10)
        options.pack(fill="x", pady=(0, 10))

        ttk.Label(options, text="Nome base:").grid(row=0, column=0, sticky="w")
        ttk.Entry(options, textvariable=self.base_name, width=24).grid(row=0, column=1, padx=6, sticky="w")

        ttk.Label(options, text="Nº inicial:").grid(row=0, column=2, padx=(15, 0), sticky="w")
        ttk.Spinbox(options, from_=0, to=999999, textvariable=self.start_number,
                    width=8).grid(row=0, column=3, padx=6, sticky="w")

        ttk.Label(options, text="Dígitos:").grid(row=0, column=4, padx=(15, 0), sticky="w")
        ttk.Spinbox(options, from_=1, to=8, textvariable=self.digits,
                    width=6).grid(row=0, column=5, padx=6, sticky="w")

        ttk.Label(options, text="Separador:").grid(row=0, column=6, padx=(15, 0), sticky="w")
        ttk.Entry(options, textvariable=self.separator, width=5).grid(row=0, column=7, padx=6, sticky="w")

        ttk.Label(options, text="Filtro:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        combo = ttk.Combobox(options, textvariable=self.filter_type,
                             values=["Todos", "Fotos", "Vídeos"], state="readonly", width=12)
        combo.grid(row=1, column=1, sticky="w", pady=(10, 0))
        combo.bind("<<ComboboxSelected>>", lambda e: self.load_files())

        ttk.Checkbutton(options, text="Incluir subpastas",
                        variable=self.include_subfolders,
                        command=self.load_files).grid(row=1, column=2, columnspan=2,
                                                      padx=(15, 0), sticky="w", pady=(10, 0))

        ttk.Button(options, text="Atualizar lista",
                   command=self.load_files).grid(row=1, column=7, pady=(10, 0), sticky="e")

        actions = ttk.Frame(main)
        actions.pack(fill="x", pady=(0, 8))
        ttk.Button(actions, text="Selecionar todos",
                   command=self.select_all).pack(side="left")
        ttk.Button(actions, text="Desmarcar todos",
                   command=self.deselect_all).pack(side="left", padx=6)
        ttk.Label(actions, text="Clique nos arquivos para selecionar/desselecionar.",
                  foreground="#666").pack(side="left", padx=10)

        list_frame = ttk.Frame(main)
        list_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(list_frame, columns=("old", "new"),
                                 show="headings", selectmode="extended")
        self.tree.heading("old", text="Arquivo atual")
        self.tree.heading("new", text="Novo nome (prévia)")
        self.tree.column("old", width=390)
        self.tree.column("new", width=390)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical",
                                  command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        bottom = ttk.Frame(main)
        bottom.pack(fill="x", pady=(10, 0))

        self.status = ttk.Label(bottom, text="Selecione uma pasta para começar.")
        self.status.pack(side="left")

        ttk.Button(bottom, text="RENOMEAR ARQUIVOS",
                   command=self.rename_files).pack(side="right")

        # Atualiza a prévia quando o usuário altera opções
        for var in (self.base_name, self.start_number, self.digits, self.separator):
            var.trace_add("write", lambda *args: self.refresh_preview())

    def choose_folder(self):
        folder = filedialog.askdirectory(title="Escolha a pasta com as fotos/vídeos")
        if folder:
            self.folder.set(folder)
            self.load_files()

    def is_photo(self, ext):
        return ext.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"}

    def is_video(self, ext):
        return ext.lower() in {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".wmv"}

    def load_files(self):
        folder = self.folder.get()
        if not folder or not os.path.isdir(folder):
            return

        old_selected_paths = {str(p) for p in self.selected}
        self.files.clear()

        root = Path(folder)
        iterator = root.rglob("*") if self.include_subfolders.get() else root.glob("*")

        for p in iterator:
            if not p.is_file() or p.suffix.lower() not in MEDIA_EXTENSIONS:
                continue

            ftype = self.filter_type.get()
            if ftype == "Fotos" and not self.is_photo(p.suffix):
                continue
            if ftype == "Vídeos" and not self.is_video(p.suffix):
                continue

            self.files.append(p)

        # Ordenação natural por nome
        self.files.sort(key=lambda p: p.name.lower())

        self.selected = {p for p in self.files if str(p) in old_selected_paths}
        if not old_selected_paths:
            self.selected = set(self.files)

        self.refresh_preview()

    def make_new_name(self, index, path):
        base = self.base_name.get().strip() or "Arquivo"
        sep = self.separator.get()
        digits = max(1, int(self.digits.get()))
        number = int(self.start_number.get()) + index
        return f"{base}{sep}{number:0{digits}d}{path.suffix}"

    def refresh_preview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, path in enumerate(self.files):
            new_name = self.make_new_name(i, path)
            self.tree.insert("", "end", iid=str(i),
                             values=(path.name, new_name))

        self.status.config(
            text=f"{len(self.files)} arquivo(s) encontrado(s) • "
                 f"{len(self.selected)} selecionado(s)"
        )

        # Seleção visual
        self.tree.selection_set([str(i) for i, p in enumerate(self.files)
                                 if p in self.selected])

    def on_tree_select(self, event=None):
        selected_iids = set(self.tree.selection())
        self.selected = {self.files[int(i)] for i in selected_iids}
        self.status.config(
            text=f"{len(self.files)} arquivo(s) encontrado(s) • "
                 f"{len(self.selected)} selecionado(s)"
        )

    def select_all(self):
        self.selected = set(self.files)
        self.refresh_preview()

    def deselect_all(self):
        self.selected.clear()
        self.refresh_preview()

    def rename_files(self):
        if not self.files:
            messagebox.showwarning("Atenção", "Nenhum arquivo encontrado.")
            return

        if not self.selected:
            messagebox.showwarning("Atenção", "Selecione pelo menos um arquivo.")
            return

        # Mantém a numeração baseada na ordem original da lista.
        operations = []
        for i, path in enumerate(self.files):
            if path in self.selected:
                operations.append((path, path.with_name(self.make_new_name(i, path))))

        # Evita colisões e renomeações que possam sobrescrever arquivos.
        targets = [new for _, new in operations]
        if len(set(map(str.lower, map(str, targets)))) != len(targets):
            messagebox.showerror("Erro", "O padrão gera nomes duplicados.")
            return

        source_set = {p.resolve() for p, _ in operations}
        for old, new in operations:
            if new.exists() and new.resolve() not in source_set:
                messagebox.showerror(
                    "Erro",
                    f"O arquivo já existe e não será sobrescrito:\n\n{new.name}"
                )
                return

        preview = "\n".join(f"{old.name}  →  {new.name}" for old, new in operations[:12])
        if len(operations) > 12:
            preview += f"\n... e mais {len(operations)-12} arquivo(s)."

        if not messagebox.askyesno(
            "Confirmar renomeação",
            f"Você está prestes a renomear {len(operations)} arquivo(s):\n\n{preview}\n\nContinuar?"
        ):
            return

        # Usa nomes temporários para permitir trocas e evitar colisões entre arquivos.
        temp_ops = []
        try:
            for n, (old, new) in enumerate(operations):
                temp = old.with_name(f".__renamer_tmp_{os.getpid()}_{n}{old.suffix}")
                while temp.exists():
                    n += 1
                    temp = old.with_name(f".__renamer_tmp_{os.getpid()}_{n}{old.suffix}")
                old.rename(temp)
                temp_ops.append((temp, new))

            for temp, new in temp_ops:
                temp.rename(new)

            messagebox.showinfo(
                "Concluído",
                f"{len(operations)} arquivo(s) renomeado(s) com sucesso."
            )
            self.selected.clear()
            self.load_files()

        except Exception as exc:
            messagebox.showerror(
                "Erro durante a renomeação",
                f"Não foi possível concluir a operação.\n\n{exc}\n\n"
                "Verifique se algum arquivo está aberto ou se você tem permissão na pasta."
            )
            self.load_files()

if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.tk.call("tk", "scaling", 1.1)
    except Exception:
        pass
    app = MediaRenamer(root)
    root.mainloop()
