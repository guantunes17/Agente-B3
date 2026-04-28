"""Barra de status (sucesso, erro, warning)."""
import customtkinter as ctk
from gui.styles import COLORS, FONTS


class StatusBar(ctk.CTkFrame):
    """Barra de status com dot colorido e mensagem de texto."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._visible = False

    def mostrar_sucesso(self, mensagem: str):
        self._mostrar(COLORS["success_bg"], COLORS["success_dot"], COLORS["success"], mensagem)

    def mostrar_erro(self, mensagem: str):
        self._mostrar(COLORS["error_bg"], COLORS["error"], COLORS["error"], mensagem)

    def mostrar_warning(self, mensagem: str):
        self._mostrar(COLORS["warning_bg"], COLORS["warning"], COLORS["warning"], mensagem)

    def mostrar_info(self, mensagem: str):
        self._mostrar(COLORS["primary_50"], COLORS["primary_600"], COLORS["primary_800"], mensagem)

    def esconder(self):
        for w in self.winfo_children():
            w.destroy()
        self.configure(fg_color="transparent")
        self._visible = False

    def _mostrar(self, bg: str, dot_color: str, text_color: str, mensagem: str):
        self.esconder()
        self.configure(fg_color=bg, corner_radius=10)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=14, pady=10)

        # Dot indicador
        canvas = ctk.CTkCanvas(container, width=10, height=10,
                                highlightthickness=0, bg=bg)
        canvas.pack(side="left", padx=(0, 8))
        canvas.create_oval(1, 1, 9, 9, fill=dot_color, outline="")

        ctk.CTkLabel(
            container, text=mensagem, font=FONTS["status_text"],
            text_color=text_color, anchor="w", wraplength=500
        ).pack(side="left", fill="x", expand=True)

        self._visible = True
