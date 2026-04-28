"""Janela principal do Agente B3 com painel completo de filtros dinâmicos."""
import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

# Garantir raiz no path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.filters import FiltrosConsulta, ESCALA_RATINGS
from config.settings import PRESETS_DIR, OUTPUTS_DIR
from gui.styles import COLORS, FONTS, WINDOW


_PERIODOS = ["3", "6", "12", "24", "custom"]
_PERIODO_LABELS = {"3": "3m", "6": "6m", "12": "12m", "24": "24m", "custom": "Custom"}
_INDEXADORES = ["todos", "cdi", "ipca", "pre"]
_INDEXADOR_LABELS = {"todos": "Todos", "cdi": "CDI", "ipca": "IPCA", "pre": "Pré"}

_ERROS_AMIGAVEIS = {
    "ConnectionError": "Não foi possível acessar a internet. Verifique sua conexão.",
    "Timeout": "O servidor demorou muito para responder. Tente novamente.",
    "FileNotFoundError": "Não foi possível salvar o relatório na pasta selecionada.",
}


def _traduzir_erro(erro: str) -> str:
    for chave, msg in _ERROS_AMIGAVEIS.items():
        if chave.lower() in erro.lower():
            return msg
    return "Ocorreu um erro inesperado. Tente novamente."


