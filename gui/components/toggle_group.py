"""Toggle group: botões mutuamente exclusivos."""
import customtkinter as ctk
from gui.styles import COLORS, SIZES


class ToggleGroup(ctk.CTkFrame):
    """
    Grupo de botões toggle (radio button visual).
    Apenas um pode estar ativo por vez.

    Uso:
        tg = ToggleGroup(parent, opcoes=["3m", "6m", "12m"], padrao="12m", on_change=callback)
    """

    def __init__(self, master, opcoes: list, padrao: str = None,
                 on_change=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.opcoes = opcoes
        self.on_change = on_change
        self._selecionado = padrao or opcoes[0]
        self._botoes = {}

        for opcao in opcoes:
            btn = ctk.CTkButton(
                self,
                text=opcao,
                width=0,
                height=34,
                corner_radius=SIZES["toggle_corner_radius"],
                font=("Arial", 12),
                command=lambda o=opcao: self._selecionar(o),
            )
            btn.pack(side="left", padx=(0, 4))
            self._botoes[opcao] = btn

        self._atualizar_visual()

    def _selecionar(self, opcao: str):
        if opcao == self._selecionado:
            return
        self._selecionado = opcao
        self._atualizar_visual()
        if self.on_change:
            self.on_change(opcao)

    def _atualizar_visual(self):
        for opcao, btn in self._botoes.items():
            if opcao == self._selecionado:
                btn.configure(
                    fg_color=COLORS["toggle_active_bg"],
                    text_color=COLORS["toggle_active_text"],
                    border_width=1,
                    border_color=COLORS["toggle_active_border"],
                    hover_color=COLORS["toggle_active_bg"],
                )
            else:
                btn.configure(
                    fg_color=COLORS["toggle_inactive_bg"],
                    text_color=COLORS["toggle_inactive_text"],
                    border_width=1,
                    border_color=COLORS["border_light"],
                    hover_color="#E8E8E8",
                )

    def get(self) -> str:
        return self._selecionado

    def set(self, opcao: str):
        if opcao in self._botoes:
            self._selecionar(opcao)
