"""Página 'Gerar relatório' — filtros + botão + status."""
import os
import threading
import subprocess
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog

from config.filters import FiltrosConsulta, ESCALA_RATINGS
from config.settings import PRESETS_DIR, OUTPUTS_DIR
from gui.styles import COLORS, FONTS, SIZES
from gui.components.card import Card
from gui.components.toggle_group import ToggleGroup
from gui.components.status_bar import StatusBar
from gui.components.preset_manager import PresetManager


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


class PaginaGerar(ctk.CTkFrame):
    """Página principal de geração de relatório."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._ultimo_arquivo: str | None = None
        self._ultimo_pasta: str | None = None
        self._construir()

    def _construir(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True,
                    padx=SIZES["page_padding_x"], pady=SIZES["page_padding_y"])

        # Título
        ctk.CTkLabel(scroll, text="Gerar relatório",
                     font=FONTS["page_title"],
                     text_color=COLORS["text_primary"],
                     anchor="w").pack(fill="x")
        ctk.CTkLabel(scroll, text="Configure os filtros e gere o relatório de Letras Financeiras",
                     font=FONTS["page_subtitle"],
                     text_color=COLORS["text_secondary"],
                     anchor="w").pack(fill="x", pady=(2, 20))

        # ── Card Rating e Período ─────────────────────────────────────────
        card_rating = Card(scroll, titulo="Rating e período")
        card_rating.pack(fill="x", pady=(0, 12))

        self._build_rating(card_rating.content)
        self._build_periodo(card_rating.content)

        # ── Card Tipos e Filtros ──────────────────────────────────────────
        card_filtros = Card(scroll, titulo="Tipos e filtros")
        card_filtros.pack(fill="x", pady=(0, 12))

        self._build_tipos(card_filtros.content)
        self._build_valor(card_filtros.content)
        self._build_spread(card_filtros.content)
        self._build_indexador(card_filtros.content)
        self._build_emissores(card_filtros.content)

        # ── Card Pasta de destino ─────────────────────────────────────────
        card_pasta = Card(scroll, titulo="Pasta de destino")
        card_pasta.pack(fill="x", pady=(0, 12))
        self._build_pasta(card_pasta.content)

        # ── Presets ───────────────────────────────────────────────────────
        self._preset_manager = PresetManager(
            scroll,
            presets_dir=PRESETS_DIR,
            coletar_filtros=self._coletar_filtros,
            on_carregar=self._preencher_campos,
        )
        self._preset_manager.pack(fill="x", pady=(0, 16))

        # ── Botão Gerar ───────────────────────────────────────────────────
        self._btn_gerar = ctk.CTkButton(
            scroll,
            text="Gerar relatório",
            height=SIZES["button_height"],
            corner_radius=SIZES["button_corner_radius"],
            fg_color=COLORS["primary_700"],
            hover_color=COLORS["primary_600"],
            text_color="white",
            font=FONTS["button"],
            command=self._iniciar_geracao,
        )
        self._btn_gerar.pack(fill="x")

        self._barra_progresso = ctk.CTkProgressBar(scroll, mode="indeterminate",
                                                    height=4,
                                                    fg_color=COLORS["border_light"],
                                                    progress_color=COLORS["primary_500"])
        self._label_progresso = ctk.CTkLabel(scroll, text="",
                                              font=FONTS["small"],
                                              text_color=COLORS["text_secondary"])

        # ── Status bar ────────────────────────────────────────────────────
        self._status_bar = StatusBar(scroll)
        self._status_bar.pack(fill="x", pady=(10, 0))

        # Botões pós-geração (ocultos inicialmente)
        self._frame_pos = ctk.CTkFrame(scroll, fg_color="transparent")
        self._btn_abrir_arq = ctk.CTkButton(
            self._frame_pos, text="Abrir relatório",
            width=130, height=32,
            corner_radius=SIZES["button_corner_radius"],
            fg_color=COLORS["primary_600"], hover_color=COLORS["primary_700"],
            text_color="white", font=FONTS["button_sm"],
            command=self._abrir_arquivo,
        )
        self._btn_abrir_pasta = ctk.CTkButton(
            self._frame_pos, text="Abrir pasta",
            width=120, height=32,
            corner_radius=SIZES["button_corner_radius"],
            fg_color="transparent", border_width=1,
            border_color=COLORS["border_medium"],
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_input"],
            font=FONTS["button_sm"],
            command=self._abrir_pasta,
        )

    # ── Builders de filtros ───────────────────────────────────────────────────

    def _field_label(self, parent, texto: str, pady=(12, 0)):
        ctk.CTkLabel(parent, text=texto, font=FONTS["field_label"],
                     text_color=COLORS["text_secondary"],
                     anchor="w").pack(fill="x", pady=(pady[0], 0))

    def _build_rating(self, parent):
        self._field_label(parent, "Rating corporativo", pady=(0, 0))
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(4, 0))
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(2, weight=1)

        ctk.CTkLabel(frame, text="Mínimo", font=FONTS["field_label"],
                     text_color=COLORS["text_muted"]).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(frame, text="Máximo", font=FONTS["field_label"],
                     text_color=COLORS["text_muted"]).grid(row=0, column=2, sticky="w", padx=(12, 0))

        self._combo_rating_min = ctk.CTkComboBox(
            frame, values=list(ESCALA_RATINGS), state="readonly",
            height=SIZES["input_height"], corner_radius=SIZES["input_corner_radius"],
            border_color=COLORS["border_medium"],
            button_color=COLORS["primary_400"],
            fg_color=COLORS["bg_card"],
        )
        self._combo_rating_min.set("A-")
        self._combo_rating_min.grid(row=1, column=0, sticky="ew", pady=(2, 0))

        ctk.CTkLabel(frame, text="–", font=FONTS["body"],
                     text_color=COLORS["text_muted"]).grid(row=1, column=1, padx=8)

        self._combo_rating_max = ctk.CTkComboBox(
            frame, values=list(ESCALA_RATINGS), state="readonly",
            height=SIZES["input_height"], corner_radius=SIZES["input_corner_radius"],
            border_color=COLORS["border_medium"],
            button_color=COLORS["primary_400"],
            fg_color=COLORS["bg_card"],
        )
        self._combo_rating_max.set("A-")
        self._combo_rating_max.grid(row=1, column=2, sticky="ew", pady=(2, 0), padx=(12, 0))

    def _build_periodo(self, parent):
        self._field_label(parent, "Período de análise")
        self._toggle_periodo = ToggleGroup(
            parent,
            opcoes=["3m", "6m", "12m", "24m", "Custom"],
            padrao="12m",
            on_change=self._ao_mudar_periodo,
        )
        self._toggle_periodo.pack(anchor="w", pady=(4, 0))

        # Frame datas customizadas (oculto por padrão)
        self._frame_datas = ctk.CTkFrame(parent, fg_color="transparent")
        f = self._frame_datas
        f.columnconfigure(0, weight=1)
        f.columnconfigure(1, weight=1)
        ctk.CTkLabel(f, text="Data início (AAAA-MM-DD)", font=FONTS["field_label"],
                     text_color=COLORS["text_muted"]).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(f, text="Data fim (AAAA-MM-DD)", font=FONTS["field_label"],
                     text_color=COLORS["text_muted"]).grid(row=0, column=1, sticky="w", padx=(12, 0))
        self._entry_data_inicio = ctk.CTkEntry(
            f, placeholder_text="2024-01-01",
            height=SIZES["input_height"], corner_radius=SIZES["input_corner_radius"],
            border_color=COLORS["border_medium"],
        )
        self._entry_data_inicio.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        self._entry_data_fim = ctk.CTkEntry(
            f, placeholder_text="2024-12-31",
            height=SIZES["input_height"], corner_radius=SIZES["input_corner_radius"],
            border_color=COLORS["border_medium"],
        )
        self._entry_data_fim.grid(row=1, column=1, sticky="ew", pady=(2, 0), padx=(12, 0))

    def _ao_mudar_periodo(self, opcao: str):
        if opcao == "Custom":
            self._frame_datas.pack(fill="x", pady=(8, 0))
        else:
            self._frame_datas.pack_forget()

    def _build_tipos(self, parent):
        self._field_label(parent, "Tipos de LF", pady=(0, 0))
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(anchor="w", pady=(4, 0))

        self._var_senior = ctk.BooleanVar(value=True)
        self._var_t2 = ctk.BooleanVar(value=True)
        self._var_at1 = ctk.BooleanVar(value=True)

        for var, texto in [
            (self._var_senior, "Sênior (quirografária)"),
            (self._var_t2, "Subordinada Nível 2 (T2)"),
            (self._var_at1, "Subordinada AT1 (perpétua)"),
        ]:
            ctk.CTkCheckBox(
                frame, text=texto, variable=var,
                font=FONTS["body"],
                text_color=COLORS["text_primary"],
                fg_color=COLORS["primary_600"],
                hover_color=COLORS["primary_400"],
                checkmark_color="white",
            ).pack(anchor="w", pady=2)

    def _build_valor(self, parent):
        self._field_label(parent, "Valor da emissão (R$)")
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(4, 0))
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="Mínimo", font=FONTS["field_label"],
                     text_color=COLORS["text_muted"]).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(frame, text="Máximo", font=FONTS["field_label"],
                     text_color=COLORS["text_muted"]).grid(row=0, column=1, sticky="w", padx=(12, 0))

        self._entry_valor_min = ctk.CTkEntry(
            frame, placeholder_text="Sem mínimo",
            height=SIZES["input_height"], corner_radius=SIZES["input_corner_radius"],
            border_color=COLORS["border_medium"],
        )
        self._entry_valor_min.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        self._entry_valor_max = ctk.CTkEntry(
            frame, placeholder_text="Sem máximo",
            height=SIZES["input_height"], corner_radius=SIZES["input_corner_radius"],
            border_color=COLORS["border_medium"],
        )
        self._entry_valor_max.grid(row=1, column=1, sticky="ew", pady=(2, 0), padx=(12, 0))

    def _build_spread(self, parent):
        self._field_label(parent, "Spread sobre CDI (% a.a.)")
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(4, 0))
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="Mínimo (%)", font=FONTS["field_label"],
                     text_color=COLORS["text_muted"]).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(frame, text="Máximo (%)", font=FONTS["field_label"],
                     text_color=COLORS["text_muted"]).grid(row=0, column=1, sticky="w", padx=(12, 0))

        self._entry_spread_min = ctk.CTkEntry(
            frame, placeholder_text="Sem mínimo",
            height=SIZES["input_height"], corner_radius=SIZES["input_corner_radius"],
            border_color=COLORS["border_medium"],
        )
        self._entry_spread_min.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        self._entry_spread_max = ctk.CTkEntry(
            frame, placeholder_text="Sem máximo",
            height=SIZES["input_height"], corner_radius=SIZES["input_corner_radius"],
            border_color=COLORS["border_medium"],
        )
        self._entry_spread_max.grid(row=1, column=1, sticky="ew", pady=(2, 0), padx=(12, 0))

    def _build_indexador(self, parent):
        self._field_label(parent, "Indexador")
        self._toggle_indexador = ToggleGroup(
            parent,
            opcoes=["Todos", "CDI", "IPCA", "Pré"],
            padrao="Todos",
        )
        self._toggle_indexador.pack(anchor="w", pady=(4, 0))

    def _build_emissores(self, parent):
        self._field_label(parent, "Emissores específicos (opcional)")
        self._entry_emissores = ctk.CTkEntry(
            parent,
            placeholder_text="Ex: Banco Pine, ABC Brasil (deixe vazio para todos)",
            height=SIZES["input_height"], corner_radius=SIZES["input_corner_radius"],
            border_color=COLORS["border_medium"],
        )
        self._entry_emissores.pack(fill="x", pady=(4, 0))

    def _build_pasta(self, parent):
        pasta_padrao = str(Path.home() / "Documents" / "Relatorios LF")
        self._var_pasta = ctk.StringVar(value=pasta_padrao)

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x")

        entry_pasta = ctk.CTkEntry(
            frame, textvariable=self._var_pasta,
            state="readonly",
            height=SIZES["input_height"], corner_radius=SIZES["input_corner_radius"],
            border_color=COLORS["border_medium"],
            fg_color=COLORS["bg_input"],
        )
        entry_pasta.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            frame, text="Alterar", width=80, height=SIZES["input_height"],
            corner_radius=SIZES["input_corner_radius"],
            fg_color="transparent", border_width=1,
            border_color=COLORS["border_medium"],
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_input"],
            font=FONTS["button_sm"],
            command=self._escolher_pasta,
        ).pack(side="left", padx=(8, 0))

    # ── Coleta de filtros ─────────────────────────────────────────────────────

    def _coletar_filtros(self) -> FiltrosConsulta:
        filtros = FiltrosConsulta()
        filtros.rating_minimo = self._combo_rating_min.get()
        filtros.rating_maximo = self._combo_rating_max.get()

        periodo = self._toggle_periodo.get()
        if periodo == "Custom":
            filtros.data_inicio = self._entry_data_inicio.get().strip() or None
            filtros.data_fim = self._entry_data_fim.get().strip() or None
        else:
            try:
                filtros.periodo_meses = int(periodo.replace("m", ""))
            except ValueError:
                filtros.periodo_meses = 12

        filtros.incluir_senior = self._var_senior.get()
        filtros.incluir_subordinada_t2 = self._var_t2.get()
        filtros.incluir_subordinada_at1 = self._var_at1.get()
        filtros.valor_minimo = self._parse_float(self._entry_valor_min.get())
        filtros.valor_maximo = self._parse_float(self._entry_valor_max.get())
        filtros.spread_minimo = self._parse_float(self._entry_spread_min.get())
        filtros.spread_maximo = self._parse_float(self._entry_spread_max.get())

        idx_map = {"Todos": "todos", "CDI": "cdi", "IPCA": "ipca", "Pré": "pre"}
        filtros.indexador = idx_map.get(self._toggle_indexador.get(), "todos")

        emissores = self._entry_emissores.get().strip()
        if emissores:
            filtros.emissores = [e.strip() for e in emissores.split(",") if e.strip()]

        filtros.output_dir = self._var_pasta.get() or None
        return filtros

    def _preencher_campos(self, filtros: FiltrosConsulta):
        """Preenche os campos com os valores de um preset."""
        self._combo_rating_min.set(filtros.rating_minimo)
        self._combo_rating_max.set(filtros.rating_maximo)

        if filtros.data_inicio:
            self._toggle_periodo.set("Custom")
            self._ao_mudar_periodo("Custom")
            self._entry_data_inicio.delete(0, "end")
            self._entry_data_inicio.insert(0, filtros.data_inicio)
            self._entry_data_fim.delete(0, "end")
            if filtros.data_fim:
                self._entry_data_fim.insert(0, filtros.data_fim)
        else:
            meses_str = f"{filtros.periodo_meses}m"
            if meses_str in ["3m", "6m", "12m", "24m"]:
                self._toggle_periodo.set(meses_str)
                self._ao_mudar_periodo(meses_str)

        self._var_senior.set(filtros.incluir_senior)
        self._var_t2.set(filtros.incluir_subordinada_t2)
        self._var_at1.set(filtros.incluir_subordinada_at1)

        self._set_entry(self._entry_valor_min, filtros.valor_minimo)
        self._set_entry(self._entry_valor_max, filtros.valor_maximo)
        self._set_entry(self._entry_spread_min, filtros.spread_minimo)
        self._set_entry(self._entry_spread_max, filtros.spread_maximo)

        idx_rev = {"todos": "Todos", "cdi": "CDI", "ipca": "IPCA", "pre": "Pré"}
        self._toggle_indexador.set(idx_rev.get(filtros.indexador or "todos", "Todos"))

        self._entry_emissores.delete(0, "end")
        if filtros.emissores:
            self._entry_emissores.insert(0, ", ".join(filtros.emissores))

    def _set_entry(self, entry: ctk.CTkEntry, valor):
        entry.delete(0, "end")
        if valor is not None:
            entry.insert(0, str(valor))

    # ── Parsers ───────────────────────────────────────────────────────────────

    def _parse_float(self, texto: str):
        if not texto or texto.strip() in ("Sem mínimo", "Sem máximo", ""):
            return None
        t = texto.strip().replace(",", ".")
        try:
            return float(t)
        except ValueError:
            return None

    # ── Geração ───────────────────────────────────────────────────────────────

    def _iniciar_geracao(self):
        try:
            filtros = self._coletar_filtros()
        except Exception as e:
            self._status_bar.mostrar_erro(str(e))
            return

        erros = filtros.validar()
        if erros:
            self._status_bar.mostrar_erro("Filtros inválidos: " + " | ".join(erros))
            return

        if filtros.output_dir:
            Path(filtros.output_dir).mkdir(parents=True, exist_ok=True)

        self._btn_gerar.configure(state="disabled", text="Gerando relatório...")
        self._barra_progresso.pack(fill="x", pady=(8, 0))
        self._barra_progresso.start()
        self._label_progresso.pack(fill="x")
        self._status_bar.esconder()
        self._frame_pos.pack_forget()

        threading.Thread(
            target=self._executar_pipeline, args=(filtros,), daemon=True
        ).start()

    def _executar_pipeline(self, filtros: FiltrosConsulta):
        from main import executar_agente

        def callback(etapa, total, msg):
            self.after(0, lambda: self._label_progresso.configure(
                text=f"[{etapa}/{total}] {msg}"
            ))

        resultado = executar_agente(filtros=filtros, callback=callback)
        self.after(0, lambda: self._finalizar_geracao(resultado, filtros))

    def _finalizar_geracao(self, resultado: dict, filtros: FiltrosConsulta):
        self._barra_progresso.stop()
        self._barra_progresso.pack_forget()
        self._label_progresso.pack_forget()
        self._btn_gerar.configure(state="normal", text="Gerar relatório")

        if resultado["sucesso"]:
            self._ultimo_arquivo = resultado.get("arquivo")
            self._ultimo_pasta = str(Path(self._ultimo_arquivo).parent) if self._ultimo_arquivo else None
            n = resultado["emissoes"]
            t = resultado["tempo"]
            plural = "ões" if n != 1 else "ão"
            msg = f"Relatório gerado — {n} emiss{plural} selecionada{'s' if n != 1 else ''} ({t}s)"

            if resultado["avisos"]:
                self._status_bar.mostrar_warning(msg + f" — {resultado['avisos'][0]}")
            else:
                self._status_bar.mostrar_sucesso(msg)

            self._frame_pos.pack(fill="x", pady=(8, 0))
            self._btn_abrir_arq.pack(side="left", padx=(0, 8))
            self._btn_abrir_pasta.pack(side="left")

            # Registrar no histórico
            try:
                _salvar_historico(resultado, filtros)
            except Exception:
                pass
        else:
            erro_raw = resultado.get("erro") or "desconhecido"
            self._status_bar.mostrar_erro(_traduzir_erro(erro_raw))

    def _escolher_pasta(self):
        pasta = filedialog.askdirectory(title="Escolher pasta de destino")
        if pasta:
            self._var_pasta.set(pasta)

    def _abrir_arquivo(self):
        if self._ultimo_arquivo and Path(self._ultimo_arquivo).exists():
            os.startfile(self._ultimo_arquivo)

    def _abrir_pasta(self):
        if self._ultimo_pasta and Path(self._ultimo_pasta).exists():
            subprocess.Popen(["explorer", self._ultimo_pasta])


def _salvar_historico(resultado: dict, filtros: FiltrosConsulta):
    """Salva registro no histórico de relatórios gerados."""
    import json
    from datetime import datetime

    outputs_dir = Path.home() / "Documents" / "Relatorios LF"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    historico_path = outputs_dir / "historico.json"

    historico = {"relatorios": []}
    if historico_path.exists():
        try:
            historico = json.loads(historico_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    arquivo = resultado.get("arquivo", "")
    registro = {
        "arquivo": Path(arquivo).name if arquivo else "",
        "caminho": arquivo,
        "data": datetime.now().isoformat(),
        "filtros": resultado.get("filtros_aplicados", {}),
        "emissoes": resultado.get("emissoes", 0),
        "tempo_segundos": resultado.get("tempo", 0),
        "fontes_usadas": [],
    }
    historico["relatorios"].insert(0, registro)
    # Manter apenas os últimos 100
    historico["relatorios"] = historico["relatorios"][:100]
    historico_path.write_text(json.dumps(historico, indent=2, ensure_ascii=False), encoding="utf-8")