class AgenteB3App:
    """Aplicação principal do Agente B3."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self._ultimo_arquivo: str | None = None
        self._ultimo_pasta: str | None = None

        self._configurar_janela()
        self._construir_ui()
        self._atualizar_pills_status()

    # ── Configuração da janela ─────────────────────────────────────────────

    def _configurar_janela(self):
        self.root.title(WINDOW["title"])
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(False, False)

        w, h = WINDOW["width"], WINDOW["height"]
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

    # ── UI ─────────────────────────────────────────────────────────────────

    def _construir_ui(self):
        # Canvas + scrollbar para scroll vertical
        self.canvas = tk.Canvas(self.root, bg=COLORS["bg"],
                                highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical",
                                      command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.frame_scroll = tk.Frame(self.canvas, bg=COLORS["bg"])
        self._win_id = self.canvas.create_window((0, 0), window=self.frame_scroll, anchor="nw")

        self.frame_scroll.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        f = self.frame_scroll
        self._build_header(f)
        self._build_pills(f)
        self._build_filtros(f)
        self._build_botao_principal(f)
        self._build_botoes_preset(f)
        self._build_area_status(f)
        self._build_footer(f)

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self._win_id, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ── Header ─────────────────────────────────────────────────────────────

    def _build_header(self, parent):
        frame = tk.Frame(parent, bg=COLORS["primary"], pady=16)
        frame.pack(fill="x")

        tk.Label(frame, text="B3", font=("Arial", 22, "bold"),
                 bg=COLORS["primary"], fg="white").pack()
        tk.Label(frame, text="Agente B3 — Letras Financeiras",
                 font=FONTS["title"], bg=COLORS["primary"], fg="white").pack()
        tk.Label(frame, text="v2.0  |  Filtros dinâmicos",
                 font=FONTS["small"], bg=COLORS["primary"],
                 fg="#A0B8D8").pack()

    # ── Pills de status ────────────────────────────────────────────────────

    def _build_pills(self, parent):
        frame = tk.Frame(parent, bg=COLORS["bg"], pady=10)
        frame.pack(fill="x", padx=16)

        self.pill_b3 = tk.Label(frame, text="● B3  —  não configurado",
                                 font=FONTS["small"], padx=10, pady=3,
                                 bg=COLORS["bg_secondary"], fg=COLORS["text_muted"])
        self.pill_b3.pack(side="left", padx=(0, 8))

        self.pill_anbima = tk.Label(frame, text="● ANBIMA  —  não configurado",
                                     font=FONTS["small"], padx=10, pady=3,
                                     bg=COLORS["bg_secondary"], fg=COLORS["text_muted"])
        self.pill_anbima.pack(side="left")

    def _atualizar_pills_status(self):
        from gui.credentials import status_credenciais
        status = status_credenciais()

        if status["b3"]:
            self.pill_b3.config(text="● B3  —  configurado",
                                bg=COLORS["success_bg"], fg=COLORS["success"])
        else:
            self.pill_b3.config(text="● B3  —  não configurado",
                                bg=COLORS["bg_secondary"], fg=COLORS["text_muted"])

        if status["anbima"]:
            self.pill_anbima.config(text="● ANBIMA  —  configurado",
                                    bg=COLORS["success_bg"], fg=COLORS["success"])
        else:
            self.pill_anbima.config(text="● ANBIMA  —  não configurado",
                                    bg=COLORS["bg_secondary"], fg=COLORS["text_muted"])

    # ── Painel de filtros ──────────────────────────────────────────────────

    def _build_filtros(self, parent):
        frame = tk.Frame(parent, bg=COLORS["bg"], padx=16, pady=4)
        frame.pack(fill="x")

        tk.Label(frame, text="Filtros da consulta",
                 font=("Arial", 13, "bold"),
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w", pady=(0, 10))

        self._filtro_rating(frame)
        self._filtro_periodo(frame)
        self._filtro_tipos(frame)
        self._filtro_valor(frame)
        self._filtro_spread(frame)
        self._filtro_indexador(frame)
        self._filtro_emissores(frame)
        self._filtro_pasta(frame)

    def _label_campo(self, parent, texto):
        tk.Label(parent, text=texto, font=FONTS["field_label"],
                 bg=COLORS["bg"], fg=COLORS["text_secondary"]).pack(anchor="w", pady=(10, 0))

    # a) Rating
    def _filtro_rating(self, parent):
        self._label_campo(parent, "Rating corporativo")

        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.pack(fill="x")
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        tk.Label(frame, text="Mínimo", font=FONTS["field_label"],
                 bg=COLORS["bg"], fg=COLORS["text_muted"]).grid(row=0, column=0, sticky="w")
        tk.Label(frame, text="Máximo", font=FONTS["field_label"],
                 bg=COLORS["bg"], fg=COLORS["text_muted"]).grid(row=0, column=1, sticky="w", padx=(8, 0))

        self.combo_rating_min = ttk.Combobox(
            frame, values=list(ESCALA_RATINGS), state="readonly",
            font=FONTS["body"], width=10
        )
        self.combo_rating_min.set("A-")
        self.combo_rating_min.grid(row=1, column=0, sticky="ew", pady=(2, 0))

        self.combo_rating_max = ttk.Combobox(
            frame, values=list(ESCALA_RATINGS), state="readonly",
            font=FONTS["body"], width=10
        )
        self.combo_rating_max.set("A-")
        self.combo_rating_max.grid(row=1, column=1, sticky="ew", pady=(2, 0), padx=(8, 0))

    # b) Período
    def _filtro_periodo(self, parent):
        self._label_campo(parent, "Período de análise")

        self.periodo_selecionado = "12"
        self._periodo_frames: dict[str, tk.Frame] = {}

        frame_toggles = tk.Frame(parent, bg=COLORS["bg"])
        frame_toggles.pack(fill="x", pady=(4, 0))

        for valor in _PERIODOS:
            label = _PERIODO_LABELS[valor]
            btn_frame = tk.Frame(frame_toggles, bg=COLORS["bg_secondary"],
                                  relief="solid", bd=1, padx=10, pady=4, cursor="hand2")
            btn_frame.pack(side="left", padx=(0, 6))
            lbl = tk.Label(btn_frame, text=label, font=FONTS["small"],
                           bg=COLORS["bg_secondary"], fg=COLORS["text_secondary"],
                           cursor="hand2")
            lbl.pack()
            for widget in (btn_frame, lbl):
                widget.bind("<Button-1>", lambda e, v=valor: self._selecionar_periodo(v))
            self._periodo_frames[valor] = (btn_frame, lbl)

        # Frame datas customizadas (oculto por padrão)
        self.frame_datas_custom = tk.Frame(parent, bg=COLORS["bg"])

        frame_d = self.frame_datas_custom
        frame_d.columnconfigure(0, weight=1)
        frame_d.columnconfigure(1, weight=1)

        tk.Label(frame_d, text="Data início (AAAA-MM-DD)", font=FONTS["field_label"],
                 bg=COLORS["bg"], fg=COLORS["text_muted"]).grid(row=0, column=0, sticky="w")
        tk.Label(frame_d, text="Data fim (AAAA-MM-DD)", font=FONTS["field_label"],
                 bg=COLORS["bg"], fg=COLORS["text_muted"]).grid(row=0, column=1, sticky="w", padx=(8, 0))

        self.entry_data_inicio = self._entry_placeholder(frame_d, "2024-01-01")
        self.entry_data_inicio.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        self.entry_data_fim = self._entry_placeholder(frame_d, "2024-12-31")
        self.entry_data_fim.grid(row=1, column=1, sticky="ew", pady=(2, 0), padx=(8, 0))

        self._selecionar_periodo("12")

    def _selecionar_periodo(self, valor: str):
        self.periodo_selecionado = valor
        for v, (btn_frame, lbl) in self._periodo_frames.items():
            if v == valor:
                btn_frame.config(bg=COLORS["primary_light"],
                                  highlightbackground=COLORS["border_active"])
                lbl.config(bg=COLORS["primary_light"], fg=COLORS["info"])
            else:
                btn_frame.config(bg=COLORS["bg_secondary"])
                lbl.config(bg=COLORS["bg_secondary"], fg=COLORS["text_secondary"])

        if valor == "custom":
            self.frame_datas_custom.pack(fill="x", pady=(6, 0))
        else:
            self.frame_datas_custom.pack_forget()

    # c) Tipos de LF
    def _filtro_tipos(self, parent):
        self._label_campo(parent, "Tipos de LF")

        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.pack(fill="x", pady=(4, 0))

        self.var_senior = tk.BooleanVar(value=True)
        self.var_t2 = tk.BooleanVar(value=True)
        self.var_at1 = tk.BooleanVar(value=True)

        for var, texto in [
            (self.var_senior, "Sênior (quirografária)"),
            (self.var_t2, "Subordinada Nível 2 (T2)"),
            (self.var_at1, "Subordinada AT1 (perpétua)"),
        ]:
            tk.Checkbutton(
                frame, text=texto, variable=var,
                font=FONTS["body"], bg=COLORS["bg"], fg=COLORS["text"],
                activebackground=COLORS["bg"],
                selectcolor=COLORS["primary_light"],
                cursor="hand2"
            ).pack(anchor="w")

    # d) Valor da emissão
    def _filtro_valor(self, parent):
        self._label_campo(parent, "Valor da emissão")

        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.pack(fill="x", pady=(4, 0))
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        tk.Label(frame, text="Mínimo (R$)", font=FONTS["field_label"],
                 bg=COLORS["bg"], fg=COLORS["text_muted"]).grid(row=0, column=0, sticky="w")
        tk.Label(frame, text="Máximo (R$)", font=FONTS["field_label"],
                 bg=COLORS["bg"], fg=COLORS["text_muted"]).grid(row=0, column=1, sticky="w", padx=(8, 0))

        self.entry_valor_min = self._entry_placeholder(frame, "Sem mínimo")
        self.entry_valor_min.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        self.entry_valor_max = self._entry_placeholder(frame, "Sem máximo")
        self.entry_valor_max.grid(row=1, column=1, sticky="ew", pady=(2, 0), padx=(8, 0))

    # e) Spread
    def _filtro_spread(self, parent):
        self._label_campo(parent, "Spread sobre CDI (% a.a.)")

        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.pack(fill="x", pady=(4, 0))
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        tk.Label(frame, text="Mínimo (%)", font=FONTS["field_label"],
                 bg=COLORS["bg"], fg=COLORS["text_muted"]).grid(row=0, column=0, sticky="w")
        tk.Label(frame, text="Máximo (%)", font=FONTS["field_label"],
                 bg=COLORS["bg"], fg=COLORS["text_muted"]).grid(row=0, column=1, sticky="w", padx=(8, 0))

        self.entry_spread_min = self._entry_placeholder(frame, "Sem mínimo")
        self.entry_spread_min.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        self.entry_spread_max = self._entry_placeholder(frame, "Sem máximo")
        self.entry_spread_max.grid(row=1, column=1, sticky="ew", pady=(2, 0), padx=(8, 0))

    # f) Indexador
    def _filtro_indexador(self, parent):
        self._label_campo(parent, "Indexador")

        self.indexador_selecionado = "todos"
        self._indexador_frames: dict[str, tuple] = {}

        frame_toggles = tk.Frame(parent, bg=COLORS["bg"])
        frame_toggles.pack(fill="x", pady=(4, 0))

        for valor in _INDEXADORES:
            label = _INDEXADOR_LABELS[valor]
            btn_frame = tk.Frame(frame_toggles, bg=COLORS["bg_secondary"],
                                  relief="solid", bd=1, padx=10, pady=4, cursor="hand2")
            btn_frame.pack(side="left", padx=(0, 6))
            lbl = tk.Label(btn_frame, text=label, font=FONTS["small"],
                           bg=COLORS["bg_secondary"], fg=COLORS["text_secondary"],
                           cursor="hand2")
            lbl.pack()
            for widget in (btn_frame, lbl):
                widget.bind("<Button-1>", lambda e, v=valor: self._selecionar_indexador(v))
            self._indexador_frames[valor] = (btn_frame, lbl)

        self._selecionar_indexador("todos")

    def _selecionar_indexador(self, valor: str):
        self.indexador_selecionado = valor
        for v, (btn_frame, lbl) in self._indexador_frames.items():
            if v == valor:
                btn_frame.config(bg=COLORS["primary_light"])
                lbl.config(bg=COLORS["primary_light"], fg=COLORS["info"])
            else:
                btn_frame.config(bg=COLORS["bg_secondary"])
                lbl.config(bg=COLORS["bg_secondary"], fg=COLORS["text_secondary"])

    # g) Emissores
    def _filtro_emissores(self, parent):
        self._label_campo(parent, "Emissores específicos (opcional)")
        self.entry_emissores = self._entry_placeholder(
            parent, "Ex: Banco Pine, ABC Brasil (deixe vazio para todos)"
        )
        self.entry_emissores.pack(fill="x", pady=(4, 0))

    # h) Pasta de destino
    def _filtro_pasta(self, parent):
        self._label_campo(parent, "Pasta de destino dos relatórios")

        pasta_padrao = str(Path.home() / "Documents" / "Relatorios LF")
        self.var_output_dir = tk.StringVar(value=pasta_padrao)

        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.pack(fill="x", pady=(4, 0))

        entry_pasta = tk.Entry(frame, textvariable=self.var_output_dir,
                               font=FONTS["body"], state="readonly",
                               relief="solid", bd=1,
                               highlightthickness=1,
                               highlightbackground=COLORS["border"],
                               readonlybackground=COLORS["bg_secondary"])
        entry_pasta.pack(side="left", fill="x", expand=True)

        tk.Button(frame, text="Alterar", font=FONTS["small"],
                  bg=COLORS["bg_secondary"], fg=COLORS["text_secondary"],
                  relief="solid", bd=1, padx=8, pady=4,
                  cursor="hand2", command=self._escolher_pasta).pack(side="left", padx=(6, 0))

    # ── Botão principal ────────────────────────────────────────────────────

    def _build_botao_principal(self, parent):
        frame = tk.Frame(parent, bg=COLORS["bg"], padx=16, pady=16)
        frame.pack(fill="x")

        self.btn_gerar = tk.Button(
            frame, text="Gerar Relatório",
            font=FONTS["button"],
            bg=COLORS["primary"], fg="white",
            relief="flat", pady=10,
            cursor="hand2", command=self._iniciar_geracao
        )
        self.btn_gerar.pack(fill="x")

        self.progressbar = ttk.Progressbar(frame, mode="indeterminate", length=100)

        self.label_progresso = tk.Label(frame, text="", font=FONTS["small"],
                                         bg=COLORS["bg"], fg=COLORS["text_secondary"])
        self.label_progresso.pack(pady=(4, 0))

    # ── Botões de preset ───────────────────────────────────────────────────

    def _build_botoes_preset(self, parent):
        frame = tk.Frame(parent, bg=COLORS["bg"], padx=16)
        frame.pack(fill="x")
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        tk.Button(
            frame, text="Salvar filtros como preset",
            font=FONTS["small"],
            bg=COLORS["bg"], fg=COLORS["text_secondary"],
            relief="solid", bd=1, pady=5,
            cursor="hand2", command=self._salvar_preset
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))

        tk.Button(
            frame, text="Carregar preset",
            font=FONTS["small"],
            bg=COLORS["bg"], fg=COLORS["text_secondary"],
            relief="solid", bd=1, pady=5,
            cursor="hand2", command=self._carregar_preset
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0))

    # ── Área de status ─────────────────────────────────────────────────────

    def _build_area_status(self, parent):
        self.frame_status = tk.Frame(parent, bg=COLORS["bg"], padx=16, pady=8)

        self.label_status_msg = tk.Label(
            self.frame_status, text="", font=FONTS["body"],
            bg=COLORS["bg"], fg=COLORS["text"], wraplength=460, justify="left"
        )
        self.label_status_msg.pack(anchor="w")

        self._frame_btns_pos = tk.Frame(self.frame_status, bg=COLORS["bg"])
        self._frame_btns_pos.pack(anchor="w", pady=(8, 0))

        self.btn_abrir_arquivo = tk.Button(
            self._frame_btns_pos, text="Abrir relatório",
            font=FONTS["small"], bg=COLORS["bg"], fg=COLORS["primary"],
            relief="solid", bd=1, padx=10, pady=4, cursor="hand2",
            command=self._abrir_arquivo
        )
        self.btn_abrir_pasta = tk.Button(
            self._frame_btns_pos, text="Abrir pasta",
            font=FONTS["small"], bg=COLORS["bg"], fg=COLORS["text_secondary"],
            relief="solid", bd=1, padx=10, pady=4, cursor="hand2",
            command=self._abrir_pasta
        )

    def _mostrar_status(self, tipo: str, mensagem: str):
        cores = {
            "sucesso": (COLORS["success_bg"], COLORS["success"]),
            "erro": (COLORS["error_bg"], COLORS["error"]),
            "aviso": (COLORS["warning_bg"], COLORS["warning"]),
        }
        bg, fg = cores.get(tipo, (COLORS["info_bg"], COLORS["info"]))
        self.frame_status.config(bg=bg)
        self._frame_btns_pos.config(bg=bg)
        self.label_status_msg.config(bg=bg, fg=fg, text=mensagem)

        self.btn_abrir_arquivo.pack_forget()
        self.btn_abrir_pasta.pack_forget()

        if tipo == "sucesso":
            self.btn_abrir_arquivo.pack(side="left", padx=(0, 8))
            self.btn_abrir_pasta.pack(side="left")

        self.frame_status.pack(fill="x", padx=16, pady=(4, 0))

    # ── Footer ─────────────────────────────────────────────────────────────

    def _build_footer(self, parent):
        tk.Frame(parent, bg=COLORS["border"], height=1).pack(fill="x", padx=16, pady=(12, 0))

        frame = tk.Frame(parent, bg=COLORS["bg"], pady=8)
        frame.pack(fill="x")

        lbl_agendar = tk.Label(frame, text="Agendar execução",
                                font=FONTS["small"], bg=COLORS["bg"],
                                fg=COLORS["primary"], cursor="hand2")
        lbl_agendar.pack(side="left", padx=16)
        lbl_agendar.bind("<Button-1>", lambda e: self._abrir_agendamento())

        lbl_config = tk.Label(frame, text="Configurações",
                               font=FONTS["small"], bg=COLORS["bg"],
                               fg=COLORS["primary"], cursor="hand2")
        lbl_config.pack(side="left")
        lbl_config.bind("<Button-1>", lambda e: self._abrir_configuracoes())

    # ── Geração do relatório ───────────────────────────────────────────────

    def _iniciar_geracao(self):
        try:
            filtros = self._coletar_filtros()
        except ValueError as e:
            messagebox.showwarning("Filtros inválidos", str(e), parent=self.root)
            return

        erros = filtros.validar()
        if erros:
            messagebox.showwarning(
                "Filtros inválidos",
                "\n".join(f"• {e}" for e in erros),
                parent=self.root
            )
            return

        # Garantir pasta de destino
        pasta = self.var_output_dir.get()
        if pasta:
            filtros.output_dir = pasta
            try:
                Path(pasta).mkdir(parents=True, exist_ok=True)
            except Exception:
                pass

        self.btn_gerar.config(state="disabled", text="Gerando relatório...")
        self.progressbar.pack(fill="x", pady=(8, 0))
        self.progressbar.start(15)
        self.label_progresso.config(text="Iniciando...")
        self.frame_status.pack_forget()

        thread = threading.Thread(
            target=self._executar_pipeline,
            args=(filtros,),
            daemon=True
        )
        thread.start()

    def _executar_pipeline(self, filtros: FiltrosConsulta):
        from main import executar_agente

        def callback(etapa, total, msg):
            self.root.after(0, lambda: self.label_progresso.config(
                text=f"[{etapa}/{total}] {msg}"
            ))

        resultado = executar_agente(filtros=filtros, callback=callback)
        self.root.after(0, lambda: self._finalizar_geracao(resultado))

    def _finalizar_geracao(self, resultado: dict):
        self.progressbar.stop()
        self.progressbar.pack_forget()
        self.btn_gerar.config(state="normal", text="Gerar Relatório")
        self.label_progresso.config(text="")

        if resultado["sucesso"]:
            self._ultimo_arquivo = resultado.get("arquivo")
            self._ultimo_pasta = str(Path(self._ultimo_arquivo).parent) if self._ultimo_arquivo else None
            n = resultado["emissoes"]
            t = resultado["tempo"]
            msg = f"✓  Relatório gerado — {n} emissão{'ões' if n != 1 else ''} selecionada{'s' if n != 1 else ''} ({t}s)"

            if resultado["avisos"]:
                msg += f"\n⚠  {resultado['avisos'][0]}"
                tipo = "aviso"
            else:
                tipo = "sucesso"

            self._mostrar_status(tipo, msg)
        else:
            erro_raw = resultado.get("erro") or "desconhecido"
            self._mostrar_status("erro", f"✗  {_traduzir_erro(erro_raw)}")

    # ── Coleta e preenchimento de filtros ──────────────────────────────────

    def _coletar_filtros(self) -> FiltrosConsulta:
        filtros = FiltrosConsulta()

        filtros.rating_minimo = self.combo_rating_min.get()
        filtros.rating_maximo = self.combo_rating_max.get()

        if self.periodo_selecionado == "custom":
            filtros.data_inicio = self.entry_data_inicio.get().strip()
            filtros.data_fim = self.entry_data_fim.get().strip()
            if filtros.data_inicio in ("", "2024-01-01"):
                filtros.data_inicio = None
            if filtros.data_fim in ("", "2024-12-31"):
                filtros.data_fim = None
        else:
            try:
                filtros.periodo_meses = int(self.periodo_selecionado)
            except ValueError:
                filtros.periodo_meses = 12

        filtros.incluir_senior = self.var_senior.get()
        filtros.incluir_subordinada_t2 = self.var_t2.get()
        filtros.incluir_subordinada_at1 = self.var_at1.get()
        filtros.valor_minimo = self._parse_valor(self.entry_valor_min.get())
        filtros.valor_maximo = self._parse_valor(self.entry_valor_max.get())
        filtros.spread_minimo = self._parse_float(self.entry_spread_min.get())
        filtros.spread_maximo = self._parse_float(self.entry_spread_max.get())
        filtros.indexador = self.indexador_selecionado

        emissores_texto = self.entry_emissores.get().strip()
        placeholder_emissores = "Ex: Banco Pine, ABC Brasil (deixe vazio para todos)"
        if emissores_texto and emissores_texto != placeholder_emissores:
            filtros.emissores = [e.strip() for e in emissores_texto.split(",") if e.strip()]

        filtros.output_dir = self.var_output_dir.get() or None
        return filtros

    def _preencher_campos(self, filtros: FiltrosConsulta):
        self.combo_rating_min.set(filtros.rating_minimo)
        self.combo_rating_max.set(filtros.rating_maximo)

        if filtros.data_inicio:
            self._selecionar_periodo("custom")
            self.entry_data_inicio.delete(0, "end")
            self.entry_data_inicio.insert(0, filtros.data_inicio)
            self.entry_data_fim.delete(0, "end")
            self.entry_data_fim.insert(0, filtros.data_fim or "")
        else:
            self._selecionar_periodo(str(filtros.periodo_meses))

        self.var_senior.set(filtros.incluir_senior)
        self.var_t2.set(filtros.incluir_subordinada_t2)
        self.var_at1.set(filtros.incluir_subordinada_at1)

        self._set_entry_placeholder(self.entry_valor_min,
                                    str(filtros.valor_minimo) if filtros.valor_minimo is not None else "",
                                    "Sem mínimo")
        self._set_entry_placeholder(self.entry_valor_max,
                                    str(filtros.valor_maximo) if filtros.valor_maximo is not None else "",
                                    "Sem máximo")
        self._set_entry_placeholder(self.entry_spread_min,
                                    str(filtros.spread_minimo) if filtros.spread_minimo is not None else "",
                                    "Sem mínimo")
        self._set_entry_placeholder(self.entry_spread_max,
                                    str(filtros.spread_maximo) if filtros.spread_maximo is not None else "",
                                    "Sem máximo")

        self._selecionar_indexador(filtros.indexador or "todos")

        placeholder_emissores = "Ex: Banco Pine, ABC Brasil (deixe vazio para todos)"
        if filtros.emissores:
            self._set_entry_placeholder(self.entry_emissores,
                                        ", ".join(filtros.emissores),
                                        placeholder_emissores)
        else:
            self._set_entry_placeholder(self.entry_emissores, "", placeholder_emissores)

    def _set_entry_placeholder(self, entry: tk.Entry, valor: str, placeholder: str):
        entry.delete(0, "end")
        if valor:
            entry.insert(0, valor)
            entry.config(fg=COLORS["text"])
        else:
            entry.insert(0, placeholder)
            entry.config(fg=COLORS["text_muted"])

    # ── Parsers ────────────────────────────────────────────────────────────

    def _parse_valor(self, texto: str) -> float | None:
        if not texto or texto.strip() in ("Sem mínimo", "Sem máximo", ""):
            return None
        t = texto.strip().lower()
        t = t.replace("r$", "").replace(" ", "").replace(".", "").replace(",", ".")
        try:
            if "mi" in t or "milhão" in t or "milhões" in t:
                num = float(t.replace("mi", "").replace("milhão", "").replace("milhões", ""))
                return num * 1_000_000
            return float(t)
        except ValueError:
            return None

    def _parse_float(self, texto: str) -> float | None:
        if not texto or texto.strip() in ("Sem mínimo", "Sem máximo", ""):
            return None
        t = texto.strip().replace(",", ".")
        try:
            return float(t)
        except ValueError:
            return None

    # ── Entry com placeholder ──────────────────────────────────────────────

    def _entry_placeholder(self, parent, placeholder: str) -> tk.Entry:
        entry = tk.Entry(parent, font=FONTS["body"],
                         relief="solid", bd=1,
                         highlightthickness=1,
                         highlightcolor=COLORS["border_active"],
                         highlightbackground=COLORS["border"],
                         fg=COLORS["text_muted"])
        entry.insert(0, placeholder)

        def on_focus_in(e):
            if entry.get() == placeholder:
                entry.delete(0, "end")
                entry.config(fg=COLORS["text"])

        def on_focus_out(e):
            if not entry.get().strip():
                entry.insert(0, placeholder)
                entry.config(fg=COLORS["text_muted"])

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        return entry

    # ── Ações ──────────────────────────────────────────────────────────────

    def _escolher_pasta(self):
        pasta = filedialog.askdirectory(title="Escolher pasta de destino", parent=self.root)
        if pasta:
            self.var_output_dir.set(pasta)

    def _salvar_preset(self):
        from gui.preset_dialog import PresetDialog
        try:
            filtros = self._coletar_filtros()
        except ValueError:
            filtros = FiltrosConsulta()
        PresetDialog(self.root, modo="salvar", filtros_atuais=filtros, presets_dir=PRESETS_DIR)

    def _carregar_preset(self):
        from gui.preset_dialog import PresetDialog
        dlg = PresetDialog(self.root, modo="carregar", presets_dir=PRESETS_DIR)
        if dlg.resultado:
            self._preencher_campos(dlg.resultado)

    def _abrir_configuracoes(self):
        from gui.settings_dialog import SettingsDialog
        SettingsDialog(self.root)
        self._atualizar_pills_status()

    def _abrir_agendamento(self):
        from gui.scheduler_dialog import SchedulerDialog
        SchedulerDialog(self.root, presets_dir=PRESETS_DIR)

    def _abrir_arquivo(self):
        if self._ultimo_arquivo and Path(self._ultimo_arquivo).exists():
            os.startfile(self._ultimo_arquivo)

    def _abrir_pasta(self):
        if self._ultimo_pasta and Path(self._ultimo_pasta).exists():
            subprocess.Popen(["explorer", self._ultimo_pasta])


def iniciar_gui():
    """Ponto de entrada da interface gráfica."""
    root = tk.Tk()
    _configurar_estilos_ttk(root)
    AgenteB3App(root)
    root.mainloop()


def _configurar_estilos_ttk(root: tk.Tk):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure("TCombobox",
                    fieldbackground=COLORS["bg"],
                    background=COLORS["bg"],
                    foreground=COLORS["text"],
                    bordercolor=COLORS["border"],
                    arrowcolor=COLORS["primary"])
    style.configure("Horizontal.TProgressbar",
                    troughcolor=COLORS["bg_secondary"],
                    background=COLORS["primary"])
