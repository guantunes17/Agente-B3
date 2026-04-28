"""Widget inline para salvar/carregar presets sem janelas modais."""
import customtkinter as ctk
from pathlib import Path
from gui.styles import COLORS, FONTS, SIZES


class PresetManager(ctk.CTkFrame):
    """
    Gerenciador de presets embutido — salvar e carregar inline.

    on_carregar(filtros): chamado quando um preset é carregado.
    coletar_filtros(): função que retorna os FiltrosConsulta atuais.
    """

    def __init__(self, master, presets_dir: Path,
                 coletar_filtros=None, on_carregar=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.presets_dir = presets_dir
        self.coletar_filtros = coletar_filtros
        self.on_carregar = on_carregar
        self._modo = None  # "salvar" | "carregar" | None

        self._frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        self._frame_botoes.pack(fill="x")

        ctk.CTkButton(
            self._frame_botoes,
            text="Salvar preset",
            width=140, height=32,
            corner_radius=SIZES["button_corner_radius"],
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["border_medium"],
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_input"],
            font=FONTS["button_sm"],
            command=self._toggle_salvar,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            self._frame_botoes,
            text="Carregar preset",
            width=140, height=32,
            corner_radius=SIZES["button_corner_radius"],
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["border_medium"],
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_input"],
            font=FONTS["button_sm"],
            command=self._toggle_carregar,
        ).pack(side="left")

        self._frame_inline = ctk.CTkFrame(self, fg_color=COLORS["bg_input"],
                                           corner_radius=8)

    def _esconder_inline(self):
        self._frame_inline.pack_forget()
        for w in self._frame_inline.winfo_children():
            w.destroy()

    def _toggle_salvar(self):
        if self._modo == "salvar":
            self._modo = None
            self._esconder_inline()
            return
        self._modo = "salvar"
        self._esconder_inline()
        self._frame_inline.pack(fill="x", pady=(8, 0))
        self._construir_form_salvar()

    def _toggle_carregar(self):
        if self._modo == "carregar":
            self._modo = None
            self._esconder_inline()
            return
        self._modo = "carregar"
        self._esconder_inline()
        self._frame_inline.pack(fill="x", pady=(8, 0))
        self._construir_lista_presets()

    def _construir_form_salvar(self):
        pad = ctk.CTkFrame(self._frame_inline, fg_color="transparent")
        pad.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(pad, text="Nome do preset:", font=FONTS["field_label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")

        entry = ctk.CTkEntry(pad, placeholder_text="Ex: LFs Subordinadas A-",
                             height=SIZES["input_height"],
                             corner_radius=SIZES["input_corner_radius"],
                             border_color=COLORS["border_medium"])
        entry.pack(fill="x", pady=(4, 8))

        frame_btns = ctk.CTkFrame(pad, fg_color="transparent")
        frame_btns.pack(fill="x")

        ctk.CTkButton(
            frame_btns, text="Salvar", width=80, height=30,
            fg_color=COLORS["primary_600"], hover_color=COLORS["primary_700"],
            text_color="white", font=FONTS["button_sm"],
            command=lambda: self._executar_salvar(entry.get()),
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            frame_btns, text="Cancelar", width=80, height=30,
            fg_color="transparent", border_width=1,
            border_color=COLORS["border_medium"],
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_input"],
            font=FONTS["button_sm"],
            command=lambda: (setattr(self, "_modo", None), self._esconder_inline()),
        ).pack(side="left")

    def _executar_salvar(self, nome: str):
        nome = nome.strip()
        if not nome:
            return
        if self.coletar_filtros:
            try:
                filtros = self.coletar_filtros()
                filtros.salvar_preset(nome, self.presets_dir)
            except Exception:
                pass
        self._modo = None
        self._esconder_inline()

    def _construir_lista_presets(self):
        from config.filters import FiltrosConsulta
        presets = FiltrosConsulta.listar_presets(self.presets_dir)

        pad = ctk.CTkFrame(self._frame_inline, fg_color="transparent")
        pad.pack(fill="x", padx=12, pady=10)

        if not presets:
            ctk.CTkLabel(pad, text="Nenhum preset salvo.",
                         font=FONTS["small"], text_color=COLORS["text_muted"]).pack(anchor="w")
        else:
            scroll = ctk.CTkScrollableFrame(pad, height=150, fg_color="transparent")
            scroll.pack(fill="x")
            for p in presets:
                item = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"],
                                    corner_radius=6, border_width=1,
                                    border_color=COLORS["border_light"])
                item.pack(fill="x", pady=(0, 4))
                ctk.CTkLabel(item, text=p["nome"], font=FONTS["body"],
                             text_color=COLORS["text_primary"],
                             anchor="w").pack(side="left", padx=10, pady=6, fill="x", expand=True)
                ctk.CTkButton(
                    item, text="Usar", width=50, height=26,
                    fg_color=COLORS["primary_600"], hover_color=COLORS["primary_700"],
                    text_color="white", font=("Arial", 11),
                    command=lambda arq=p["arquivo"]: self._executar_carregar(arq),
                ).pack(side="right", padx=6, pady=4)

        ctk.CTkButton(
            pad, text="Fechar", width=80, height=28,
            fg_color="transparent", border_width=1,
            border_color=COLORS["border_medium"],
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_input"],
            font=FONTS["button_sm"],
            command=lambda: (setattr(self, "_modo", None), self._esconder_inline()),
        ).pack(anchor="w", pady=(8, 0))

    def _executar_carregar(self, arquivo: str):
        from config.filters import FiltrosConsulta
        try:
            filtros, _ = FiltrosConsulta.carregar_preset(Path(arquivo))
            if self.on_carregar:
                self.on_carregar(filtros)
        except Exception:
            pass
        self._modo = None
        self._esconder_inline()
