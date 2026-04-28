"""Card de métrica com valor grande."""
import customtkinter as ctk
from gui.styles import COLORS, FONTS


class MetricCard(ctk.CTkFrame):
    """Card com label, valor grande e subtexto opcional."""

    def __init__(self, master, label: str, valor: str, subtexto: str = "", **kwargs):
        super().__init__(master, fg_color=COLORS["bg_input"], corner_radius=10, **kwargs)
        pad = ctk.CTkFrame(self, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=14, pady=14)

        self._label_widget = ctk.CTkLabel(
            pad, text=label, font=FONTS["metric_label"],
            text_color=COLORS["text_secondary"], anchor="w"
        )
        self._label_widget.pack(fill="x")

        self._valor_widget = ctk.CTkLabel(
            pad, text=valor, font=FONTS["metric_value"],
            text_color=COLORS["text_primary"], anchor="w"
        )
        self._valor_widget.pack(fill="x")

        self._sub_widget = ctk.CTkLabel(
            pad, text=subtexto, font=("Arial", 10),
            text_color=COLORS["text_muted"], anchor="w"
        )
        if subtexto:
            self._sub_widget.pack(fill="x")

    def atualizar(self, valor: str, subtexto: str = None):
        """Atualiza o valor e opcionalmente o subtexto exibidos."""
        self._valor_widget.configure(text=valor)
        if subtexto is not None:
            self._sub_widget.configure(text=subtexto)
            self._sub_widget.pack(fill="x")
