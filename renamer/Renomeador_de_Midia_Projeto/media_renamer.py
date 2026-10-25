import os
import json
import re
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    DND_FILES = None
    TkinterDnD = None

PHOTO_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff",
}
VIDEO_EXTENSIONS = {
    ".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".wmv",
}
AUDIO_EXTENSIONS = {
    ".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg", ".wma",
}
DOCUMENT_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".txt", ".csv", ".zip", ".rar", ".7z",
}
CONFIG_PATH = Path(os.path.expanduser("~/.media_renamer.json"))
FILTER_OPTIONS = [
    "Todos",
    "Fotos",
    "Vídeos",
    "Áudio",
    "Documentos",
    "Arquivos/Outros",
]


class MediaRenamer:
    def __init__(self, root):
        self.root = root
        self.root.title("Renomeador de Mídia")
        self.root.geometry("980x680")
        self.root.minsize(840, 640)
        self.root.resizable(True, True)
        self.root.option_add("*Font", ("Segoe UI", 10))
        self.root.option_add("*TCombobox*Listbox*Font", ("Segoe UI", 10))

        self.config = self.load_config()
        self.folder = tk.StringVar()
        self.base_name = tk.StringVar(value="Arquivo")
        self.start_number = tk.IntVar(value=1)
        self.digits = tk.IntVar(value=3)
        self.separator = tk.StringVar(value="_")
        self.filter_type = tk.StringVar(value="Todos")
        self.include_subfolders = tk.BooleanVar(value=self.config.get("include_subfolders", False))
        self.theme_mode = tk.StringVar(value=self.config.get("theme", "Claro"))
        self.confirm_before_rename = tk.BooleanVar(value=self.config.get("confirm_before_rename", True))
        try:
            configured_interval = int(self.config.get("watch_interval", 1200))
        except (TypeError, ValueError):
            configured_interval = 1200
        self.watch_interval = tk.IntVar(value=max(500, configured_interval))
        self.sort_mode = tk.StringVar(value="Nome")
        self.search_text = tk.StringVar()
        self.separator_choice = tk.StringVar(value="_")
        self.use_date = tk.BooleanVar(value=False)
        self.date_source = tk.StringVar(value="Data de criação")
        self.date_format = tk.StringVar(value="AAAA-MM-DD")
        self.replace_text = tk.StringVar(value="")
        self.replace_with = tk.StringVar(value="")

        self.files = []
        self.selected = set()
        self.hidden_selected = set()
        self.undo_stack = []
        self._updating_tree = False
        self._busy = False
        self._watch_job = None
        self._pending_sizes = {}
        self.selection_summary = None
        self.example_label = None

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.apply_theme()
        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.close_application)
        self._schedule_watch()

    def load_config(self):
        try:
            with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
                config = json.load(config_file)
                return config if isinstance(config, dict) else {}
        except (OSError, ValueError):
            return {}

    def save_config(self):
        try:
            interval = max(500, int(self.watch_interval.get()))
        except (tk.TclError, ValueError):
            interval = 1200
        config = {
            "theme": self.theme_mode.get(),
            "confirm_before_rename": self.confirm_before_rename.get(),
            "watch_interval": interval,
            "include_subfolders": self.include_subfolders.get(),
        }
        try:
            with CONFIG_PATH.open("w", encoding="utf-8") as config_file:
                json.dump(config, config_file, ensure_ascii=True, indent=2)
        except OSError:
            pass

    def build_ui(self):
        main = ttk.Frame(self.root, padding=18)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(5, weight=1)

        header = ttk.Frame(main)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="RENOMEADOR DE MÍDIA",
                  style="Header.TLabel").grid(row=0, column=0, sticky="w")

        ttk.Button(header, text="⚙ Configurações",
               style="Secondary.TButton", command=self.open_settings).grid(
            row=0, column=1, sticky="e")

        folder_frame = ttk.LabelFrame(main, text="Pasta de trabalho", padding=10)
        folder_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        folder_frame.columnconfigure(1, weight=1)

        ttk.Label(folder_frame, text="Pasta:", style="Bold.TLabel").grid(
            row=0, column=0, sticky="w")
        ttk.Entry(folder_frame, textvariable=self.folder, style="Field.TEntry").grid(
            row=0, column=1, sticky="ew", padx=8)
        btn_row = ttk.Frame(folder_frame)
        btn_row.grid(row=0, column=2, sticky="e")
        ttk.Button(btn_row, text="▣ Selecionar pasta",
                   style="Secondary.TButton", command=self.choose_folder).pack(
            side="left", padx=(0, 6))

        options = ttk.LabelFrame(main, text="Padrão de renomeação", padding=12)
        options.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        for col in (1,):
            options.grid_columnconfigure(col, weight=1)

        ttk.Label(options, text="Nome base:", style="Bold.TLabel").grid(
            row=0, column=0, sticky="w")
        ttk.Entry(options, textvariable=self.base_name, style="Field.TEntry").grid(
            row=0, column=1, columnspan=3, padx=(6, 12), sticky="ew")

        ttk.Label(options, text="Nº inicial:", style="Bold.TLabel").grid(
            row=0, column=4, sticky="w")
        ttk.Spinbox(
            options, from_=0, to=999999, textvariable=self.start_number,
            width=7, style="Compact.TSpinbox",
        ).grid(row=0, column=5, padx=(6, 12), sticky="w")

        ttk.Label(options, text="Dígitos:", style="Bold.TLabel").grid(
            row=0, column=6, sticky="w")
        ttk.Spinbox(
            options, from_=1, to=8, textvariable=self.digits,
            width=4, style="Compact.TSpinbox",
        ).grid(row=0, column=7, padx=(6, 12), sticky="w")

        ttk.Label(options, text="Separador:", style="Bold.TLabel").grid(
            row=0, column=8, sticky="w")
        separator_combo = ttk.Combobox(
            options, textvariable=self.separator_choice,
            values=["_", "-", "espaço", "nenhum", "Personalizado"],
            state="readonly", width=13, style="Compact.TCombobox",
        )
        separator_combo.grid(row=0, column=9, padx=(6, 0), sticky="w")
        separator_combo.bind("<<ComboboxSelected>>", self.on_separator_choice)
        ttk.Entry(
            options, textvariable=self.separator, width=5, style="Compact.TEntry",
        ).grid(row=0, column=10, padx=(6, 0), sticky="w")

        ttk.Label(options, text="Filtro:", style="Bold.TLabel").grid(
            row=1, column=0, sticky="w", pady=(12, 0))
        combo = ttk.Combobox(
            options,
            textvariable=self.filter_type,
            values=FILTER_OPTIONS,
            state="readonly",
            width=18,
            style="Compact.TCombobox",
        )
        combo.grid(row=1, column=1, columnspan=2, sticky="w", pady=(12, 0), padx=(6, 0))
        combo.bind("<<ComboboxSelected>>", lambda e: self.load_files())

        ttk.Label(options, text="Ordenar por:", style="Bold.TLabel").grid(
            row=2, column=0, sticky="w", pady=(12, 0))
        sort_combo = ttk.Combobox(
            options,
            textvariable=self.sort_mode,
            values=["Nome", "Data de criação", "Data de modificação", "Tamanho"],
            state="readonly",
            width=18,
            style="Compact.TCombobox",
        )
        sort_combo.grid(row=2, column=1, columnspan=2, sticky="w", pady=(12, 0), padx=(6, 0))
        sort_combo.bind("<<ComboboxSelected>>", lambda event: self.apply_sort())

        ttk.Checkbutton(
            options,
            text="Usar data/hora no nome",
            variable=self.use_date,
            command=self.refresh_preview,
        ).grid(row=2, column=4, columnspan=2, sticky="w", pady=(12, 0), padx=(10, 0))

        ttk.Label(options, text="Formato da data:", style="Bold.TLabel").grid(
            row=2, column=6, sticky="w", pady=(12, 0), padx=(12, 0))
        date_combo = ttk.Combobox(
            options,
            textvariable=self.date_format,
            values=["AAAA-MM-DD", "AAAAMMDD", "AAAA-MM-DD_HH-MM", "AAAA-MM-DD_HHMM", "DD/MM/AAAA"],
            state="readonly",
            width=16,
            style="Compact.TCombobox",
        )
        date_combo.grid(row=2, column=7, columnspan=2, sticky="w", pady=(12, 0), padx=(6, 0))
        date_combo.bind("<<ComboboxSelected>>", lambda event: self.refresh_preview())

        ttk.Label(options, text="Fonte da data:", style="Bold.TLabel").grid(
            row=3, column=0, sticky="w", pady=(10, 0))
        source_combo = ttk.Combobox(
            options,
            textvariable=self.date_source,
            values=["Data de criação", "Data de modificação", "Data atual do sistema"],
            state="readonly",
            width=20,
            style="Compact.TCombobox",
        )
        source_combo.grid(row=3, column=1, columnspan=2, sticky="w", pady=(10, 0), padx=(6, 0))
        source_combo.bind("<<ComboboxSelected>>", lambda event: self.refresh_preview())

        self.example_label = ttk.Label(
            options, text="Exemplo: Arquivo_001.ext", style="Muted.TLabel")
        self.example_label.grid(row=3, column=3, columnspan=6, sticky="w", pady=(10, 0), padx=(12, 0))

        actions = ttk.Frame(main)
        actions.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        actions.columnconfigure(2, weight=1)
        ttk.Button(actions, text="Selecionar todos",
                   style="Secondary.TButton", command=self.select_all).grid(
            row=0, column=0, sticky="w")
        ttk.Button(actions, text="Desmarcar todos",
                   style="Secondary.TButton", command=self.deselect_all).grid(
            row=0, column=1, sticky="w", padx=(6, 0))
        ttk.Label(
            actions,
            text="Clique nos arquivos para selecionar/desselecionar.",
            style="Muted.TLabel",
        ).grid(row=0, column=2, sticky="w", padx=(10, 0))
        self.selection_summary = ttk.Label(
            actions, text="0 de 0 arquivos selecionados", style="Bold.TLabel")
        self.selection_summary.grid(row=0, column=3, sticky="e", padx=(10, 0))

        replace_frame = ttk.LabelFrame(main, text="Substituir texto no nome", padding=8)
        replace_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        replace_frame.columnconfigure(1, weight=1)
        ttk.Label(replace_frame, text="Procurar:", style="Bold.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(replace_frame, textvariable=self.replace_text, style="Field.TEntry").grid(
            row=0, column=1, sticky="ew", padx=(8, 12))
        ttk.Label(replace_frame, text="Substituir por:", style="Bold.TLabel").grid(
            row=0, column=2, sticky="w")
        ttk.Entry(replace_frame, textvariable=self.replace_with, style="Field.TEntry").grid(
            row=0, column=3, sticky="ew", padx=(8, 0))
        ttk.Button(replace_frame, text="Substituir texto",
                   style="Secondary.TButton", command=self.replace_selected_names).grid(
            row=0, column=4, sticky="e", padx=(10, 0))

        list_frame = ttk.Frame(main)
        list_frame.grid(row=5, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)

        search_bar = ttk.Frame(list_frame)
        search_bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        search_bar.columnconfigure(1, weight=1)
        ttk.Label(search_bar, text="⌕ Filtrar arquivos:", style="Bold.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 8))
        self.search_entry = ttk.Entry(search_bar, textvariable=self.search_text,
                          style="Field.TEntry")
        self.search_entry.grid(row=0, column=1, sticky="ew")

        tree_container = ttk.Frame(list_frame)
        tree_container.grid(row=1, column=0, sticky="nsew")
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            tree_container, columns=("old", "type", "size", "modified", "new"),
            show="headings", selectmode="extended", height=10,
        )
        self.tree.heading("old", text="Arquivo atual")
        self.tree.heading("type", text="Tipo")
        self.tree.heading("size", text="Tamanho")
        self.tree.heading("modified", text="Modificado")
        self.tree.heading("new", text="Novo nome (prévia)")
        self.tree.column("old", width=280, minwidth=180, anchor="w")
        self.tree.column("type", width=100, minwidth=80, anchor="w")
        self.tree.column("size", width=95, minwidth=75, anchor="e")
        self.tree.column("modified", width=145, minwidth=120, anchor="center")
        self.tree.column("new", width=280, minwidth=180, anchor="w")

        yscrollbar = ttk.Scrollbar(tree_container, orient="vertical",
                                   command=self.tree.yview)
        xscrollbar = ttk.Scrollbar(tree_container, orient="horizontal",
                                   command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscrollbar.grid(row=0, column=1, sticky="ns")
        xscrollbar.grid(row=1, column=0, sticky="ew")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", self.open_selected_file)
        self.register_drop_target(self.root)
        self.register_drop_target(self.tree)

        bottom = ttk.Frame(main)
        bottom.grid(row=6, column=0, sticky="ew", pady=(10, 0))
        bottom.columnconfigure(0, weight=1)
        self.status = ttk.Label(
            bottom, text="Selecione uma pasta para começar.",
            style="Muted.TLabel",
        )
        self.status.grid(row=0, column=0, sticky="w")

        action_bar = ttk.Frame(bottom)
        action_bar.grid(row=0, column=1, sticky="e")
        self.undo_button = ttk.Button(action_bar, text="↶ DESFAZER",
               style="Secondary.TButton", command=self.undo_last_rename)
        self.undo_button.pack(side="left", padx=(0, 10))
        ttk.Button(action_bar, text="× LIMPAR",
                   style="Danger.TButton", command=self.clear_workspace).pack(
            side="left", padx=(0, 10))
        ttk.Button(action_bar, text="✓ RENOMEAR ARQUIVOS",
                   style="Primary.TButton", command=self.rename_files).pack(side="left")

        for var in (
            self.base_name, self.start_number, self.digits, self.separator,
            self.replace_text, self.replace_with,
        ):
            var.trace_add("write", lambda *args: self.refresh_preview())
        self.search_text.trace_add("write", lambda *args: self.load_files(preserve_selection=True))
        self.root.bind("<Control-f>", lambda event: self.focus_search())
        self.update_undo_button()
        self.refresh_preview()

    def focus_search(self):
        self.search_entry.focus_set()
        return "break"

    def on_separator_choice(self, event=None):
        choice = self.separator_choice.get()
        if choice == "espaço":
            self.separator.set(" ")
        elif choice == "nenhum":
            self.separator.set("")
        elif choice != "Personalizado":
            self.separator.set(choice)
        self.refresh_preview()

    def open_settings(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Configurações")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        frame = ttk.Frame(dialog, padding=18)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)

        settings_theme = tk.StringVar(value=self.theme_mode.get())
        settings_confirm = tk.BooleanVar(value=self.confirm_before_rename.get())
        settings_interval = tk.IntVar(value=self.watch_interval.get())
        settings_subfolders = tk.BooleanVar(value=self.include_subfolders.get())

        ttk.Label(frame, text="Tema:", style="Bold.TLabel").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Combobox(frame, textvariable=settings_theme, values=["Claro", "Escuro"],
                     state="readonly", width=15, style="Compact.TCombobox").grid(
            row=0, column=1, sticky="ew", padx=(14, 0), pady=5)
        ttk.Checkbutton(frame, text="Confirmar antes de renomear",
                        variable=settings_confirm).grid(
            row=1, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Label(frame, text="Atualização automática (ms):",
                  style="Bold.TLabel").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Spinbox(frame, from_=500, to=60000, increment=100,
                    textvariable=settings_interval, width=15,
                    style="Compact.TSpinbox").grid(
            row=2, column=1, sticky="w", padx=(14, 0), pady=5)
        ttk.Checkbutton(frame, text="Abrir subpastas por padrão",
                        variable=settings_subfolders).grid(
            row=3, column=0, columnspan=2, sticky="w", pady=5)
        buttons = ttk.Frame(frame)
        buttons.grid(row=4, column=0, columnspan=2, sticky="e", pady=(14, 0))
        ttk.Button(buttons, text="Cancelar", command=dialog.destroy).pack(side="left", padx=(0, 8))

        def apply_settings():
            try:
                interval = max(500, int(settings_interval.get()))
            except (tk.TclError, ValueError):
                interval = 1200
            self.theme_mode.set(settings_theme.get())
            self.confirm_before_rename.set(settings_confirm.get())
            self.watch_interval.set(interval)
            self.include_subfolders.set(settings_subfolders.get())
            self.apply_theme()
            self.save_config()
            if self.folder.get().strip():
                self.load_files()
            dialog.destroy()

        ttk.Button(buttons, text="Salvar", style="Primary.TButton",
                   command=apply_settings).pack(side="left")

    def format_size(self, size):
        value = float(size)
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if value < 1024 or unit == "TB":
                return f"{value:.0f} {unit}" if unit == "B" else f"{value:.2f} {unit}"
            value /= 1024
        return "0 B"

    def file_type_label(self, path):
        icons = {"Fotos": "▧", "Vídeos": "▶", "Áudio": "♫", "Documentos": "▤", "Arquivos/Outros": "□"}
        category = self.file_category(path.suffix)
        return f"{icons.get(category, '□')} {category}"

    def modified_label(self, path):
        try:
            return datetime.fromtimestamp(path.stat().st_mtime).strftime("%d/%m/%Y %H:%M")
        except OSError:
            return "-"

    def open_selected_file(self, event=None):
        item = self.tree.identify_row(event.y) if event is not None else ""
        if not item or not item.isdigit() or int(item) >= len(self.files):
            return
        path = self.files[int(item)]
        try:
            os.startfile(str(path))
        except (OSError, AttributeError) as exc:
            messagebox.showerror(
                "Não foi possível abrir o arquivo",
                f"Não foi possível abrir '{path.name}' com o aplicativo padrão do Windows.\n\n{exc}",
            )

    def friendly_file_error(self, exc, filename="o arquivo"):
        if isinstance(exc, FileExistsError):
            return f"Não foi possível renomear '{filename}' porque já existe um arquivo com esse nome."
        if isinstance(exc, PermissionError) or getattr(exc, "winerror", None) == 32:
            return f"Não foi possível renomear '{filename}' porque ele está sendo usado por outro programa."
        return f"Não foi possível concluir a operação em '{filename}'. Verifique as permissões da pasta e tente novamente."

    def rename_operations(self, operations, progress=None):
        temporary_operations = []
        for operation_number, (old, new) in enumerate(operations):
            temporary_number = operation_number
            temporary = old.with_name(
                f".__renamer_tmp_{os.getpid()}_{temporary_number}{old.suffix}")
            while temporary.exists():
                temporary_number += 1
                temporary = old.with_name(
                    f".__renamer_tmp_{os.getpid()}_{temporary_number}{old.suffix}")
            old.rename(temporary)
            temporary_operations.append((temporary, new))

        for temporary, new in temporary_operations:
            temporary.rename(new)
            if progress is not None:
                progress[0] += 1

    def register_drop_target(self, widget):
        if DND_FILES is None:
            return
        try:
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self.on_drop)
        except tk.TclError:
            self.dnd_enabled = False

    def apply_theme(self):
        mode = self.theme_mode.get()

        if mode == "Escuro":
            bg = "#1e1f22"
            fg = "#f3f4f6"
            panel = "#2a2d31"
            field = "#2f343a"
            field_border = "#4b5563"
            accent = "#4f8cff"
            accent_dark = "#3b78f2"
            button = "#3a3d42"
            button_border = "#6b7280"
            danger = "#3f2a2a"
            danger_border = "#e57373"
            danger_fg = "#fecaca"
            muted = "#b7bcc6"
            tree_bg = "#23262b"
            tree_fg = "#f5f7fa"
            selected = "#3d5a80"
        else:
            bg = "#eef2f8"
            fg = "#1f2937"
            panel = "#ffffff"
            field = "#ffffff"
            field_border = "#94a3b8"
            accent = "#2563eb"
            accent_dark = "#1d4ed8"
            button = "#f8fafc"
            button_border = "#64748b"
            danger = "#fef2f2"
            danger_border = "#dc2626"
            danger_fg = "#991b1b"
            muted = "#5e6470"
            tree_bg = "#ffffff"
            tree_fg = "#1c2430"
            selected = "#bfdbfe"

        self.root.configure(bg=bg)
        self.style.configure(
            ".", background=bg, foreground=fg, fieldbackground=field, font=("Segoe UI", 10),
        )
        self.style.configure("TFrame", background=bg)
        self.style.configure(
            "TLabelframe", background=bg, borderwidth=1, relief="solid",
            bordercolor=field_border,
        )
        self.style.configure(
            "TLabelframe.Label", background=bg, foreground=fg, font=("Segoe UI", 10, "bold"),
        )
        self.style.configure("TLabel", background=bg, foreground=fg, font=("Segoe UI", 10))
        self.style.configure("Bold.TLabel", background=bg, foreground=fg, font=("Segoe UI", 10, "bold"))
        self.style.configure("Muted.TLabel", background=bg, foreground=muted, font=("Segoe UI", 9, "bold"))
        self.style.configure(
            "Header.TLabel", background=bg, foreground=fg, font=("Segoe UI", 22, "bold"),
        )

        for entry_style in ("TEntry", "Field.TEntry", "Compact.TEntry"):
            self.style.configure(
                entry_style,
                fieldbackground=field,
                foreground=fg,
                background=field,
                borderwidth=1,
                relief="solid",
                padding=(6, 4),
            )
            self.style.map(entry_style, fieldbackground=[("readonly", field)])

        for combo_style in ("TCombobox", "Compact.TCombobox"):
            self.style.configure(
                combo_style,
                fieldbackground=field,
                background=button,
                foreground=fg,
                borderwidth=1,
                relief="solid",
                arrowsize=14,
                padding=(6, 4),
            )

        for spin_style in ("TSpinbox", "Compact.TSpinbox"):
            self.style.configure(
                spin_style,
                fieldbackground=field,
                foreground=fg,
                background=field,
                borderwidth=1,
                relief="solid",
                padding=(4, 4),
            )

        self.style.configure(
            "TButton",
            background=button,
            foreground=fg,
            borderwidth=2,
            padding=(12, 7),
            relief="solid",
            bordercolor=button_border,
        )
        self.style.map(
            "TButton",
            background=[("active", panel), ("pressed", button)],
            foreground=[("active", fg), ("pressed", fg)],
            bordercolor=[("active", accent), ("pressed", accent)],
        )

        self.style.configure(
            "Primary.TButton",
            background=accent,
            foreground="#ffffff",
            borderwidth=2,
            padding=(18, 10),
            relief="solid",
            font=("Segoe UI", 10, "bold"),
            bordercolor=accent_dark,
        )
        self.style.map(
            "Primary.TButton",
            background=[("active", accent_dark), ("pressed", accent)],
            foreground=[("active", "#ffffff"), ("pressed", "#ffffff")],
            bordercolor=[("active", "#1e40af"), ("pressed", accent_dark)],
        )

        self.style.configure(
            "Secondary.TButton",
            background=button,
            foreground=fg,
            borderwidth=2,
            padding=(12, 7),
            relief="solid",
            bordercolor=button_border,
        )
        self.style.map(
            "Secondary.TButton",
            background=[("active", panel), ("pressed", button)],
            foreground=[("active", fg), ("pressed", fg)],
            bordercolor=[("active", accent), ("pressed", button_border)],
        )

        self.style.configure(
            "Danger.TButton",
            background=danger,
            foreground=danger_fg,
            borderwidth=2,
            padding=(12, 7),
            relief="solid",
            font=("Segoe UI", 10, "bold"),
            bordercolor=danger_border,
        )
        self.style.map(
            "Danger.TButton",
            background=[("active", danger_border), ("pressed", danger)],
            foreground=[("active", "#ffffff"), ("pressed", danger_fg)],
            bordercolor=[("active", danger_fg), ("pressed", danger_border)],
        )

        self.style.configure("TCheckbutton", background=bg, foreground=fg, font=("Segoe UI", 10))
        self.style.configure(
            "Treeview",
            background=tree_bg,
            foreground=tree_fg,
            fieldbackground=tree_bg,
            rowheight=28,
            font=("Segoe UI", 10),
            borderwidth=1,
            relief="solid",
        )
        self.style.configure(
            "Treeview.Heading",
            background=panel,
            foreground=fg,
            relief="solid",
            font=("Segoe UI", 10, "bold"),
            borderwidth=1,
        )
        self.style.map(
            "Treeview",
            background=[("selected", selected)],
            foreground=[("selected", fg)],
        )

        if hasattr(self, "status"):
            self.status.configure(style="Muted.TLabel")

    def file_category(self, ext):
        ext = ext.lower()
        if ext in PHOTO_EXTENSIONS:
            return "Fotos"
        if ext in VIDEO_EXTENSIONS:
            return "Vídeos"
        if ext in AUDIO_EXTENSIONS:
            return "Áudio"
        if ext in DOCUMENT_EXTENSIONS:
            return "Documentos"
        return "Arquivos/Outros"

    def is_renameable_file(self, path):
        if not path.is_file():
            return False
        name = path.name
        if name.startswith(".__renamer_tmp_") or name.startswith("~$"):
            return False
        suffix = path.suffix.lower()
        if not suffix:
            return False
        if suffix in {".crdownload", ".part", ".partial", ".download"}:
            return False
        return True

    def matches_filter(self, path):
        category = self.file_category(path.suffix)
        ftype = self.filter_type.get()
        if ftype == "Todos":
            return True
        return category == ftype

    def should_confirm_clear(self):
        if self.files or self.selected:
            return True
        folder = self.folder.get().strip()
        if not folder:
            return False
        pending_settings = (
            self.base_name.get().strip() != "Arquivo"
            or self.start_number.get() != 1
            or self.digits.get() != 3
            or self.separator.get() != "_"
        )
        return pending_settings or bool(folder)

    def clear_workspace(self):
        if self.should_confirm_clear():
            if not messagebox.askyesno(
                "Limpar trabalho atual",
                "Deseja encerrar o trabalho com a pasta atual?\n\n"
                "A lista de arquivos, seleções e prévias serão apagadas. "
                "Você poderá escolher outra pasta sem fechar o programa.",
            ):
                return

        self.folder.set("")
        self.files.clear()
        self.selected.clear()
        self.hidden_selected.clear()
        self._pending_sizes.clear()
        self.refresh_preview()

    def choose_folder(self):
        folder = filedialog.askdirectory(
            title="Escolha a pasta com fotos, vídeos ou outros arquivos",
        )
        if folder:
            self.folder.set(folder)
            self.load_files()

    def load_files(self, auto=False, preserve_selection=False):
        folder = self.folder.get()
        if not folder or not os.path.isdir(folder):
            return

        if auto and self._busy:
            return

        old_selected_paths = {str(p) for p in self.selected}
        if preserve_selection and self.search_text.get().strip():
            self.hidden_selected.update(old_selected_paths)
        elif preserve_selection and not self.search_text.get().strip():
            old_selected_paths.update(str(p) for p in self.hidden_selected)
            self.hidden_selected.clear()
        collected = self._collect_folder_files()
        if auto:
            collected = [p for p in collected if self._file_is_stable(p, already_listed=True)]

        new_signature = self._files_signature(collected)
        old_signature = self._files_signature(self.files)
        if auto and new_signature == old_signature:
            return

        yscroll = self.tree.yview() if auto and hasattr(self, "tree") else None

        self.files = collected
        self.apply_sort(refresh=False)

        self.selected = {p for p in self.files if str(p) in old_selected_paths}
        if not old_selected_paths and not auto and not preserve_selection:
            self.selected = set(self.files)

        self.refresh_preview()
        if yscroll is not None:
            try:
                self.tree.yview_moveto(yscroll[0])
            except tk.TclError:
                pass

    def _file_key(self, path):
        try:
            return str(path.resolve()).lower()
        except OSError:
            return str(path).lower()

    def _file_signature(self, path):
        try:
            stat = path.stat()
            return (self._file_key(path), stat.st_size, stat.st_mtime_ns)
        except OSError:
            return (self._file_key(path), None, None)

    def _files_signature(self, paths):
        return {self._file_signature(path) for path in paths}

    def _collect_folder_files(self):
        folder = self.folder.get()
        files = []
        if not folder or not os.path.isdir(folder):
            return files
        root = Path(folder)
        iterator = root.rglob("*") if self.include_subfolders.get() else root.glob("*")
        for p in iterator:
            try:
                if not self.is_renameable_file(p):
                    continue
            except OSError:
                continue
            if not self.matches_filter(p):
                continue
            search = self.search_text.get().strip().casefold()
            if search and search not in p.name.casefold():
                continue
            files.append(p)
        return files

    def _file_is_stable(self, path, already_listed=False):
        key = self._file_key(path)
        listed_keys = {self._file_key(p) for p in self.files}
        try:
            size = path.stat().st_size
        except OSError:
            self._pending_sizes.pop(key, None)
            return False

        previous = self._pending_sizes.get(key)
        self._pending_sizes[key] = size

        if already_listed and key in listed_keys:
            return True
        if previous is None:
            return key in listed_keys
        return previous == size

    def _schedule_watch(self):
        if self._watch_job is not None:
            try:
                self.root.after_cancel(self._watch_job)
            except tk.TclError:
                pass
        try:
            interval = max(500, int(self.watch_interval.get()))
        except (tk.TclError, ValueError):
            interval = 1200
        self._watch_job = self.root.after(interval, self._poll_folder)

    def close_application(self):
        if self._watch_job is not None:
            try:
                self.root.after_cancel(self._watch_job)
            except tk.TclError:
                pass
            self._watch_job = None
        self.save_config()
        self.root.destroy()

    def _poll_folder(self):
        self._watch_job = None
        try:
            if not self._busy:
                folder = self.folder.get().strip()
                if folder and os.path.isdir(folder):
                    self.load_files(auto=True)
                    live_keys = {self._file_key(p) for p in self._collect_folder_files()}
                    self._pending_sizes = {
                        key: size for key, size in self._pending_sizes.items()
                        if key in live_keys
                    }
        except Exception:
            pass
        self._schedule_watch()

    def _selected_ordered_paths(self):
        return [p for p in self.files if p in self.selected]

    def _number_for_path(self, path, fallback_index):
        start = int(self.start_number.get())
        if not self.selected:
            return start + fallback_index

        selected_in_order = self._selected_ordered_paths()
        if path in self.selected:
            return start + selected_in_order.index(path)
        return start + fallback_index

    def _date_token_for(self, path):
        if not self.use_date.get():
            return ""

        source = self.date_source.get()
        fmt = self.date_format.get()

        try:
            if source == "Data atual do sistema":
                dt = datetime.now()
            else:
                stat = path.stat()
                ts = stat.st_ctime if source == "Data de criação" else stat.st_mtime
                dt = datetime.fromtimestamp(ts)
        except OSError:
            dt = datetime.now()

        mapping = {
            "AAAA-MM-DD": "%Y-%m-%d",
            "AAAAMMDD": "%Y%m%d",
            "AAAA-MM-DD_HH-MM": "%Y-%m-%d_%H-%M",
            "AAAA-MM-DD_HHMM": "%Y-%m-%d_%H%M",
            "DD/MM/AAAA": "%d-%m-%Y",
        }
        return self._safe_name_part(dt.strftime(mapping.get(fmt, "%Y-%m-%d")))

    def _safe_name_part(self, text):
        return re.sub(r'[<>:"/\\|?*]', "-", text)

    def _replace_preview_name(self, candidate_name):
        search = self.replace_text.get().strip()
        repl = self.replace_with.get()
        if not search:
            return candidate_name
        return candidate_name.replace(search, repl)

    def make_new_name(self, index, path):
        base = self.base_name.get().strip() or "Arquivo"
        sep = self.separator.get()
        digits = max(1, int(self.digits.get()))
        number = self._number_for_path(path, index)
        counter = f"{number:0{digits}d}"

        if self.use_date.get():
            date_token = self._date_token_for(path)
            if date_token:
                if base:
                    base_name = f"{base}{sep}{date_token}"
                else:
                    base_name = date_token
                final_name = f"{base_name}{sep}{counter}{path.suffix}"
                return self._replace_preview_name(final_name)

        final_name = f"{base}{sep}{counter}{path.suffix}"
        return self._replace_preview_name(final_name)

    def refresh_preview(self):
        self._updating_tree = True
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)

            selected_order = self._selected_ordered_paths()
            for i, path in enumerate(self.files):
                if path not in self.selected:
                    new_name = path.name
                else:
                    selected_index = selected_order.index(path) if path in self.selected else i
                    new_name = self.make_new_name(selected_index, path)
                try:
                    size = self.format_size(path.stat().st_size)
                except OSError:
                    size = "-"
                self.tree.insert(
                    "", "end", iid=str(i),
                    values=(path.name, self.file_type_label(path), size,
                            self.modified_label(path), new_name),
                )

            self._update_status_summary()

            if self.selection_summary is not None:
                self.selection_summary.config(
                    text=f"{len(self.selected)} de {len(self.files)} arquivos selecionados")
            if self.example_label is not None:
                if self.files:
                    example_path = next(iter(self.files))
                    self.example_label.config(
                        text=f"Exemplo: {self.make_new_name(0, example_path)}")
                else:
                    self.example_label.config(text="Exemplo: Arquivo_001.ext")

            self.tree.selection_set([str(i) for i, p in enumerate(self.files)
                                     if p in self.selected])
        finally:
            self._updating_tree = False
        self.update_undo_button()

    def on_tree_select(self, event=None):
        if self._updating_tree:
            return
        selected_iids = set(self.tree.selection())
        self.selected = {
            self.files[int(i)] for i in selected_iids
            if str(i).isdigit() and int(i) < len(self.files)
        }
        if self.search_text.get().strip():
            visible_paths = set(self.files)
            self.hidden_selected.difference_update(visible_paths)
            self.hidden_selected.update(self.selected)
        selected_order = self._selected_ordered_paths()
        for i, path in enumerate(self.files):
            iid = str(i)
            if not self.tree.exists(iid):
                continue
            if path not in self.selected:
                new_name = path.name
            else:
                selected_index = selected_order.index(path) if path in self.selected else i
                new_name = self.make_new_name(selected_index, path)
            self.tree.set(iid, "new", new_name)
        if self.folder.get().strip():
            self._update_status_summary()

    def _update_status_summary(self):
        if not self.folder.get().strip():
            self.status.config(text="Selecione uma pasta para começar.")
            if self.selection_summary is not None:
                self.selection_summary.config(text="0 de 0 arquivos selecionados")
            return
        total_size = 0
        for path in self.files:
            try:
                total_size += path.stat().st_size
            except OSError:
                pass
        self.status.config(
            text=f"{len(self.files)} arquivo(s) encontrado(s) • "
                 f"{len(self.selected)} selecionado(s) • {self.format_size(total_size)}")
        if self.selection_summary is not None:
            self.selection_summary.config(
                text=f"{len(self.selected)} de {len(self.files)} arquivos selecionados")

    def select_all(self):
        self.selected = set(self.files)
        self.refresh_preview()

    def deselect_all(self):
        self.selected.clear()
        self.hidden_selected.clear()
        self.refresh_preview()

    def apply_sort(self, refresh=True):
        mode = self.sort_mode.get()
        sorters = {
            "Nome": lambda path: (path.name.casefold(),),
            "Data de criação": lambda path: (path.stat().st_ctime, path.name.casefold()),
            "Data de modificação": lambda path: (path.stat().st_mtime, path.name.casefold()),
            "Tamanho": lambda path: (path.stat().st_size, path.name.casefold()),
        }
        sort_key = sorters.get(mode, sorters["Nome"])

        def safe_sort_key(path):
            try:
                return sort_key(path)
            except OSError:
                return (0, path.name.casefold())

        self.files.sort(key=safe_sort_key)
        if refresh:
            self.refresh_preview()

    def update_undo_button(self):
        state = ["!disabled"] if self.undo_stack else ["disabled"]
        try:
            self.undo_button.state(state)
        except tk.TclError:
            pass

    def handle_dropped_paths(self, dropped_paths):
        if not dropped_paths:
            return

        paths = [Path(item) for item in dropped_paths if Path(item).exists()]
        directories = [path for path in paths if path.is_dir()]
        files = [path for path in paths if path.is_file()]

        if directories:
            if len(directories) > 1 or files:
                messagebox.showwarning(
                    "Itens misturados",
                    "Arraste uma única pasta ou arquivos da mesma pasta por vez.",
                )
                return
            self.folder.set(str(directories[0]))
            self.load_files()
            return

        if not files:
            messagebox.showwarning(
                "Item não suportado",
                "O item arrastado não é um arquivo ou pasta acessível.",
            )
            return

        parents = {path.parent.resolve() for path in files}
        if len(parents) != 1:
            messagebox.showwarning(
                "Pastas diferentes",
                "Para carregar vários arquivos, eles precisam estar na mesma pasta.",
            )
            return

        unsupported = [path.name for path in files if not self.is_renameable_file(path)]
        if unsupported:
            messagebox.showwarning(
                "Arquivo não suportado",
                "Estes itens não possuem extensão válida:\n\n"
                + "\n".join(unsupported[:10]),
            )
            files = [path for path in files if self.is_renameable_file(path)]
        if not files:
            return

        self.folder.set(str(files[0].parent))
        self.load_files()
        self.selected = set(files).intersection(self.files)
        self.refresh_preview()

    def on_drop(self, event):
        try:
            data = event.data
        except AttributeError:
            return
        if not data:
            return
        try:
            paths = list(self.root.tk.splitlist(data))
        except tk.TclError:
            paths = [data]
        self.handle_dropped_paths(paths)

    def replace_selected_names(self):
        if not self.selected:
            messagebox.showwarning("Atenção", "Selecione pelo menos um arquivo para substituir o texto no nome.")
            return

        search = self.replace_text.get().strip()
        if not search:
            messagebox.showwarning("Atenção", "Informe o texto a ser procurado antes de substituir.")
            return

        operations = []
        for path in self._selected_ordered_paths():
            stem = path.stem
            new_stem = stem.replace(search, self.replace_with.get())
            new_name = f"{new_stem}{path.suffix}"
            if new_name == path.name:
                continue
            target = path.with_name(new_name)
            if target.exists() and target.resolve() != path.resolve():
                messagebox.showerror("Erro", f"Não foi possível substituir em '{path.name}' porque o destino já existe.")
                return
            operations.append((path, target))

        if not operations:
            messagebox.showinfo("Sem alterações", "Nenhum arquivo corresponde ao texto informado.")
            return

        preview = "\n".join(f"{old.name}  →  {new.name}" for old, new in operations[:12])
        if len(operations) > 12:
            preview += f"\n... e mais {len(operations)-12} arquivo(s)."

        if not messagebox.askyesno(
            "Confirmar substituição",
            f"Você está prestes a substituir o texto em {len(operations)} arquivo(s):\n\n{preview}\n\nContinuar?",
        ):
            return

        self._busy = True
        try:
            self.rename_operations(operations)

            self.undo_stack.append({"operations": operations})
            self.update_undo_button()
            self.selected.clear()
            self.load_files()
            messagebox.showinfo("Concluído", f"Texto substituído em {len(operations)} arquivo(s) com sucesso.")
        except Exception as exc:
            messagebox.showerror(
                "Erro durante a substituição",
                self.friendly_file_error(exc),
            )
            self.load_files()
        finally:
            self._busy = False

    def undo_last_rename(self):
        if not self.undo_stack:
            messagebox.showinfo("Nada para desfazer", "Não existe nenhuma renomeação para desfazer.")
            return

        if not messagebox.askyesno("Desfazer última renomeação", "Deseja restaurar os nomes originais da última operação?"):
            return

        record = self.undo_stack[-1]
        operations = record.get("operations", [])
        if not operations:
            self.update_undo_button()
            return

        self._busy = True
        try:
            for new_path, old_path in [(new, old) for old, new in operations]:
                if old_path.exists():
                    raise FileExistsError(f"O nome original já existe e não pode ser restaurado: {old_path.name}")
                new_path.rename(old_path)
            self.undo_stack.pop()
            self.update_undo_button()
            self.selected.clear()
            self.load_files()
            messagebox.showinfo("Concluído", "A última renomeação foi desfeita com sucesso.")
        except Exception as exc:
            messagebox.showerror(
                "Não foi possível desfazer",
                f"Não foi possível restaurar os nomes anteriores.\n\n"
                f"{self.friendly_file_error(exc)}",
            )
        finally:
            self._busy = False

    def rename_files(self):
        if not self.files:
            messagebox.showwarning("Atenção", "Nenhum arquivo encontrado.")
            return

        if not self.selected:
            messagebox.showwarning("Atenção", "Selecione pelo menos um arquivo.")
            return

        operations = []
        selected_order = self._selected_ordered_paths()
        for i, path in enumerate(selected_order):
            operations.append((path, path.with_name(self.make_new_name(i, path))))

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

        if self.confirm_before_rename.get() and not messagebox.askyesno(
                "Confirmar renomeação",
                f"Você está prestes a renomear {len(operations)} arquivo(s):\n\n{preview}\n\nContinuar?"
        ):
            return

        completed = 0
        self._busy = True
        try:
            progress = [0]
            self.rename_operations(operations, progress)
            completed = progress[0]

            self.undo_stack.append({"operations": operations})
            self.update_undo_button()
            messagebox.showinfo(
                "Concluído",
                f"{len(operations)} arquivo(s) renomeado(s) com sucesso."
            )
            self.selected.clear()
            self.load_files()

        except Exception as exc:
            messagebox.showerror(
                "Erro durante a renomeação",
                f"{self.friendly_file_error(exc)}\n\n"
                f"{completed} de {len(operations)} arquivo(s) foram processados antes da falha."
            )
            self.load_files()
        finally:
            self._busy = False


if __name__ == "__main__":
    root = TkinterDnD.Tk() if TkinterDnD is not None else tk.Tk()
    try:
        root.tk.call("tk", "scaling", 1.1)
    except Exception:
        pass
    app = MediaRenamer(root)
    root.mainloop()
