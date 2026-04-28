"""
Janela principal do Agente B3 — CustomTkinter.
Gerencia sidebar + container de páginas com transições suaves.
"""
import sys
from pathlib import Path

import customtkinter as ctk

from gui.styles import configurar_tema, COLORS, SIZES
from gui.sidebar import Sidebar
from gui.pages.gerar import PaginaGerar
from gui.pages.historico import PaginaHistorico
from gui.pages.agendamento import PaginaAgendamento
from gui.pages.configuracoes import PaginaConfiguracoes


_ANIM_STEPS = 8
_ANIM_MS = 25  # ms por step → ~200ms total


class App(ctk.CTk):
    """Janela principal do Agente B3."""

    def __init__(self):
        super().__init__()
        self._pagina_atual: str | None = None
        self._paginas: dict[str, ctk.CTkFrame] = {}
        self._configurar_janela()
        self._construir_layout()
        self.navegar_para("gerar")

    # ── Configuração da janela ─────────────────────────────────────────────

    def _configurar_janela(self):
        self.title("Agente B3 — Letras Financeiras")
        w = SIZES["default_window_width"]
        h = SIZES["default_window_height"]
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(SIZES["min_window_width"], SIZES["min_window_height"])
        self.resizable(True, True)

        # Ícone
        ico_path = Path(__file__).resolve().parent.parent / "assets" / "icon.ico"
        if not ico_path.exists():
            try:
                from gui.logo import salvar_ico
                salvar_ico(ico_path)
            except Exception:
                pass
        if ico_path.exists():
            try:
                self.iconbitmap(str(ico_path))
            except Exception:
                pass

        self.configure(fg_color=COLORS["bg_main"])

    # ── Layout ────────────────────────────────────────────────────────────────

    def _construir_layout(self):
        # Grid principal: sidebar fixa | conteúdo expansível
        self.grid_columnconfigure(0, weight=0, minsize=SIZES["sidebar_width"])
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = Sidebar(self, on_navegar=self.navegar_para)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Container das páginas com gradiente de fundo
        self._container = ctk.CTkFrame(self, fg_color=COLORS["bg_main"],
                                        corner_radius=0)
        self._container.grid(row=0, column=1, sticky="nsew")
        self._container.grid_rowconfigure(0, weight=1)
        self._container.grid_columnconfigure(0, weight=1)

        # Gradiente — canvas que fica atrás das páginas
        self._canvas_grad = ctk.CTkCanvas(
            self._container, highlightthickness=0, bd=0
        )
        self._canvas_grad.place(x=0, y=0, relwidth=1, relheight=1)
        self._container.bind("<Configure>", self._redesenhar_gradiente)

        # Instanciar páginas sobre o canvas
        self._paginas["gerar"] = PaginaGerar(self._container)
        self._paginas["historico"] = PaginaHistorico(self._container)
        self._paginas["agendamento"] = PaginaAgendamento(self._container)
        self._paginas["configuracoes"] = PaginaConfiguracoes(
            self._container,
            on_credenciais_salvas=self.atualizar_status_fontes,
        )

        for pagina in self._paginas.values():
            pagina.place(x=0, y=0, relwidth=1, relheight=1)
            pagina.place_forget()

    def _redesenhar_gradiente(self, event=None):
        """Redesenha o gradiente de fundo ao redimensionar."""
        w = self._container.winfo_width()
        if w < 1:
            return
        altura_grad = min(200, self._container.winfo_height())
        self._canvas_grad.delete("all")
        start = _hex_to_rgb(COLORS["bg_gradient_start"])
        end = _hex_to_rgb(COLORS["bg_gradient_end"])
        for i in range(altura_grad):
            t = i / altura_grad
            r = int(start[0] + (end[0] - start[0]) * t)
            g = int(start[1] + (end[1] - start[1]) * t)
            b = int(start[2] + (end[2] - start[2]) * t)
            cor = f"#{r:02x}{g:02x}{b:02x}"
            self._canvas_grad.create_line(0, i, w, i, fill=cor)
        # Resto da tela na cor de fundo
        bg = COLORS["bg_main"]
        self._canvas_grad.create_rectangle(
            0, altura_grad, w, self._container.winfo_height(),
            fill=bg, outline=bg
        )

    # ── Navegação e animações ─────────────────────────────────────────────────

    def navegar_para(self, pagina_nome: str):
        """Navega para uma página com transição slide-up suave."""
        if pagina_nome == self._pagina_atual:
            return

        pagina_nova = self._paginas.get(pagina_nome)
        pagina_antiga = self._paginas.get(self._pagina_atual) if self._pagina_atual else None

        # Atualizar histórico antes de exibir
        if pagina_nome == "historico":
            try:
                pagina_nova.atualizar()
            except Exception:
                pass

        if pagina_antiga:
            pagina_antiga.place_forget()

        self._pagina_atual = pagina_nome
        self.sidebar.atualizar_ativo(pagina_nome)

        # Slide up: começar com offset e animar para y=0
        pagina_nova.place(x=0, y=16, relwidth=1, relheight=1)
        pagina_nova.lift()
        self._animar_slide_up(pagina_nova, offset=16, step=0)

    def _animar_slide_up(self, pagina: ctk.CTkFrame, offset: int, step: int):
        """Anima a página de y=offset para y=0 em _ANIM_STEPS passos."""
        if step >= _ANIM_STEPS or offset <= 0:
            pagina.place(x=0, y=0, relwidth=1, relheight=1)
            return
        novo_offset = int(offset * (1 - (step + 1) / _ANIM_STEPS))
        pagina.place(x=0, y=novo_offset, relwidth=1, relheight=1)
        self.after(_ANIM_MS, lambda: self._animar_slide_up(pagina, offset, step + 1))

    # ── Método público ────────────────────────────────────────────────────────

    def atualizar_status_fontes(self):
        """Atualiza os pills de status da sidebar após salvar credenciais."""
        self.sidebar.atualizar_status()


def iniciar_gui():
    """Ponto de entrada da interface gráfica."""
    configurar_tema()
    app = App()
    app.mainloop()


def _hex_to_rgb(hex_str: str) -> tuple:
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
