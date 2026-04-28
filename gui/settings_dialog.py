"""Diálogo de configurações e gerenciamento de credenciais."""
import tkinter as tk
from tkinter import messagebox, filedialog
from pathlib import Path

from gui.styles import COLORS, FONTS
from gui.credentials import (
    obter_todas_credenciais, salvar_todas_credenciais,
    salvar_credencial, obter_credencial,
    tem_credenciais_up2data_cloud, tem_credenciais_up2data_client,
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

        # ── Seção UP2DATA ─────────────────────────────────────────────────────
        self._secao(frame_main, "UP2DATA (fonte oficial B3)")

        # Nota informativa
        frame_nota = tk.Frame(frame_main, bg=COLORS["info_bg"], padx=10, pady=8)
        frame_nota.pack(fill="x", pady=(0, 10))
        tk.Label(
            frame_nota,
            text=(
                "O UP2DATA é a fonte oficial da B3 para dados de Letras Financeiras.\n"
                "Configure abaixo as credenciais Cloud e/ou o caminho do Client."
            ),
            font=FONTS["small"],
            bg=COLORS["info_bg"], fg=COLORS["info"],
            justify="left", wraplength=400,
        ).pack(anchor="w")

        # Sub-seção Cloud
        tk.Label(frame_main, text="Cloud (API + Azure Blob Storage)",
                 font=FONTS["field_label"], bg=COLORS["bg"],
                 fg=COLORS["text_secondary"]).pack(anchor="w", pady=(4, 0))

        self._campo(frame_main, "Client ID", "entry_up2data_client_id")
        self._campo(frame_main, "Client Secret", "entry_up2data_client_secret", mostrar="*")

        # Certificado .pfx UP2DATA
        frame_pfx_up2 = tk.Frame(frame_main, bg=COLORS["bg"])
        frame_pfx_up2.pack(fill="x", pady=(6, 0))
        tk.Label(frame_pfx_up2, text="Certificado .pfx", font=FONTS["field_label"],
                 bg=COLORS["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        frame_pfx_up2_row = tk.Frame(frame_pfx_up2, bg=COLORS["bg"])
        frame_pfx_up2_row.pack(fill="x", pady=(2, 0))
        self.entry_up2data_cert_path = tk.Entry(
            frame_pfx_up2_row, font=FONTS["body"], relief="solid", bd=1,
            highlightthickness=1, highlightcolor=COLORS["border_active"],
            highlightbackground=COLORS["border"],
        )
        self.entry_up2data_cert_path.pack(side="left", fill="x", expand=True)
        tk.Button(
            frame_pfx_up2_row, text="Procurar",
            font=FONTS["small"], bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"], relief="solid", bd=1,
            padx=8, pady=4, cursor="hand2",
            command=self._escolher_pfx_up2data,
        ).pack(side="left", padx=(6, 0))

        self._campo(frame_main, "Senha do certificado", "entry_up2data_cert_password", mostrar="*")

        btn_testar_cloud = tk.Button(
            frame_main, text="Testar conexão Cloud",
            font=FONTS["small"], bg=COLORS["info_bg"],
            fg=COLORS["info"], relief="solid", bd=1,
            padx=10, pady=4, cursor="hand2",
            command=self._testar_up2data_cloud,
        )
        btn_testar_cloud.pack(anchor="w", pady=(8, 0))
        self.label_status_up2data = tk.Label(
            frame_main, text="", font=FONTS["small"],
            bg=COLORS["bg"], fg=COLORS["text_secondary"],
        )
        self.label_status_up2data.pack(anchor="w")

        # Sub-seção Client (local)
        tk.Label(frame_main, text="Client (diretório local)",
                 font=FONTS["field_label"], bg=COLORS["bg"],
                 fg=COLORS["text_secondary"]).pack(anchor="w", pady=(12, 0))

        frame_dir = tk.Frame(frame_main, bg=COLORS["bg"])
        frame_dir.pack(fill="x", pady=(2, 0))
        self.entry_up2data_client_path = tk.Entry(
            frame_dir, font=FONTS["body"], relief="solid", bd=1,
            highlightthickness=1, highlightcolor=COLORS["border_active"],
            highlightbackground=COLORS["border"],
        )
        self.entry_up2data_client_path.pack(side="left", fill="x", expand=True)
        tk.Button(
            frame_dir, text="Procurar pasta",
            font=FONTS["small"], bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"], relief="solid", bd=1,
            padx=8, pady=4, cursor="hand2",
            command=self._escolher_dir_up2data,
        ).pack(side="left", padx=(6, 0))

        tk.Button(
            frame_main, text="Verificar diretório",
            font=FONTS["small"], bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"], relief="solid", bd=1,
            padx=10, pady=4, cursor="hand2",
            command=self._verificar_dir_up2data,
        ).pack(anchor="w", pady=(8, 0))

        # Pill de status UP2DATA
        self.label_up2data_status_pill = tk.Label(
            frame_main, text="", font=FONTS["small"],
            padx=8, pady=3, bg=COLORS["bg_secondary"], fg=COLORS["text_muted"],
        )
        self.label_up2data_status_pill.pack(anchor="w", pady=(4, 0))
        self._atualizar_pill_up2data()

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
        self.entry_up2data_client_id.insert(0, creds.get("up2data_client_id", ""))
        self.entry_up2data_client_secret.insert(0, creds.get("up2data_client_secret", ""))
        self.entry_up2data_cert_path.insert(0, creds.get("up2data_cert_path", ""))
        self.entry_up2data_cert_password.insert(0, creds.get("up2data_cert_password", ""))
        self.entry_up2data_client_path.insert(0, creds.get("up2data_client_path", ""))

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

    def _escolher_pfx_up2data(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar certificado .pfx (UP2DATA)",
            filetypes=[("Certificados PFX", "*.pfx"), ("Todos os arquivos", "*.*")],
            parent=self,
        )
        if caminho:
            self.entry_up2data_cert_path.delete(0, "end")
            self.entry_up2data_cert_path.insert(0, caminho)

    def _escolher_dir_up2data(self):
        pasta = filedialog.askdirectory(
            title="Selecionar diretório do UP2DATA Client", parent=self
        )
        if pasta:
            self.entry_up2data_client_path.delete(0, "end")
            self.entry_up2data_client_path.insert(0, pasta)
            self._atualizar_pill_up2data()

    def _testar_up2data_cloud(self):
        self.label_status_up2data.config(
            text="Teste de conexão disponível apenas com credenciais válidas contratadas.",
            fg=COLORS["text_secondary"],
        )

    def _verificar_dir_up2data(self):
        pasta = self.entry_up2data_client_path.get().strip()
        if not pasta:
            self.label_status_up2data.config(
                text="Informe o diretório do UP2DATA Client.", fg=COLORS["warning"]
            )
            return
        p = Path(pasta)
        if not p.exists():
            self.label_status_up2data.config(
                text=f"Diretório não encontrado: {pasta}", fg=COLORS["error"]
            )
        else:
            subdirs = [d.name for d in p.iterdir() if d.is_dir()]
            if subdirs:
                self.label_status_up2data.config(
                    text=f"Diretório válido — {len(subdirs)} pasta(s) encontrada(s): {', '.join(subdirs[:4])}",
                    fg=COLORS["success"],
                )
            else:
                self.label_status_up2data.config(
                    text="Diretório existe mas está vazio ou sem subpastas.",
                    fg=COLORS["warning"],
                )

    def _atualizar_pill_up2data(self):
        cloud = tem_credenciais_up2data_cloud()
        client = tem_credenciais_up2data_client()
        if cloud and client:
            texto = "● UP2DATA — Cloud + Client configurados"
            bg, fg = COLORS["success_bg"], COLORS["success"]
        elif cloud:
            texto = "● UP2DATA — Cloud configurado"
            bg, fg = COLORS["success_bg"], COLORS["success"]
        elif client:
            texto = "● UP2DATA — Client configurado"
            bg, fg = COLORS["success_bg"], COLORS["success"]
        else:
            texto = "● UP2DATA — não configurado"
            bg, fg = COLORS["bg_secondary"], COLORS["text_muted"]
        self.label_up2data_status_pill.config(text=texto, bg=bg, fg=fg)

    def _salvar(self):
        dados = {
            "b3_usuario": self.entry_b3_usuario.get().strip(),
            "b3_senha": self.entry_b3_senha.get().strip(),
            "b3_certificado": self.entry_b3_pfx.get().strip(),
            "anbima_client_id": self.entry_anbima_client_id.get().strip(),
            "anbima_client_secret": self.entry_anbima_secret.get().strip(),
            "up2data_client_id": self.entry_up2data_client_id.get().strip(),
            "up2data_client_secret": self.entry_up2data_client_secret.get().strip(),
            "up2data_cert_path": self.entry_up2data_cert_path.get().strip(),
            "up2data_cert_password": self.entry_up2data_cert_password.get().strip(),
            "up2data_client_path": self.entry_up2data_client_path.get().strip(),
        }
        try:
            salvar_todas_credenciais(dados)
            messagebox.showinfo("Salvo", "Credenciais salvas com sucesso.", parent=self)
            self.destroy()
        except Exception:
            messagebox.showerror("Erro ao salvar",
                                 "Não foi possível salvar as credenciais.", parent=self)

    def _centralizar(self):
        self.update_idletasks()
        w = self.winfo_width() or 480
        h = self.winfo_height() or 500
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")
