"""Card container com título opcional."""
import customtkinter as ctk
from gui.styles import COLORS, SIZES, FONTS


class Card(ctk.CTkFrame):
    """
    Card com fundo branco, cantos arredondados e título opcional.

    Uso:
        card = Card(parent, titulo="Rating e período")
        ctk.CTkLabel(card.content, text="Conteúdo").pack()
    """

    def __init__(self, master, titulo: str = None, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_card"],
            corner_radius=SIZES["card_corner_radius"],
            border_width=1,
            border_color=COLORS["border_light"],
            **kwargs,
        )
        self._padding = ctk.CTkFrame(self, fg_color="transparent")
        self._padding.pack(fill="both", expand=True,
                           padx=SIZES["card_padding"], pady=SIZES["card_padding"])

        if titulo:
            ctk.CTkLabel(
                self._padding,
                text=titulo,
                font=FONTS["card_title"],
                text_color=COLORS["text_primary"],
                anchor="w",
            ).pack(fill="x", pady=(0, 12))

    @property
    def content(self) -> ctk.CTkFrame:
        """Frame interno onde os filhos devem ser adicionados."""
        return self._padding
