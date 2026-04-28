"""Diálogo de configurações e gerenciamento de credenciais."""
import tkinter as tk
from tkinter import messagebox, filedialog

from gui.styles import COLORS, FONTS
from gui.credentials import (
    obter_todas_credenciais, salvar_todas_credenciais,
    salvar_credencial, obter_credencial
)


class SettingsDialog(tk.Toplevel):
    """Janela modal de configurações com seções B3 e ANBIMA."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self._configurar_janela()
        self._construir_ui()
        self._carregar_credenciais()
        self._centralizar()

        self.grab_set()
        self.focus_set()
        self.wait_window()

    def _configurar_janela(self):
        self.title("Configurações — Credenciais de Acesso")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg"])

    def _construir_ui(self):
        frame_main = tk.Frame(self, bg=COLORS["bg"], padx=24, pady=20)
        frame_main.pack(fill="both", expand=True)

        # ── Seção B3 ─────────────────────────────────────────────────────────
        self._secao(frame_main, "Credenciais B3 (RJLF)")

        self._campo(frame_main, "Usuário B3", "entry_b3_usuario")
        self._campo(frame_main, "Senha B3", "entry_b3_senha", mostrar="*")

        frame_pfx = tk.Frame(frame_main, bg=COLORS["bg"])
        frame_pfx.pack(fill="x", pady=(6, 0))

        tk.Label(frame_pfx, text="Certificado .pfx", font=FONTS["field_label"],
                 bg=COLORS["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")

        frame_pfx_row = tk.Frame(frame_pfx, bg=COLORS["bg"])
        frame_pfx_row.pack(fill="x", pady=(2, 0))

        self.entry_b3_pfx = tk.Entry(frame_pfx_row, font=FONTS["body"],
                                     relief="solid", bd=1,
                                     highlightthickness=1,
                                     highlightcolor=COLORS["border_active"],
                                     highlightbackground=COLORS["border"])
        self.entry_b3_pfx.pack(side="left", fill="x", expand=True)

        tk.Button(frame_pfx_row, text="Escolher arquivo...",
                  font=FONTS["small"], bg=COLORS["bg_secondary"],
                  fg=COLORS["text_secondary"], relief="solid", bd=1,
                  padx=8, pady=4, cursor="hand2",
                  command=self._escolher_pfx).pack(side="left", padx=(6, 0))

        btn_testar = tk.Button(
            frame_main, text="Testar conexão B3",
            font=FONTS["small"], bg=COLORS["info_bg"],
            fg=COLORS["info"], relief="solid", bd=1,
            padx=10, pady=4, cursor="hand2",
            command=self._testar_b3
        )
        btn_testar.pack(anchor="w", pady=(10, 0))

        self.label_status_b3 = tk.Label(frame_main, text="", font=FONTS["small"],
                                        bg=COLORS["bg"], fg=COLORS["text_secondary"])
        self.label_status_b3.pack(anchor="w")

        # Separador
        tk.Frame(frame_main, bg=COLORS["border"], height=1).pack(fill="x", pady=16)

        # ── Seção ANBIMA ──────────────────────────────────────────────────────
        self._secao(frame_main, "Credenciais ANBIMA Data")

        self._campo(frame_main, "Client ID", "entry_anbima_client_id")
        self._campo(frame_main, "Client Secret", "entry_anbima_secret", mostrar="*")

        # Separador
        tk.Frame(frame_main, bg=COLORS["border"], height=1).pack(fill="x", pady=16)

        # ── Botões ────────────────────────────────────────────────────────────
        frame_btns = tk.Frame(frame_main, bg=COLORS["bg"])
        frame_btns.pack(fill="x")

        tk.Button(frame_btns, text="Cancelar", font=FONTS["body"],
                  bg=COLORS["bg_secondary"], fg=COLORS["text_secondary"],
                  relief="solid", bd=1, padx=12, pady=6,
                  cursor="hand2", command=self.destroy).pack(side="right", padx=(8, 0))

        tk.Button(frame_btns, text="Salvar credenciais", font=FONTS["body"],
                  bg=COLORS["primary"], fg="white",
                  relief="flat", padx=12, pady=6,
                  cursor="hand2", command=self._salvar).pack(side="right")

    def _secao(self, parent, titulo: str):
        tk.Label(parent, text=titulo, font=FONTS["subtitle"],
                 bg=COLORS["bg"], fg=COLORS["primary"]).pack(anchor="w", pady=(0, 8))

    def _campo(self, parent, label: str, attr: str, mostrar: str = ""):
        tk.Label(parent, text=label, font=FONTS["field_label"],
                 bg=COLORS["bg"], fg=COLORS["text_secondary"]).pack(anchor="w", pady=(6, 0))
        entry = tk.Entry(parent, font=FONTS["body"], show=mostrar,
                         relief="solid", bd=1,
                         highlightthickness=1,
                         highlightcolor=COLORS["border_active"],
                         highlightbackground=COLORS["border"])
        entry.pack(fill="x", pady=(2, 0))
        setattr(self, attr, entry)

    def _carregar_credenciais(self):
        creds = obter_todas_credenciais()
        self.entry_b3_usuario.insert(0, creds.get("b3_usuario", ""))
        self.entry_b3_senha.insert(0, creds.get("b3_senha", ""))
        self.entry_b3_pfx.insert(0, creds.get("b3_certificado", ""))
        self.entry_anbima_client_id.insert(0, creds.get("anbima_client_id", ""))
        self.entry_anbima_secret.insert(0, creds.get("anbima_client_secret", ""))

    def _escolher_pfx(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar certificado .pfx",
            filetypes=[("Certificados PFX", "*.pfx"), ("Todos os arquivos", "*.*")],
            parent=self
        )
        if caminho:
            self.entry_b3_pfx.delete(0, "end")
            self.entry_b3_pfx.insert(0, caminho)

    def _testar_b3(self):
        self.label_status_b3.config(
            text="Testando... (conexão real disponível apenas com credenciais válidas)",
            fg=COLORS["text_secondary"]
        )

    def _salvar(self):
        dados = {
            "b3_usuario": self.entry_b3_usuario.get().strip(),
            "b3_senha": self.entry_b3_senha.get().strip(),
            "b3_certificado": self.entry_b3_pfx.get().strip(),
            "anbima_client_id": self.entry_anbima_client_id.get().strip(),
            "anbima_client_secret": self.entry_anbima_secret.get().strip(),
        }
        try:
            salvar_todas_credenciais(dados)
            messagebox.showinfo("Salvo", "Credenciais salvas com sucesso.", parent=self)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro ao salvar",
                                 "Não foi possível salvar as credenciais.", parent=self)

    def _centralizar(self):
        self.update_idletasks()
        w = self.winfo_width() or 480
        h = self.winfo_height() or 500
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")
