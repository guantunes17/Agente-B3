"""Página 'Configurações' — credenciais de acesso e preferências."""
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog

from gui.styles import COLORS, FONTS, SIZES
from gui.components.card import Card
from gui.components.status_bar import StatusBar


class PaginaConfiguracoes(ctk.CTkFrame):
    """Página de configuração de credenciais e preferências."""

    def __init__(self, master, on_credenciais_salvas=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_credenciais_salvas = on_credenciais_salvas
        self._construir()

    def _construir(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True,
                    padx=SIZES["page_padding_x"], pady=SIZES["page_padding_y"])

        ctk.CTkLabel(scroll, text="Configurações",
                     font=FONTS["page_title"],
                     text_color=COLORS["text_primary"],
                     anchor="w").pack(fill="x")
        ctk.CTkLabel(scroll, text="Credenciais de acesso e preferências",
                     font=FONTS["page_subtitle"],
                     text_color=COLORS["text_secondary"],
                     anchor="w").pack(fill="x", pady=(2, 20))

        from gui.credentials import obter_todas_credenciais
        creds = obter_todas_credenciais()

        card = Card(scroll)
        card.pack(fill="x", pady=(0, 16))
        c = card.content

        # ── Seção B3 / CETIP ──────────────────────────────────────────────
        self._section_title(c, "B3 / CETIP")
        self._entry_b3_usuario = self._campo(c, "Usuário B3", creds.get("b3_usuario", ""))
        self._entry_b3_senha = self._campo(c, "Senha B3", creds.get("b3_senha", ""), show="●")
        self._entry_b3_cert, _ = self._campo_arquivo(c, "Certificado .pfx", creds.get("b3_certificado", ""))

        ctk.CTkLabel(c, text="Suas credenciais ficam salvas com segurança neste computador.",
                     font=FONTS["small"], text_color=COLORS["text_muted"],
                     anchor="w").pack(fill="x", pady=(4, 0))

        self._separador(c)

        # ── Seção UP2DATA ─────────────────────────────────────────────────
        self._section_title(c, "UP2DATA")

        ctk.CTkLabel(c, text="Cloud", font=FONTS["section_title"],
                     text_color=COLORS["primary_600"], anchor="w").pack(fill="x", pady=(4, 0))

        self._entry_up2data_id = self._campo(c, "Client ID", creds.get("up2data_client_id", ""))
        self._entry_up2data_secret = self._campo(c, "Client Secret",
                                                  creds.get("up2data_client_secret", ""), show="●")
        self._entry_up2data_cert, _ = self._campo_arquivo(
            c, "Certificado .pfx (Cloud)", creds.get("up2data_cert_path", "")
        )
        self._entry_up2data_cert_senha = self._campo(
            c, "Senha do certificado", creds.get("up2data_cert_password", ""), show="●"
        )

        ctk.CTkLabel(c, text="Client (software local)", font=FONTS["section_title"],
                     text_color=COLORS["primary_600"], anchor="w").pack(fill="x", pady=(12, 0))

        self._entry_up2data_client_path, _ = self._campo_pasta(
            c, "Diretório de dados", creds.get("up2data_client_path", "")
        )

        self._separador(c)

        # ── Seção ANBIMA Data ─────────────────────────────────────────────
        self._section_title(c, "ANBIMA Data (opcional)")
        self._entry_anbima_id = self._campo(c, "Client ID ANBIMA", creds.get("anbima_client_id", ""))
        self._entry_anbima_secret = self._campo(
            c, "Client Secret ANBIMA", creds.get("anbima_client_secret", ""), show="●"
        )
        ctk.CTkLabel(c, text="Deixe em branco para usar dados públicos da ANBIMA.",
                     font=FONTS["small"], text_color=COLORS["text_muted"],
                     anchor="w").pack(fill="x", pady=(4, 0))

        # ── Botão salvar ──────────────────────────────────────────────────
        ctk.CTkButton(
            scroll, text="Salvar configurações",
            height=SIZES["button_height"],
            corner_radius=SIZES["button_corner_radius"],
            fg_color=COLORS["primary_700"], hover_color=COLORS["primary_600"],
            text_color="white", font=FONTS["button"],
            command=self._salvar,
        ).pack(fill="x", pady=(0, 12))

        self._status_bar = StatusBar(scroll)
        self._status_bar.pack(fill="x")

    # ── Helpers de UI ─────────────────────────────────────────────────────────

    def _section_title(self, parent, texto: str):
        ctk.CTkLabel(
            parent, text=texto.upper(),
            font=FONTS["section_title"],
            text_color=COLORS["primary_700"],
            anchor="w",
        ).pack(fill="x", pady=(8, 4))

    def _separador(self, parent):
        ctk.CTkFrame(parent, fg_color=COLORS["border_light"], height=1).pack(
            fill="x", pady=16
        )

    def _campo(self, parent, label: str, valor: str = "", show: str = "") -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label, font=FONTS["field_label"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x")
        entry = ctk.CTkEntry(
            parent,
            height=SIZES["input_height"],
            corner_radius=SIZES["input_corner_radius"],
            border_color=COLORS["border_medium"],
            show=show,
        )
        if valor:
            entry.insert(0, valor)
        entry.pack(fill="x", pady=(2, 8))
        return entry

    def _campo_arquivo(self, parent, label: str, valor: str = ""):
        ctk.CTkLabel(parent, text=label, font=FONTS["field_label"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x")
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(2, 8))

        entry = ctk.CTkEntry(frame, state="readonly",
                              height=SIZES["input_height"],
                              corner_radius=SIZES["input_corner_radius"],
                              border_color=COLORS["border_medium"],
                              fg_color=COLORS["bg_input"])
        if valor:
            entry.configure(state="normal")
            entry.insert(0, valor)
            entry.configure(state="readonly")
        entry.pack(side="left", fill="x", expand=True)

        def procurar():
            caminho = filedialog.askopenfilename(
                title=f"Selecionar {label}",
                filetypes=[("Certificado PFX", "*.pfx"), ("Todos", "*.*")],
            )
            if caminho:
                entry.configure(state="normal")
                entry.delete(0, "end")
                entry.insert(0, caminho)
                entry.configure(state="readonly")

        ctk.CTkButton(
            frame, text="Procurar", width=80, height=SIZES["input_height"],
            corner_radius=SIZES["input_corner_radius"],
            fg_color="transparent", border_width=1,
            border_color=COLORS["border_medium"],
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_input"],
            font=FONTS["button_sm"],
            command=procurar,
        ).pack(side="left", padx=(8, 0))
        return entry, frame

    def _campo_pasta(self, parent, label: str, valor: str = ""):
        ctk.CTkLabel(parent, text=label, font=FONTS["field_label"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x")
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(2, 8))

        entry = ctk.CTkEntry(frame, state="readonly",
                              height=SIZES["input_height"],
                              corner_radius=SIZES["input_corner_radius"],
                              border_color=COLORS["border_medium"],
                              fg_color=COLORS["bg_input"])
        if valor:
            entry.configure(state="normal")
            entry.insert(0, valor)
            entry.configure(state="readonly")
        entry.pack(side="left", fill="x", expand=True)

        def procurar():
            pasta = filedialog.askdirectory(title=f"Selecionar {label}")
            if pasta:
                entry.configure(state="normal")
                entry.delete(0, "end")
                entry.insert(0, pasta)
                entry.configure(state="readonly")

        ctk.CTkButton(
            frame, text="Procurar", width=80, height=SIZES["input_height"],
            corner_radius=SIZES["input_corner_radius"],
            fg_color="transparent", border_width=1,
            border_color=COLORS["border_medium"],
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_input"],
            font=FONTS["button_sm"],
            command=procurar,
        ).pack(side="left", padx=(8, 0))
        return entry, frame

    def _get_entry(self, entry: ctk.CTkEntry) -> str:
        """Obtém valor de um CTkEntry, mesmo que em estado readonly."""
        try:
            entry.configure(state="normal")
            val = entry.get()
            entry.configure(state="readonly")
            return val
        except Exception:
            return entry.get()

    # ── Salvar ────────────────────────────────────────────────────────────────

    def _salvar(self):
        from gui.credentials import salvar_todas_credenciais

        dados = {
            "b3_usuario": self._entry_b3_usuario.get(),
            "b3_senha": self._entry_b3_senha.get(),
            "b3_certificado": self._get_entry(self._entry_b3_cert),
            "up2data_client_id": self._entry_up2data_id.get(),
            "up2data_client_secret": self._entry_up2data_secret.get(),
            "up2data_cert_path": self._get_entry(self._entry_up2data_cert),
            "up2data_cert_password": self._entry_up2data_cert_senha.get(),
            "up2data_client_path": self._get_entry(self._entry_up2data_client_path),
            "anbima_client_id": self._entry_anbima_id.get(),
            "anbima_client_secret": self._entry_anbima_secret.get(),
        }

        try:
            salvar_todas_credenciais(dados)
            self._status_bar.mostrar_sucesso("Configurações salvas com sucesso.")
            if self.on_credenciais_salvas:
                self.on_credenciais_salvas()
        except Exception as e:
            self._status_bar.mostrar_erro(f"Erro ao salvar: {e}")
