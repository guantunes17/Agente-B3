"""
Sidebar fixa do Agente B3.
Contém: logo, navegação entre páginas, indicadores de status das fontes.
"""
import customtkinter as ctk
from gui.styles import COLORS, FONTS, SIZES


_ITENS_NAV = [
    ("gerar",        "Gerar relatório",  COLORS["dot_gerar"]),
    ("historico",    "Histórico",        COLORS["dot_historico"]),
    ("agendamento",  "Agendamento",      COLORS["dot_agenda"]),
    ("configuracoes","Configurações",    COLORS["dot_config"]),
]


class Sidebar(ctk.CTkFrame):
    """Sidebar com logo, navegação e status das fontes de dados."""

    def __init__(self, master, on_navegar=None, **kwargs):
        super().__init__(
            master,
            width=SIZES["sidebar_width"],
            fg_color=COLORS["sidebar_bg"],
            corner_radius=0,
            **kwargs,
        )
        self.on_navegar = on_navegar
        self._ativo = "gerar"
        self._item_frames: dict[str, ctk.CTkFrame] = {}
        self._item_labels: dict[str, ctk.CTkLabel] = {}

        self.pack_propagate(False)
        self._construir()

    def _construir(self):
        # ── Header com logo ───────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(20, 0))

        try:
            from gui.logo import gerar_ctk_image
            logo_img = gerar_ctk_image(tamanho_display=32)
            ctk.CTkLabel(header, image=logo_img, text="").pack(side="left")
        except Exception:
            ctk.CTkLabel(header, text="B3", font=("Arial", 16, "bold"),
                         text_color=COLORS["accent_teal"]).pack(side="left")

        texto_frame = ctk.CTkFrame(header, fg_color="transparent")
        texto_frame.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(texto_frame, text="Agente B3",
                     font=FONTS["sidebar_title"],
                     text_color=COLORS["sidebar_item_active_text"]).pack(anchor="w")
        ctk.CTkLabel(texto_frame, text="Letras Financeiras",
                     font=FONTS["sidebar_sub"],
                     text_color=COLORS["sidebar_status_text"]).pack(anchor="w")

        # Separador
        self._separador(pady=(16, 12))

        # ── Itens de navegação ────────────────────────────────────────────
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="x", padx=8)

        for chave, label, dot_color in _ITENS_NAV:
            item = ctk.CTkFrame(nav_frame, fg_color="transparent",
                                corner_radius=8, cursor="hand2")
            item.pack(fill="x", pady=1)

            inner = ctk.CTkFrame(item, fg_color="transparent")
            inner.pack(fill="x", padx=8, pady=7)

            # Dot colorido
            canvas = ctk.CTkCanvas(inner, width=8, height=8,
                                   highlightthickness=0,
                                   bg=COLORS["sidebar_bg"])
            canvas.pack(side="left", padx=(0, 10))
            canvas.create_oval(0, 0, 8, 8, fill=dot_color, outline="")

            lbl = ctk.CTkLabel(inner, text=label,
                               font=FONTS["sidebar_item"],
                               text_color=COLORS["sidebar_item"],
                               anchor="w")
            lbl.pack(side="left", fill="x", expand=True)

            self._item_frames[chave] = item
            self._item_labels[chave] = lbl

            # Bind clique no frame inteiro e nos filhos
            for w in (item, inner, canvas, lbl):
                w.bind("<Button-1>", lambda e, c=chave: self._clicar(c))
            item.bind("<Enter>", lambda e, c=chave: self._hover_enter(c))
            item.bind("<Leave>", lambda e, c=chave: self._hover_leave(c))

        # Espaçador para empurrar status para baixo
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        # ── Status das fontes ─────────────────────────────────────────────
        self._separador(pady=(0, 12))

        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.pack(fill="x", padx=16, pady=(0, 4))

        ctk.CTkLabel(status_frame, text="FONTES",
                     font=("Arial", 9, "bold"),
                     text_color=COLORS["sidebar_status_text"]).pack(anchor="w", pady=(0, 6))

        self._pills: dict[str, ctk.CTkLabel] = {}
        for chave, texto in [("b3", "B3 RJLF"), ("anbima", "ANBIMA"),
                              ("up2data", "UP2DATA")]:
            pill = ctk.CTkLabel(
                status_frame,
                text=f"● {texto}",
                font=("Arial", 10),
                text_color=COLORS["sidebar_status_text"],
                anchor="w",
            )
            pill.pack(anchor="w", pady=1)
            self._pills[chave] = pill

        # Versão
        ctk.CTkLabel(self, text="v2.0",
                     font=("Arial", 10),
                     text_color=COLORS["sidebar_status_text"]).pack(pady=(4, 12))

        self._atualizar_visual()
        self.atualizar_status()

    def _separador(self, pady=(8, 8)):
        ctk.CTkFrame(self, fg_color=COLORS["sidebar_border"], height=1).pack(
            fill="x", pady=pady
        )

    def _clicar(self, chave: str):
        if chave == self._ativo:
            return
        self._ativo = chave
        self._atualizar_visual()
        if self.on_navegar:
            self.on_navegar(chave)

    def _hover_enter(self, chave: str):
        if chave != self._ativo:
            self._item_frames[chave].configure(fg_color="#141F35")
            self._item_labels[chave].configure(text_color=COLORS["sidebar_item_hover"])

    def _hover_leave(self, chave: str):
        if chave != self._ativo:
            self._item_frames[chave].configure(fg_color="transparent")
            self._item_labels[chave].configure(text_color=COLORS["sidebar_item"])

    def _atualizar_visual(self):
        for chave, frame in self._item_frames.items():
            if chave == self._ativo:
                frame.configure(fg_color=COLORS["sidebar_item_active_bg"])
                self._item_labels[chave].configure(
                    text_color=COLORS["sidebar_item_active_text"]
                )
            else:
                frame.configure(fg_color="transparent")
                self._item_labels[chave].configure(
                    text_color=COLORS["sidebar_item"]
                )

    def atualizar_ativo(self, chave: str):
        """Atualiza o item ativo sem disparar navegação."""
        self._ativo = chave
        self._atualizar_visual()

    def atualizar_status(self):
        """Atualiza os pills de status das fontes."""
        try:
            from gui.credentials import status_credenciais
            status = status_credenciais()
        except Exception:
            return

        mapa = {
            "b3": ("B3 RJLF", status.get("b3", False)),
            "anbima": ("ANBIMA", status.get("anbima", False)),
            "up2data": ("UP2DATA", status.get("up2data_cloud", False) or status.get("up2data_client", False)),
        }
        for chave, (texto, ativo) in mapa.items():
            pill = self._pills.get(chave)
            if not pill:
                continue
            cor = COLORS["accent_teal"] if ativo else COLORS["sidebar_status_text"]
            pill.configure(text=f"● {texto}", text_color=cor)
