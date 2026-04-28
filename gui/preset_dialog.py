"""Diálogo de salvar/carregar presets de filtros."""
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

from gui.styles import COLORS, FONTS


class PresetDialog(tk.Toplevel):
    """Janela modal para gerenciamento de presets."""

    def __init__(self, parent, modo: str, filtros_atuais=None, presets_dir: Path = None):
        """
        Args:
            modo: 'salvar' ou 'carregar'
            filtros_atuais: FiltrosConsulta com os filtros atuais (modo salvar)
            presets_dir: Diretório onde os presets são salvos
        """
        super().__init__(parent)
        self.parent = parent
        self.modo = modo
        self.filtros_atuais = filtros_atuais
        self.presets_dir = presets_dir
        self.resultado = None  # FiltrosConsulta carregado (modo carregar)

        self._configurar_janela()
        self._construir_ui()
        self._centralizar()

        self.grab_set()
        self.focus_set()
        self.wait_window()

    def _configurar_janela(self):
        titulo = "Salvar filtros como preset" if self.modo == "salvar" else "Carregar preset"
        self.title(titulo)
        self.resizable(False, False)
        self.configure(bg=COLORS["bg"])

    def _construir_ui(self):
        if self.modo == "salvar":
            self._ui_salvar()
        else:
            self._ui_carregar()

    def _ui_salvar(self):
        frame = tk.Frame(self, bg=COLORS["bg"], padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Nome do preset", font=FONTS["field_label"],
                 bg=COLORS["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")

        self.entry_nome = tk.Entry(frame, font=FONTS["body"], width=35,
                                   relief="solid", bd=1,
                                   highlightthickness=1,
                                   highlightcolor=COLORS["border_active"],
                                   highlightbackground=COLORS["border"])
        self.entry_nome.pack(fill="x", pady=(2, 0))
        self.entry_nome.insert(0, "Ex: LFs Subordinadas A-")
        self.entry_nome.config(fg=COLORS["text_muted"])
        self.entry_nome.bind("<FocusIn>", self._limpar_placeholder)
        self.entry_nome.bind("<FocusOut>", self._restaurar_placeholder)
        self.entry_nome.bind("<Return>", lambda e: self._salvar())

        frame_btns = tk.Frame(frame, bg=COLORS["bg"])
        frame_btns.pack(fill="x", pady=(16, 0))

        btn_cancelar = tk.Button(
            frame_btns, text="Cancelar", font=FONTS["body"],
            bg=COLORS["bg_secondary"], fg=COLORS["text_secondary"],
            relief="solid", bd=1, padx=12, pady=6,
            cursor="hand2", command=self.destroy
        )
        btn_cancelar.pack(side="right", padx=(8, 0))

        btn_salvar = tk.Button(
            frame_btns, text="Salvar", font=FONTS["body"],
            bg=COLORS["primary"], fg="white",
            relief="flat", padx=12, pady=6,
            cursor="hand2", command=self._salvar
        )
        btn_salvar.pack(side="right")

    def _ui_carregar(self):
        frame = tk.Frame(self, bg=COLORS["bg"], padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        presets = []
        if self.presets_dir:
            from config.filters import FiltrosConsulta
            presets = FiltrosConsulta.listar_presets(self.presets_dir)

        if not presets:
            tk.Label(
                frame,
                text="Nenhum preset salvo.\nUse 'Salvar filtros como preset' para criar o primeiro.",
                font=FONTS["body"], bg=COLORS["bg"], fg=COLORS["text_secondary"],
                justify="center"
            ).pack(pady=20)
            tk.Button(
                frame, text="Fechar", font=FONTS["body"],
                bg=COLORS["bg_secondary"], fg=COLORS["text_secondary"],
                relief="solid", bd=1, padx=12, pady=6,
                cursor="hand2", command=self.destroy
            ).pack()
            return

        tk.Label(frame, text=f"Presets disponíveis ({len(presets)})",
                 font=FONTS["field_label"], bg=COLORS["bg"],
                 fg=COLORS["text_secondary"]).pack(anchor="w")

        frame_lista = tk.Frame(frame, bg=COLORS["border"], bd=1, relief="solid")
        frame_lista.pack(fill="both", expand=True, pady=(4, 0))

        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            frame_lista, font=FONTS["body"],
            bg=COLORS["bg"], fg=COLORS["text"],
            selectbackground=COLORS["primary_light"],
            selectforeground=COLORS["info"],
            relief="flat", bd=0,
            yscrollcommand=scrollbar.set,
            height=8, activestyle="none"
        )
        self.listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        self._presets_lista = presets
        for p in presets:
            data = p.get("criado_em", "")[:10]
            self.listbox.insert("end", f"  {p['nome']}  —  {data}")

        if presets:
            self.listbox.selection_set(0)

        frame_btns = tk.Frame(frame, bg=COLORS["bg"])
        frame_btns.pack(fill="x", pady=(16, 0))

        btn_cancelar = tk.Button(
            frame_btns, text="Cancelar", font=FONTS["body"],
            bg=COLORS["bg_secondary"], fg=COLORS["text_secondary"],
            relief="solid", bd=1, padx=12, pady=6,
            cursor="hand2", command=self.destroy
        )
        btn_cancelar.pack(side="right", padx=(8, 0))

        btn_excluir = tk.Button(
            frame_btns, text="Excluir", font=FONTS["body"],
            bg=COLORS["error_bg"], fg=COLORS["error"],
            relief="solid", bd=1, padx=12, pady=6,
            cursor="hand2", command=self._excluir
        )
        btn_excluir.pack(side="right", padx=(8, 0))

        btn_carregar = tk.Button(
            frame_btns, text="Carregar", font=FONTS["body"],
            bg=COLORS["primary"], fg="white",
            relief="flat", padx=12, pady=6,
            cursor="hand2", command=self._carregar
        )
        btn_carregar.pack(side="right")

    def _limpar_placeholder(self, event):
        if self.entry_nome.get() == "Ex: LFs Subordinadas A-":
            self.entry_nome.delete(0, "end")
            self.entry_nome.config(fg=COLORS["text"])

    def _restaurar_placeholder(self, event):
        if not self.entry_nome.get().strip():
            self.entry_nome.insert(0, "Ex: LFs Subordinadas A-")
            self.entry_nome.config(fg=COLORS["text_muted"])

    def _salvar(self):
        nome = self.entry_nome.get().strip()
        if not nome or nome == "Ex: LFs Subordinadas A-":
            messagebox.showwarning("Nome inválido", "Digite um nome para o preset.", parent=self)
            return

        if self.presets_dir:
            arquivo = self.presets_dir / f"{nome.replace(' ', '_').lower()}.json"
            if arquivo.exists():
                if not messagebox.askyesno(
                    "Sobrescrever?",
                    f"Já existe um preset com o nome '{nome}'.\nDeseja sobrescrever?",
                    parent=self
                ):
                    return

        try:
            caminho = self.filtros_atuais.salvar_preset(nome, self.presets_dir)
            messagebox.showinfo("Preset salvo", f"Preset '{nome}' salvo com sucesso.", parent=self)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro ao salvar", f"Não foi possível salvar o preset.\n{e}", parent=self)

    def _carregar(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Nenhum selecionado", "Selecione um preset para carregar.", parent=self)
            return

        idx = sel[0]
        preset_info = self._presets_lista[idx]
        try:
            from config.filters import FiltrosConsulta
            filtros, _ = FiltrosConsulta.carregar_preset(Path(preset_info["arquivo"]))
            self.resultado = filtros
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro ao carregar", f"Não foi possível carregar o preset.\n{e}", parent=self)

    def _excluir(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Nenhum selecionado", "Selecione um preset para excluir.", parent=self)
            return

        idx = sel[0]
        preset_info = self._presets_lista[idx]
        nome = preset_info["nome"]

        if not messagebox.askyesno(
            "Confirmar exclusão",
            f"Deseja excluir o preset '{nome}'?",
            parent=self
        ):
            return

        try:
            Path(preset_info["arquivo"]).unlink()
            self.listbox.delete(idx)
            self._presets_lista.pop(idx)
        except Exception as e:
            messagebox.showerror("Erro ao excluir", f"Não foi possível excluir o preset.\n{e}", parent=self)

    def _centralizar(self):
        self.update_idletasks()
        w = self.winfo_width() or 400
        h = self.winfo_height() or 300
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")
