"""Página 'Agendamento' — configuração de execuções automáticas."""
import json
import subprocess
from pathlib import Path

import customtkinter as ctk

from config.filters import FiltrosConsulta
from config.settings import PRESETS_DIR, PROJECT_ROOT
from gui.styles import COLORS, FONTS, SIZES
from gui.components.card import Card
from gui.components.toggle_group import ToggleGroup
from gui.components.status_bar import StatusBar


class PaginaAgendamento(ctk.CTkFrame):
    """Página de agendamento de execução automática."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._construir()

    def _construir(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True,
                    padx=SIZES["page_padding_x"], pady=SIZES["page_padding_y"])

        ctk.CTkLabel(scroll, text="Agendamento",
                     font=FONTS["page_title"],
                     text_color=COLORS["text_primary"],
                     anchor="w").pack(fill="x")
        ctk.CTkLabel(scroll,
                     text="Configure execuções automáticas do agente",
                     font=FONTS["page_subtitle"],
                     text_color=COLORS["text_secondary"],
                     anchor="w").pack(fill="x", pady=(2, 20))

        # ── Card principal ────────────────────────────────────────────────
        card = Card(scroll, titulo="Configuração do agendamento")
        card.pack(fill="x", pady=(0, 12))
        c = card.content

        # Frequência
        ctk.CTkLabel(c, text="Frequência", font=FONTS["field_label"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x")
        self._toggle_freq = ToggleGroup(
            c, opcoes=["Diário", "Semanal", "Mensal"], padrao="Diário",
            on_change=self._ao_mudar_frequencia,
        )
        self._toggle_freq.pack(anchor="w", pady=(4, 12))

        # Dia da semana (só para Semanal)
        self._frame_semana = ctk.CTkFrame(c, fg_color="transparent")
        ctk.CTkLabel(self._frame_semana, text="Dia da semana",
                     font=FONTS["field_label"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x")
        self._combo_dia_semana = ctk.CTkComboBox(
            self._frame_semana,
            values=["Segunda-feira", "Terça-feira", "Quarta-feira",
                    "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"],
            height=SIZES["input_height"], corner_radius=SIZES["input_corner_radius"],
            border_color=COLORS["border_medium"],
            state="readonly",
        )
        self._combo_dia_semana.set("Segunda-feira")
        self._combo_dia_semana.pack(fill="x", pady=(4, 12))

        # Dia do mês (só para Mensal)
        self._frame_mes = ctk.CTkFrame(c, fg_color="transparent")
        ctk.CTkLabel(self._frame_mes, text="Dia do mês",
                     font=FONTS["field_label"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x")
        self._combo_dia_mes = ctk.CTkComboBox(
            self._frame_mes,
            values=[str(i) for i in range(1, 29)],
            height=SIZES["input_height"], corner_radius=SIZES["input_corner_radius"],
            border_color=COLORS["border_medium"],
            state="readonly",
        )
        self._combo_dia_mes.set("1")
        self._combo_dia_mes.pack(fill="x", pady=(4, 12))

        # Horário
        ctk.CTkLabel(c, text="Horário de execução", font=FONTS["field_label"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x")
        frame_hora = ctk.CTkFrame(c, fg_color="transparent")
        frame_hora.pack(anchor="w", pady=(4, 12))

        horas = [f"{h:02d}" for h in range(24)]
        minutos = ["00", "15", "30", "45"]

        self._combo_hora = ctk.CTkComboBox(
            frame_hora, values=horas, width=70,
            height=SIZES["input_height"], corner_radius=SIZES["input_corner_radius"],
            border_color=COLORS["border_medium"], state="readonly",
        )
        self._combo_hora.set("08")
        self._combo_hora.pack(side="left")

        ctk.CTkLabel(frame_hora, text=":", font=FONTS["body"],
                     text_color=COLORS["text_primary"]).pack(side="left", padx=6)

        self._combo_minuto = ctk.CTkComboBox(
            frame_hora, values=minutos, width=70,
            height=SIZES["input_height"], corner_radius=SIZES["input_corner_radius"],
            border_color=COLORS["border_medium"], state="readonly",
        )
        self._combo_minuto.set("00")
        self._combo_minuto.pack(side="left")

        # Preset
        ctk.CTkLabel(c, text="Filtros para execução automática",
                     font=FONTS["field_label"],
                     text_color=COLORS["text_secondary"], anchor="w").pack(fill="x")

        presets = FiltrosConsulta.listar_presets(PRESETS_DIR)
        opcoes_preset = ["(Filtros padrão)"] + [p["nome"] for p in presets]
        self._presets_lista = presets
        self._combo_preset = ctk.CTkComboBox(
            c, values=opcoes_preset,
            height=SIZES["input_height"], corner_radius=SIZES["input_corner_radius"],
            border_color=COLORS["border_medium"], state="readonly",
        )
        self._combo_preset.set(opcoes_preset[0])
        self._combo_preset.pack(fill="x", pady=(4, 12))

        # Nota informativa
        ctk.CTkLabel(
            c,
            text="O computador precisa estar ligado e desbloqueado no horário agendado.",
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
            anchor="w",
            wraplength=500,
        ).pack(fill="x")

        # ── Botões ────────────────────────────────────────────────────────
        frame_btns = ctk.CTkFrame(scroll, fg_color="transparent")
        frame_btns.pack(fill="x", pady=(0, 12))

        ctk.CTkButton(
            frame_btns, text="Salvar agendamento",
            height=SIZES["button_height"],
            corner_radius=SIZES["button_corner_radius"],
            fg_color=COLORS["primary_700"], hover_color=COLORS["primary_600"],
            text_color="white", font=FONTS["button"],
            command=self._agendar,
        ).pack(side="left")

        self._btn_remover = ctk.CTkButton(
            frame_btns, text="Remover agendamento",
            height=SIZES["button_height"],
            corner_radius=SIZES["button_corner_radius"],
            fg_color="transparent", border_width=1,
            border_color=COLORS["error"],
            text_color=COLORS["error"],
            hover_color=COLORS["error_bg"],
            font=FONTS["button"],
            command=self._remover,
        )

        # ── Status bar ────────────────────────────────────────────────────
        self._status_bar = StatusBar(scroll)
        self._status_bar.pack(fill="x", pady=(0, 12))

        # ── Status atual do agendamento ───────────────────────────────────
        self._card_status = ctk.CTkFrame(scroll, fg_color=COLORS["bg_input"],
                                          corner_radius=10, border_width=1,
                                          border_color=COLORS["border_light"])
        self._card_status.pack(fill="x")
        self._label_status_agenda = ctk.CTkLabel(
            self._card_status, text="",
            font=FONTS["body"], text_color=COLORS["text_muted"],
            anchor="w",
        )
        self._label_status_agenda.pack(padx=14, pady=10, anchor="w")

        self._verificar_agendamento()

    def _ao_mudar_frequencia(self, opcao: str):
        self._frame_semana.pack_forget()
        self._frame_mes.pack_forget()
        if opcao == "Semanal":
            self._frame_semana.pack(fill="x")
        elif opcao == "Mensal":
            self._frame_mes.pack(fill="x")

    def _verificar_agendamento(self):
        try:
            resultado = subprocess.run(
                ["schtasks", "/query", "/tn", "AgenteB3", "/fo", "LIST"],
                capture_output=True, text=True, encoding="cp1252"
            )
            ativo = resultado.returncode == 0 and "AgenteB3" in resultado.stdout
        except Exception:
            ativo = False

        if ativo:
            self._label_status_agenda.configure(
                text="Agendamento ativo: tarefa 'AgenteB3' encontrada no Agendador de Tarefas.",
                text_color=COLORS["success"],
            )
            self._card_status.configure(fg_color=COLORS["success_bg"])
            self._btn_remover.pack(side="left", padx=(12, 0))
        else:
            self._label_status_agenda.configure(
                text="Nenhum agendamento configurado.",
                text_color=COLORS["text_muted"],
            )
            self._card_status.configure(fg_color=COLORS["bg_input"])
            self._btn_remover.pack_forget()

    def _agendar(self):
        freq_map = {"Diário": "DAILY", "Semanal": "WEEKLY", "Mensal": "MONTHLY"}
        freq = freq_map.get(self._toggle_freq.get(), "DAILY")
        hora = self._combo_hora.get()
        minuto = self._combo_minuto.get()
        horario = f"{hora}:{minuto}"

        preset_nome = self._combo_preset.get()
        self._salvar_scheduler_config(preset_nome)

        import sys
        if getattr(sys, "frozen", False):
            exe = f'"{sys.executable}" --auto'
        else:
            launcher = PROJECT_ROOT / "launcher.py"
            exe = f'"{sys.executable}" "{launcher}" --auto'

        cmd = ["schtasks", "/create", "/tn", "AgenteB3", "/tr", exe,
               "/sc", freq, "/st", horario, "/f"]

        try:
            resultado = subprocess.run(cmd, capture_output=True, text=True, encoding="cp1252")
            if resultado.returncode == 0:
                self._status_bar.mostrar_sucesso(
                    f"Agendamento salvo! {self._toggle_freq.get()} às {horario}."
                )
                self._verificar_agendamento()
            else:
                raise RuntimeError(resultado.stderr or resultado.stdout)
        except Exception as e:
            self._status_bar.mostrar_erro(
                "Não foi possível criar o agendamento. Verifique as permissões de administrador."
            )

    def _remover(self):
        try:
            resultado = subprocess.run(
                ["schtasks", "/delete", "/tn", "AgenteB3", "/f"],
                capture_output=True, text=True, encoding="cp1252"
            )
            if resultado.returncode == 0:
                self._status_bar.mostrar_sucesso("Agendamento removido com sucesso.")
                self._verificar_agendamento()
            else:
                raise RuntimeError(resultado.stderr)
        except Exception:
            self._status_bar.mostrar_erro("Não foi possível remover o agendamento.")

    def _salvar_scheduler_config(self, preset_nome: str):
        config = {"preset_nome": preset_nome, "preset_path": ""}
        if preset_nome != "(Filtros padrão)":
            for p in self._presets_lista:
                if p["nome"] == preset_nome:
                    config["preset_path"] = p["arquivo"]
                    break
        config_path = PROJECT_ROOT / "scheduler_config.json"
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
